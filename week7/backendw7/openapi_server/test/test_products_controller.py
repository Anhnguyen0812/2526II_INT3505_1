import unittest

from flask import json

from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_create_request import ProductCreateRequest  # noqa: E501
from openapi_server.models.product_list_response import ProductListResponse  # noqa: E501
from openapi_server.models.product_update_request import ProductUpdateRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProductsController(BaseTestCase):
    """ProductsController integration test stubs"""

    def test_create_product(self):
        """Test case for create_product

        Create a product
        """
        product_create_request = {"price":0.08008282,"name":"name","description":"description","stock":0,"category":"category","isActive":True,"tags":["tags","tags","tags","tags","tags"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products',
            method='POST',
            headers=headers,
            data=json.dumps(product_create_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_product_by_id(self):
        """Test case for delete_product_by_id

        Delete product by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products/{product_id}'.format(product_id='product_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_product_by_id(self):
        """Test case for get_product_by_id

        Get product by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products/{product_id}'.format(product_id='product_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_products(self):
        """Test case for list_products

        List products
        """
        query_string = [('page', 1),
                        ('limit', 10),
                        ('search', 'search_example'),
                        ('category', 'category_example'),
                        ('minPrice', 3.4),
                        ('maxPrice', 3.4),
                        ('sortBy', createdAt),
                        ('sortOrder', desc)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_replace_product_by_id(self):
        """Test case for replace_product_by_id

        Replace product by ID
        """
        product_create_request = {"price":0.08008282,"name":"name","description":"description","stock":0,"category":"category","isActive":True,"tags":["tags","tags","tags","tags","tags"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products/{product_id}'.format(product_id='product_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(product_create_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_product_by_id(self):
        """Test case for update_product_by_id

        Update product by ID (partial)
        """
        product_update_request = {"price":0.08008282,"name":"name","description":"description","stock":0,"category":"category","isActive":True,"tags":["tags","tags","tags","tags","tags"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/products/{product_id}'.format(product_id='product_id_example'),
            method='PATCH',
            headers=headers,
            data=json.dumps(product_update_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
