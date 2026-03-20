import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.create_book_request import CreateBookRequest  # noqa: E501
from openapi_server.models.delete_response import DeleteResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.update_book_request import UpdateBookRequest  # noqa: E501
from openapi_server import util


def api_books_book_id_delete(book_id):  # noqa: E501
    """Xoa sach theo ID

     # noqa: E501

    :param book_id: ID cua sach
    :type book_id: int

    :rtype: Union[DeleteResponse, Tuple[DeleteResponse, int], Tuple[DeleteResponse, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_book_id_get(book_id):  # noqa: E501
    """Lay chi tiet sach theo ID

     # noqa: E501

    :param book_id: ID cua sach
    :type book_id: int

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_book_id_put(book_id, body):  # noqa: E501
    """Cap nhat thong tin sach

     # noqa: E501

    :param book_id: ID cua sach
    :type book_id: int
    :param update_book_request: 
    :type update_book_request: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    update_book_request = body
    if connexion.request.is_json:
        update_book_request = UpdateBookRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def api_books_get(q=None):  # noqa: E501
    """Lay danh sach sach

    Co ho tro tim kiem theo ten hoac tac gia qua query &#x60;q&#x60;. # noqa: E501

    :param q: Tu khoa tim trong title hoac author
    :type q: str

    :rtype: Union[List[Book], Tuple[List[Book], int], Tuple[List[Book], int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_post(body):  # noqa: E501
    """Tao sach moi

     # noqa: E501

    :param create_book_request: 
    :type create_book_request: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    create_book_request = body
    if connexion.request.is_json:
        create_book_request = CreateBookRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
