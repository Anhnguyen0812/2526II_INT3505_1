import logging
import os
import time
import uuid
from functools import wraps

from flask import Flask, Response, jsonify, request, has_request_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger, swag_from
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

load_dotenv()

APP_NAME = "week10-service"
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Week10 Service",
    "uiversion": 3,
}

Swagger(app)
# Flasgger spec for POST /items to avoid YAML indentation issues.
CREATE_ITEM_SPEC = {
    "parameters": [
        {
            "in": "header",
            "name": "X-API-Key",
            "required": False,
            "schema": {"type": "string"},
        },
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            },
        },
    ],
    "responses": {
        201: {"description": "Created"},
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
    },
}

# Basic logging for audit and ops visibility.
_base_factory = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs):
    record = _base_factory(*args, **kwargs)
    if not hasattr(record, "request_id"):
        record.request_id = "-"
    if not hasattr(record, "trace_id"):
        record.trace_id = "-"
    if not hasattr(record, "span_id"):
        record.span_id = "-"
    return record


logging.setLogRecordFactory(_record_factory)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format=(
        "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s "
        "trace_id=%(trace_id)s span_id=%(span_id)s %(message)s"
    ),
)
logger = logging.getLogger(APP_NAME)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if has_request_context() and hasattr(request, "request_id"):
            record.request_id = request.request_id
        elif not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "trace_id") or not hasattr(record, "span_id"):
            span = trace.get_current_span()
            span_context = span.get_span_context()
            if span_context and span_context.is_valid:
                record.trace_id = format(span_context.trace_id, "032x")
                record.span_id = format(span_context.span_id, "016x")
            else:
                record.trace_id = "-"
                record.span_id = "-"
        return True


logger.addFilter(RequestIdFilter())

# Prometheus metrics.
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
AUTH_FAILURES = Counter(
    "auth_failures_total",
    "Total authentication failures",
    ["path"],
)
RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Total rate limit violations",
    ["path"],
)

# Rate limiting.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
)
limiter.init_app(app)


def setup_tracing() -> None:
    if os.getenv("ENABLE_TRACING", "false").lower() not in {"1", "true", "yes", "on"}:
        return
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", APP_NAME)})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    FlaskInstrumentor().instrument_app(app)


@app.before_request
def attach_request_id() -> None:
    request.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    request.start_time = time.time()


@app.after_request
def record_metrics(response: Response) -> Response:
    elapsed = time.time() - getattr(request, "start_time", time.time())
    path = request.path
    REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "-")
    logger.info(
        "request completed method=%s path=%s status=%s latency=%.4f ip=%s ua=%s",
        request.method,
        path,
        response.status_code,
        elapsed,
        client_ip,
        user_agent,
    )
    span = trace.get_current_span()
    span_context = span.get_span_context()
    if span_context and span_context.is_valid:
        response.headers["X-Trace-Id"] = format(span_context.trace_id, "032x")
    response.headers["X-Request-Id"] = request.request_id
    return response


def require_api_key(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not API_KEY:
            return handler(*args, **kwargs)
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            AUTH_FAILURES.labels(request.path).inc()
            logger.warning("auth failed")
            return jsonify({"error": "unauthorized"}), 401
        return handler(*args, **kwargs)

    return wrapper


@app.get("/health")
@limiter.limit("120 per minute")
def health() -> Response:
    """
    Health check endpoint.
    ---
    responses:
      200:
        description: OK
    """
    return jsonify({"status": "ok", "service": APP_NAME})


@app.get("/items")
@limiter.limit("10 per minute")
def list_items() -> Response:
    """
    List demo items.
    ---
    responses:
      200:
        description: OK
    """
    items = [
        {"id": 1, "name": "alpha"},
        {"id": 2, "name": "beta"},
    ]
    return jsonify({"items": items})


@app.post("/items")
@limiter.limit("5 per minute")
@require_api_key
@swag_from(CREATE_ITEM_SPEC)
def create_item() -> Response:
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
                return jsonify({"error": "name is required"}), 400
        item = {"id": int(time.time()), "name": name.strip()}
        return jsonify(item), 201


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.errorhandler(429)
def rate_limit_handler(error: Exception) -> Response:
    RATE_LIMIT_HITS.labels(request.path).inc()
    logger.warning("rate limit exceeded")
    return jsonify({"error": "rate limit exceeded"}), 429


@app.errorhandler(400)
def bad_request_handler(error: Exception) -> Response:
    return jsonify({"error": "bad request"}), 400


@app.errorhandler(401)
def unauthorized_handler(error: Exception) -> Response:
    return jsonify({"error": "unauthorized"}), 401


if __name__ == "__main__":
    setup_tracing()
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
