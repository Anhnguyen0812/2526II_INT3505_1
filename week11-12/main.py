import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List

import requests
from flask import Flask, Response, jsonify, request
from flasgger import Swagger

APP_NAME = "week11-12-api-design"
WEBHOOK_SHARED_SECRET = os.getenv("WEBHOOK_SHARED_SECRET", "demo-secret")

app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Week11-12 API Design Patterns",
    "uiversion": 3,
}
Swagger(app)

ARTICLES: Dict[int, Dict[str, str]] = {}
SUBSCRIPTIONS: Dict[str, Dict[str, object]] = {}
SEEN_EVENT_IDS: List[str] = []
NEXT_ARTICLE_ID = 1

SUPPORTED_EVENTS = {
    "article.created",
    "article.updated",
    "article.deleted",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_article_links(article_id: int) -> Dict[str, str]:
    base = request.host_url.rstrip("/")
    return {
        "self": f"{base}/articles/{article_id}",
        "update": f"{base}/articles/{article_id}",
        "delete": f"{base}/articles/{article_id}",
        "list": f"{base}/articles",
        "subscriptions": f"{base}/webhooks/subscriptions",
    }


def add_seen_event(event_id: str) -> None:
    SEEN_EVENT_IDS.append(event_id)
    if len(SEEN_EVENT_IDS) > 1000:
        SEEN_EVENT_IDS.pop(0)


def sign_payload(secret: str, body: bytes, timestamp: str) -> str:
    message = timestamp.encode("utf-8") + b"." + body
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def send_webhook(event_type: str, payload: Dict[str, object]) -> None:
    event_id = str(uuid.uuid4())
    payload_with_meta = {
        "id": event_id,
        "type": event_type,
        "created_at": now_iso(),
        "data": payload,
    }
    body = json.dumps(payload_with_meta).encode("utf-8")

    for sub in SUBSCRIPTIONS.values():
        if event_type not in sub["events"]:
            continue
        timestamp = str(int(time.time()))
        signature = sign_payload(sub["secret"], body, timestamp)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Id": event_id,
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Signature": signature,
        }
        for attempt in range(1, 4):
            try:
                resp = requests.post(sub["url"], data=body, headers=headers, timeout=3)
                if 200 <= resp.status_code < 300:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.5 * attempt)


@app.get("/health")
def health() -> Response:
    """
    Health check.
    ---
    responses:
      200:
        description: OK
    """
    return jsonify({"status": "ok", "service": APP_NAME})


@app.get("/articles")
def list_articles() -> Response:
    """
    List articles with query pattern.
    ---
    parameters:
      - in: query
        name: q
        schema:
          type: string
      - in: query
        name: status
        schema:
          type: string
          enum: [draft, published]
      - in: query
        name: page
        schema:
          type: integer
      - in: query
        name: limit
        schema:
          type: integer
    responses:
      200:
        description: OK
    """
    q = (request.args.get("q") or "").lower()
    status = request.args.get("status")
    page = max(int(request.args.get("page", 1)), 1)
    limit = min(max(int(request.args.get("limit", 10)), 1), 50)

    items = list(ARTICLES.values())
    if q:
        items = [item for item in items if q in item["title"].lower()]
    if status:
        items = [item for item in items if item["status"] == status]

    start = (page - 1) * limit
    end = start + limit
    paged = items[start:end]

    base = request.host_url.rstrip("/")
    links = {"self": f"{base}/articles?page={page}&limit={limit}"}
    if end < len(items):
        links["next"] = f"{base}/articles?page={page + 1}&limit={limit}"
    if page > 1:
        links["prev"] = f"{base}/articles?page={page - 1}&limit={limit}"

    return jsonify({
        "items": [
            {**item, "links": make_article_links(item["id"])} for item in paged
        ],
        "count": len(items),
        "links": links,
    })


@app.post("/articles")
def create_article() -> Response:
    """
    Create article (CRUD pattern).
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [title, status]
          properties:
            title:
              type: string
            status:
              type: string
              enum: [draft, published]
            content:
              type: string
    responses:
      201:
        description: Created
    """
    global NEXT_ARTICLE_ID
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    status = payload.get("status")
    content = payload.get("content", "")
    if not isinstance(title, str) or not isinstance(status, str):
        return jsonify({"error": "title and status are required"}), 400

    article = {
        "id": NEXT_ARTICLE_ID,
        "title": title.strip(),
        "status": status,
        "content": content,
        "created_at": now_iso(),
    }
    ARTICLES[NEXT_ARTICLE_ID] = article
    NEXT_ARTICLE_ID += 1

    send_webhook("article.created", article)
    return jsonify({**article, "links": make_article_links(article["id"])}), 201


@app.get("/articles/<int:article_id>")
def get_article(article_id: int) -> Response:
    """
    Get article by id (CRUD).
    ---
    responses:
      200:
        description: OK
      404:
        description: Not Found
    """
    article = ARTICLES.get(article_id)
    if not article:
        return jsonify({"error": "not found"}), 404
    return jsonify({**article, "links": make_article_links(article_id)})


@app.put("/articles/<int:article_id>")
def update_article(article_id: int) -> Response:
    """
    Update article by id (CRUD).
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            status:
              type: string
              enum: [draft, published]
            content:
              type: string
    responses:
      200:
        description: OK
    """
    payload = request.get_json(silent=True) or {}
    article = ARTICLES.get(article_id)
    if not article:
        return jsonify({"error": "not found"}), 404

    if "title" in payload:
        article["title"] = str(payload["title"]).strip()
    if "status" in payload:
        article["status"] = str(payload["status"]).strip()
    if "content" in payload:
        article["content"] = str(payload["content"])

    send_webhook("article.updated", article)
    return jsonify({**article, "links": make_article_links(article_id)})


@app.delete("/articles/<int:article_id>")
def delete_article(article_id: int) -> Response:
    """
    Delete article by id (CRUD).
    ---
    responses:
      200:
        description: OK
    """
    article = ARTICLES.pop(article_id, None)
    if not article:
        return jsonify({"error": "not found"}), 404
    send_webhook("article.deleted", {"id": article_id})
    return jsonify({"status": "deleted", "id": article_id})


@app.post("/webhooks/subscriptions")
def create_subscription() -> Response:
    """
    Register webhook subscription.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [url]
          properties:
            url:
              type: string
            events:
              type: array
              items:
                type: string
    responses:
      201:
        description: Created
    """
    payload = request.get_json(silent=True) or {}
    url = payload.get("url")
    events = payload.get("events") or list(SUPPORTED_EVENTS)

    if not isinstance(url, str) or not url.startswith("http"):
        return jsonify({"error": "url is required"}), 400

    for event in events:
        if event not in SUPPORTED_EVENTS:
            return jsonify({"error": f"unsupported event {event}"}), 400

    sub_id = str(uuid.uuid4())
    sub = {
        "id": sub_id,
        "url": url,
        "events": events,
        "secret": uuid.uuid4().hex,
        "created_at": now_iso(),
    }
    SUBSCRIPTIONS[sub_id] = sub
    return jsonify(sub), 201


@app.get("/webhooks/subscriptions")
def list_subscriptions() -> Response:
    """
    List webhook subscriptions.
    ---
    responses:
      200:
        description: OK
    """
    return jsonify({"items": list(SUBSCRIPTIONS.values())})


@app.delete("/webhooks/subscriptions/<sub_id>")
def delete_subscription(sub_id: str) -> Response:
    """
    Delete webhook subscription.
    ---
    responses:
      200:
        description: OK
    """
    sub = SUBSCRIPTIONS.pop(sub_id, None)
    if not sub:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted", "id": sub_id})


@app.post("/webhooks/receiver")
def webhook_receiver() -> Response:
    """
    Webhook receiver demo.
    ---
    responses:
      200:
        description: OK
    """
    raw_body = request.get_data() or b""
    event_id = request.headers.get("X-Webhook-Id", "")
    timestamp = request.headers.get("X-Webhook-Timestamp", "")
    signature = request.headers.get("X-Webhook-Signature", "")

    expected = sign_payload(WEBHOOK_SHARED_SECRET, raw_body, timestamp)
    if not hmac.compare_digest(signature, expected):
        return jsonify({"error": "invalid signature"}), 400

    if event_id in SEEN_EVENT_IDS:
        return jsonify({"status": "duplicate"}), 200

    add_seen_event(event_id)
    payload = request.get_json(silent=True) or {}
    return jsonify({"status": "received", "event": payload})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
