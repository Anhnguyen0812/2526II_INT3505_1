import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_create_request import ProductCreateRequest  # noqa: E501
from openapi_server.models.product_list_response import ProductListResponse  # noqa: E501
from openapi_server.models.product_list_response_pagination import ProductListResponsePagination  # noqa: E501
from openapi_server.models.product_update_request import ProductUpdateRequest  # noqa: E501
from openapi_server.api import mongodb
from openapi_server import util


def _bad_request(message, details=None):
    return ErrorResponse(message=message, code="BAD_REQUEST", details=details), 400


def _not_found(message="Product not found"):
    return ErrorResponse(message=message, code="NOT_FOUND"), 404


def _internal_error(err):
    return ErrorResponse(message=str(err), code="INTERNAL_ERROR"), 500


def _coerce_body(payload):
    if payload is None:
        return {}
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    if isinstance(payload, dict):
        return payload
    return {}


def _to_product_model(data):
    return Product.from_dict(data)


def create_product(body):  # noqa: E501
    """Create a product

     # noqa: E501

    :param product_create_request: 
    :type product_create_request: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    product_create_request = body
    if connexion.request.is_json:
        product_create_request = ProductCreateRequest.from_dict(connexion.request.get_json())  # noqa: E501

    payload = _coerce_body(product_create_request)

    try:
        created = mongodb.create_product(payload)
        return _to_product_model(created), 201
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("Create product failed", {"error": str(err)})


def delete_product_by_id(product_id):  # noqa: E501
    """Delete product by ID

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        deleted = mongodb.delete_product_by_id(product_id)
        if not deleted:
            return _not_found()
        return None, 204
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("Delete product failed", {"error": str(err)})


def get_product_by_id(product_id):  # noqa: E501
    """Get product by ID

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    try:
        product = mongodb.get_product_by_id(product_id)
        if not product:
            return _not_found()
        return _to_product_model(product), 200
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("Get product failed", {"error": str(err)})


def list_products(page=None, limit=None, search=None, category=None, min_price=None, max_price=None, sort_by=None, sort_order=None):  # noqa: E501
    """List products

     # noqa: E501

    :param page: Page number
    :type page: int
    :param limit: Number of items per page
    :type limit: int
    :param search: Search by product name (contains)
    :type search: str
    :param category: Filter by category
    :type category: str
    :param min_price: Minimum product price
    :type min_price: float
    :param max_price: Maximum product price
    :type max_price: float
    :param sort_by: Field to sort by
    :type sort_by: str
    :param sort_order: Sort direction
    :type sort_order: str

    :rtype: Union[ProductListResponse, Tuple[ProductListResponse, int], Tuple[ProductListResponse, int, Dict[str, str]]
    """
    page = page or 1
    limit = limit or 10
    sort_by = sort_by or "createdAt"
    sort_order = sort_order or "desc"

    valid_sort = {
        "name": "name",
        "price": "price",
        "stock": "stock",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
    }
    if sort_by not in valid_sort:
        return _bad_request("Invalid sortBy", {"sortBy": sort_by})
    if sort_order not in {"asc", "desc"}:
        return _bad_request("Invalid sortOrder", {"sortOrder": sort_order})

    try:
        rows, pagination = mongodb.list_products(
            page=page,
            limit=limit,
            search=search,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=valid_sort[sort_by],
            sort_order=sort_order,
        )
        data = [_to_product_model(row) for row in rows]
        paging = ProductListResponsePagination.from_dict(pagination)
        return ProductListResponse(data=data, pagination=paging), 200
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("List products failed", {"error": str(err)})


def replace_product_by_id(product_id, body):  # noqa: E501
    """Replace product by ID

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str
    :param product_create_request: 
    :type product_create_request: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    product_create_request = body
    if connexion.request.is_json:
        product_create_request = ProductCreateRequest.from_dict(connexion.request.get_json())  # noqa: E501

    payload = _coerce_body(product_create_request)

    try:
        product = mongodb.replace_product_by_id(product_id, payload)
        if not product:
            return _not_found()
        return _to_product_model(product), 200
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("Replace product failed", {"error": str(err)})


def update_product_by_id(product_id, body):  # noqa: E501
    """Update product by ID (partial)

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str
    :param product_update_request: 
    :type product_update_request: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    product_update_request = body
    if connexion.request.is_json:
        product_update_request = ProductUpdateRequest.from_dict(connexion.request.get_json())  # noqa: E501

    payload = _coerce_body(product_update_request)

    try:
        product = mongodb.update_product_by_id(product_id, payload)
        if not product:
            return _not_found()
        return _to_product_model(product), 200
    except RuntimeError as err:
        return _internal_error(err)
    except Exception as err:
        return _bad_request("Update product failed", {"error": str(err)})
