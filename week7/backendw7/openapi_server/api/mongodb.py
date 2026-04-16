import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

TABLE_NAME = "products"

_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[Database] = None
_mongo_collection: Optional[Collection] = None


def _get_collection() -> Collection:
    global _mongo_client, _mongo_db, _mongo_collection
    if _mongo_collection is not None:
        return _mongo_collection

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "product_api")
    if not db_name:
        raise RuntimeError("Missing MONGODB_DB environment variable")

    try:
        _mongo_client = MongoClient(uri)
        _mongo_db = _mongo_client[db_name]
        _mongo_collection = _mongo_db[TABLE_NAME]
        _mongo_collection.create_index("name")
        _mongo_collection.create_index("category")
        _mongo_collection.create_index("price")
        _mongo_collection.create_index("created_at")
    except PyMongoError as err:
        raise RuntimeError(f"MongoDB connection failed: {err}")

    return _mongo_collection


def _parse_object_id(product_id: str) -> Optional[ObjectId]:
    if not ObjectId.is_valid(product_id):
        return None
    return ObjectId(product_id)


def _serialize_datetime(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_id": str(row.get("_id")) if row.get("_id") is not None else None,
        "name": row.get("name"),
        "description": row.get("description"),
        "price": row.get("price"),
        "stock": row.get("stock"),
        "category": row.get("category"),
        "isActive": row.get("is_active", True),
        "tags": row.get("tags") or [],
        "createdAt": _serialize_datetime(row.get("created_at")),
        "updatedAt": _serialize_datetime(row.get("updated_at")),
    }


def _build_payload(data: Dict[str, Any], include_all_fields: bool = False) -> Dict[str, Any]:
    is_active = data.get("isActive")
    if is_active is None:
        is_active = data.get("is_active")

    tags = data.get("tags")
    if tags is None:
        tags = data.get("product_tags")

    payload = {
        "name": data.get("name"),
        "description": data.get("description"),
        "price": data.get("price"),
        "stock": data.get("stock"),
        "category": data.get("category"),
        "is_active": is_active,
        "tags": tags,
    }
    if include_all_fields:
        return payload
    return {k: v for k, v in payload.items() if v is not None}


def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
    payload = _build_payload(data, include_all_fields=False)
    if payload.get("is_active") is None:
        payload["is_active"] = True
    if payload.get("tags") is None:
        payload["tags"] = []

    now = datetime.utcnow()
    payload["created_at"] = now
    payload["updated_at"] = now

    result = _get_collection().insert_one(payload)
    created = _get_collection().find_one({"_id": result.inserted_id})
    if not created:
        raise RuntimeError("Create product failed")
    return _normalize_row(created)


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    oid = _parse_object_id(product_id)
    if oid is None:
        return None

    row = _get_collection().find_one({"_id": oid})
    if not row:
        return None
    return _normalize_row(row)


def delete_product_by_id(product_id: str) -> bool:
    oid = _parse_object_id(product_id)
    if oid is None:
        return False

    result = _get_collection().delete_one({"_id": oid})
    return result.deleted_count > 0


def replace_product_by_id(product_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    oid = _parse_object_id(product_id)
    if oid is None:
        return None

    payload = _build_payload(data, include_all_fields=True)
    payload["is_active"] = payload.get("is_active", True)
    payload["tags"] = payload.get("tags") or []

    existing = _get_collection().find_one({"_id": oid})
    if not existing:
        return None

    payload["created_at"] = existing.get("created_at")
    payload["updated_at"] = datetime.utcnow()

    _get_collection().replace_one({"_id": oid}, payload)
    updated = _get_collection().find_one({"_id": oid})
    if not updated:
        return None
    return _normalize_row(updated)


def update_product_by_id(product_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    oid = _parse_object_id(product_id)
    if oid is None:
        return None

    payload = _build_payload(data, include_all_fields=False)
    if not payload:
        return get_product_by_id(product_id)

    payload["updated_at"] = datetime.utcnow()
    result = _get_collection().find_one_and_update(
        {"_id": oid},
        {"$set": payload},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        return None
    return _normalize_row(result)


def list_products(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    start = (page - 1) * limit
    filters: Dict[str, Any] = {}

    if search:
        filters["name"] = {"$regex": search, "$options": "i"}
    if category:
        filters["category"] = category
    if min_price is not None or max_price is not None:
        filters["price"] = {}
        if min_price is not None:
            filters["price"]["$gte"] = min_price
        if max_price is not None:
            filters["price"]["$lte"] = max_price

    sort_direction = DESCENDING if sort_order == "desc" else ASCENDING

    collection = _get_collection()
    cursor = (
        collection.find(filters)
        .sort(sort_by, sort_direction)
        .skip(start)
        .limit(limit)
    )

    total_items = collection.count_documents(filters)
    total_pages = math.ceil(total_items / limit) if total_items else 0

    items = [_normalize_row(item) for item in cursor]
    pagination = {
        "page": page,
        "limit": limit,
        "totalItems": total_items,
        "totalPages": total_pages,
    }
    return items, pagination