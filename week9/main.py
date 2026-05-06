from datetime import datetime, timezone
from email.utils import format_datetime

from flask import Flask, jsonify, request
from flasgger import Swagger


app = Flask(__name__)

app.config["SWAGGER"] = {
    "title": "API Versioning and Lifecycle Management Lab",
    "uiversion": 3,
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Versioning and Lifecycle Management Lab",
        "description": (
            "A teaching API that demonstrates URL versioning, header versioning, "
            "query parameter versioning, deprecation, and migration planning."
        ),
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
}

Swagger(app, template=swagger_template)

SUPPORTED_VERSIONS = ["v1", "v2"]
SUNSET_DATE = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

payments_store = []
payment_sequence = 1


def next_payment_id():
    global payment_sequence
    payment_id = f"pay_{payment_sequence:04d}"
    payment_sequence += 1
    return payment_id


def to_http_date(value):
    return format_datetime(value, usegmt=True)


def deprecation_headers():
    return {
        "Deprecation": "true",
        "Sunset": to_http_date(SUNSET_DATE),
        "Link": '<http://localhost:5000/api/lifecycle/migration-plan>; rel="deprecation"',
        "Warning": '299 - "API v1 is deprecated and will be removed after the sunset date"',
    }


def canonical_payment(record):
    return {
        "id": record["id"],
        "amount_minor": record["amount_minor"],
        "currency": record["currency"],
        "payment_method": record["payment_method"],
        "customer_reference": record.get("customer_reference"),
        "status": record["status"],
        "created_at": record["created_at"],
    }


def payment_v1_view(record):
    return {
        "id": record["id"],
        "amount": round(record["amount_minor"] / 100, 2),
        "currency": record["currency"],
        "source": record["payment_method"],
        "customer_reference": record.get("customer_reference"),
        "status": record["status"],
        "created_at": record["created_at"],
    }


def payment_v2_view(record):
    return canonical_payment(record)


def json_error(message, status_code, extra=None):
    payload = {"error": message, "status": status_code}
    if extra:
        payload.update(extra)
    return jsonify(payload), status_code


def create_payment_from_v1(payload):
    required_fields = ["amount", "currency", "source"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return None, (json_error("Missing required fields for v1", 400, {"missing_fields": missing}))

    try:
        amount = float(payload["amount"])
    except (TypeError, ValueError):
        return None, json_error("amount must be numeric in v1", 400)

    if amount <= 0:
        return None, json_error("amount must be greater than 0", 400)

    record = {
        "id": next_payment_id(),
        "amount_minor": int(round(amount * 100)),
        "currency": str(payload["currency"]).upper(),
        "payment_method": str(payload["source"]),
        "customer_reference": payload.get("customer_reference"),
        "status": "authorized",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    payments_store.append(record)
    return record, None


def create_payment_from_v2(payload):
    required_fields = ["amount_minor", "currency", "payment_method"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return None, (json_error("Missing required fields for v2", 400, {"missing_fields": missing}))

    try:
        amount_minor = int(payload["amount_minor"])
    except (TypeError, ValueError):
        return None, json_error("amount_minor must be an integer in v2", 400)

    if amount_minor <= 0:
        return None, json_error("amount_minor must be greater than 0", 400)

    record = {
        "id": next_payment_id(),
        "amount_minor": amount_minor,
        "currency": str(payload["currency"]).upper(),
        "payment_method": str(payload["payment_method"]),
        "customer_reference": payload.get("customer_reference"),
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    payments_store.append(record)
    return record, None


def find_payment(payment_id):
    return next((payment for payment in payments_store if payment["id"] == payment_id), None)


def version_from_request(default="v2"):
    header_version = request.headers.get("X-API-Version")
    query_version = request.args.get("version")
    value = header_version or query_version or default
    value = value.lower().replace("/", "")
    if value in {"1", "v1"}:
        return "v1"
    if value in {"2", "v2"}:
        return "v2"
    return None


def versioned_list_response(version):
    if version == "v1":
        return jsonify({"version": "v1", "data": [payment_v1_view(payment) for payment in payments_store]}), 200, deprecation_headers()
    return jsonify({"version": "v2", "data": [payment_v2_view(payment) for payment in payments_store]}), 200


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    ---
    tags:
      - System
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({"status": "healthy", "service": "api-versioning-lab"}), 200


@app.route("/api/versions", methods=["GET"])
def versions():
    """
    List supported API versions and versioning strategies.
    ---
    tags:
      - Lifecycle
    responses:
      200:
        description: Supported versions
    """
    return jsonify(
        {
            "supported_versions": SUPPORTED_VERSIONS,
            "strategies": ["url", "header", "query_param"],
            "default_version": "v2",
            "deprecated_versions": ["v1"],
        }
    ), 200


@app.route("/api/v1/payments", methods=["GET"])
def list_payments_v1():
    """
    List payments using URL versioning for v1.
    ---
    tags:
      - Payments v1
    responses:
      200:
        description: V1 payment list
    """
    response, status_code, headers = versioned_list_response("v1")
    return response, status_code, headers


@app.route("/api/v1/payments", methods=["POST"])
def create_payment_v1():
    """
    Create a payment using the v1 contract.
    ---
    tags:
      - Payments v1
    parameters:
      - in: body
        name: payload
        required: true
        schema:
          type: object
          required:
            - amount
            - currency
            - source
          properties:
            amount:
              type: number
              example: 49.99
            currency:
              type: string
              example: USD
            source:
              type: string
              example: card
            customer_reference:
              type: string
              example: ORD-10001
    responses:
      201:
        description: Payment created
      400:
        description: Invalid request payload
    """
    payload = request.get_json(silent=True) or {}
    record, error_response = create_payment_from_v1(payload)
    if error_response:
        return error_response
    return jsonify({"version": "v1", "payment": payment_v1_view(record)}), 201, deprecation_headers()


@app.route("/api/v1/payments/<payment_id>", methods=["GET"])
def get_payment_v1(payment_id):
    """
    Get a single payment using the v1 contract.
    ---
    tags:
      - Payments v1
    responses:
      200:
        description: Payment found
      404:
        description: Payment not found
    """
    payment = find_payment(payment_id)
    if not payment:
        return json_error("Payment not found", 404)
    return jsonify({"version": "v1", "payment": payment_v1_view(payment)}), 200, deprecation_headers()


@app.route("/api/v2/payments", methods=["GET"])
def list_payments_v2():
    """
    List payments using URL versioning for v2.
    ---
    tags:
      - Payments v2
    responses:
      200:
        description: V2 payment list
    """
    response, status_code, headers = versioned_list_response("v2")
    return response, status_code, headers


@app.route("/api/v2/payments", methods=["POST"])
def create_payment_v2():
    """
    Create a payment using the v2 contract.
    ---
    tags:
      - Payments v2
    parameters:
      - in: body
        name: payload
        required: true
        schema:
          type: object
          required:
            - amount_minor
            - currency
            - payment_method
          properties:
            amount_minor:
              type: integer
              example: 4999
            currency:
              type: string
              example: USD
            payment_method:
              type: string
              example: card
            customer_reference:
              type: string
              example: ORD-10001
    responses:
      201:
        description: Payment created
      400:
        description: Invalid request payload
    """
    payload = request.get_json(silent=True) or {}
    record, error_response = create_payment_from_v2(payload)
    if error_response:
        return error_response
    return jsonify({"version": "v2", "payment": payment_v2_view(record)}), 201


@app.route("/api/v2/payments/<payment_id>", methods=["GET"])
def get_payment_v2(payment_id):
    """
    Get a single payment using the v2 contract.
    ---
    tags:
      - Payments v2
    responses:
      200:
        description: Payment found
      404:
        description: Payment not found
    """
    payment = find_payment(payment_id)
    if not payment:
        return json_error("Payment not found", 404)
    return jsonify({"version": "v2", "payment": payment_v2_view(payment)}), 200


@app.route("/api/payments", methods=["GET"])
def payments_by_header_or_query():
    """
    Resolve the API version from header or query parameter.
    ---
    tags:
      - Version Negotiation
    parameters:
      - in: header
        name: X-API-Version
        required: false
        type: string
        description: Set to v1 or v2
      - in: query
        name: version
        required: false
        type: string
        description: Set to v1 or v2
    responses:
      200:
        description: Versioned payment list
      400:
        description: Unknown version requested
    """
    version = version_from_request()
    if not version:
        return json_error("Unsupported version. Use v1 or v2.", 400)
    return versioned_list_response(version)


@app.route("/api/lifecycle/deprecation-notice", methods=["GET"])
def deprecation_notice():
    """
    Sample deprecation notice for developers.
    ---
    tags:
      - Lifecycle
    responses:
      200:
        description: Deprecation notice
    """
    return jsonify(
        {
            "title": "Deprecation notice for v1 payments API",
            "summary": "API v1 is deprecated and will be removed after the sunset date.",
            "sunset": to_http_date(SUNSET_DATE),
            "recommended_action": "Migrate to /api/v2/payments before the sunset date.",
            "developer_message": (
                "Please update integrations to use amount_minor and payment_method. "
                "v1 responses will continue to work until the sunset date, but new features only land in v2."
            ),
        }
    ), 200


@app.route("/api/lifecycle/migration-plan", methods=["GET"])
def migration_plan():
    """
    Migration plan from v1 to v2.
    ---
    tags:
      - Lifecycle
    responses:
      200:
        description: Migration plan
    """
    return jsonify(
        {
            "goal": "Upgrade payment integrations from v1 to v2 with minimal downtime.",
            "phases": [
                {
                    "phase": "1. Audit",
                    "activities": [
                        "Inventory all clients using /api/v1/payments.",
                        "Log response shapes and payload assumptions.",
                    ],
                },
                {
                    "phase": "2. Dual run",
                    "activities": [
                        "Expose /api/v2/payments in parallel with v1.",
                        "Add compatibility tests and contract tests.",
                    ],
                },
                {
                    "phase": "3. Cutover",
                    "activities": [
                        "Switch new clients to v2 by default.",
                        "Keep v1 only for existing consumers during the grace period.",
                    ],
                },
                {
                    "phase": "4. Sunset",
                    "activities": [
                        "Send deprecation reminders.",
                        "Remove v1 after the announced sunset date.",
                    ],
                },
            ],
        }
    ), 200


@app.route("/api/lifecycle/case-study/payment-upgrade", methods=["GET"])
def payment_case_study():
    """
    Case study: upgrade a payment API from v1 to v2.
    ---
    tags:
      - Lifecycle
    responses:
      200:
        description: Payment API case study
    """
    return jsonify(
        {
            "business_problem": "The payment API must support more accurate money handling and richer metadata.",
            "breaking_changes": [
                "amount changed from decimal dollars to amount_minor integer cents.",
                "source renamed to payment_method.",
                "status values changed from authorized to confirmed in the new flow.",
            ],
            "compatibility_strategy": [
                "Keep v1 alive as a deprecated URL version.",
                "Allow header-based and query-based version negotiation for controlled rollouts.",
                "Return deprecation and sunset headers from v1.",
            ],
            "success_metrics": [
                "80 percent of traffic moved to v2 before sunset.",
                "Zero critical integration incidents during migration.",
            ],
        }
    ), 200


@app.route("/api/lifecycle/deprecation-message", methods=["GET"])
def deprecation_message():
    """
    Ready-to-send deprecation message for developers.
    ---
    tags:
      - Lifecycle
    responses:
      200:
        description: Deprecation message
    """
    return jsonify(
        {
            "subject": "Action required: migrate payment integrations from v1 to v2",
            "message": (
                "We are deprecating /api/v1/payments. The endpoint will remain available until the sunset date, "
                "after which it will be removed. Please migrate to /api/v2/payments and update your payload to use "
                "amount_minor, currency, and payment_method. Full migration steps are documented in /api/lifecycle/migration-plan."
            ),
            "timeline": {
                "notice_sent": "now",
                "grace_period": "until 2026-12-31T23:59:59Z",
                "shutdown": "after the sunset date",
            },
        }
    ), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "message": "API Versioning and Lifecycle Management Lab",
            "swagger_docs": "/apidocs/",
            "endpoints": [
                "/api/v1/payments",
                "/api/v2/payments",
                "/api/payments?version=v1|v2",
                "/api/lifecycle/migration-plan",
            ],
        }
    ), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)