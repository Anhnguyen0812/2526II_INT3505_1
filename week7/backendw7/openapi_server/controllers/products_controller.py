import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_create_request import ProductCreateRequest  # noqa: E501
from openapi_server.models.product_list_response import ProductListResponse  # noqa: E501
from openapi_server.models.product_update_request import ProductUpdateRequest  # noqa: E501
from openapi_server import util


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
    return 'do some magic!'


def delete_product_by_id(product_id):  # noqa: E501
    """Delete product by ID

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_product_by_id(product_id):  # noqa: E501
    """Get product by ID

     # noqa: E501

    :param product_id: MongoDB ObjectId of the product
    :type product_id: str

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    return 'do some magic!'


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
    return 'do some magic!'


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
    return 'do some magic!'


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
    return 'do some magic!'
