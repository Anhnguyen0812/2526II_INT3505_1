import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.create_book_request import CreateBookRequest  # noqa: E501
from openapi_server.models.delete_response import DeleteResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.update_book_request import UpdateBookRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_api_books_book_id_delete(self):
        """Test case for api_books_book_id_delete

        Xoa sach theo ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_get(self):
        """Test case for api_books_book_id_get

        Lay chi tiet sach theo ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_put(self):
        """Test case for api_books_book_id_put

        Cap nhat thong tin sach
        """
        update_book_request = {"published_year":0,"author":"author","title":"title"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(update_book_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_get(self):
        """Test case for api_books_get

        Lay danh sach sach
        """
        query_string = [('q', 'q_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_post(self):
        """Test case for api_books_post

        Tao sach moi
        """
        create_book_request = {"published_year":0,"author":"author","title":"title"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/books',
            method='POST',
            headers=headers,
            data=json.dumps(create_book_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
