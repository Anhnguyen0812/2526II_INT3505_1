from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)

swagger = Swagger(app, template={
    "info": {
        "title": "My API",
        "description": "API Documentation",
        "version": "1.0.1"
    }
})

# Mock data
users = [
    {"id": 1, "username": "anhnguyen", "email": "anh@example.com"},
    {"id": 2, "username": "anhnguyen1", "email": "anhnp@example.com"}
]

products = [
    {
        "id": 101,
        "name": "Laptop Dell XPS",
        "price": 1200,
        "category": "electronics",
        "stock": 15,
        "rating": 4.7
    },
    {
        "id": 102,
        "name": "iPhone 15 Pro",
        "price": 999,
        "category": "electronics",
        "description": "Latest iPhone with advanced camera system",
        "stock": 32,
        "rating": 4.9
    }
]

orders = [
    {"id": 501, "user_id": 1, "product_ids": [101], "status": "shipped"},
    {"id": 502, "user_id": 2, "product_ids": [102], "status": "pending"}
]

# API versioning: /api/v1/...


def serialize_product(product, include_description=False, include_stock=False, include_rating=False):
    """Build a product response without mutating source data."""
    item = {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "category": product["category"]
    }

    if include_description and "description" in product:
        item["description"] = product["description"]
    if include_stock and "stock" in product:
        item["stock"] = product["stock"]
    if include_rating and "rating" in product:
        item["rating"] = product["rating"]

    return item

# --- USER ENDPOINTS ---
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    """
    get users 
    ---
    responses:
      200:
        description: list of users
    """
    return jsonify(users)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    get user by ID
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: user details
      404:
        description: user not found
    """
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# --- PRODUCT ENDPOINTS ---
@app.route('/api/v1/products', methods=['GET'])
def get_products_v1():
    """
    get products with optional category filter
    ---
    parameters:
      - name: category
        in: query
        type: string
        required: false
    responses:
        200:
            description: list of products
    """
    category = request.args.get('category')
    filtered_products = products
    if category:
        filtered_products = [p for p in products if p["category"] == category]

    data = [
        serialize_product(p, include_description=False, include_stock=False, include_rating=False)
        for p in filtered_products
    ]
    return jsonify({
        "version": "v1",
        "data": data
    })


# --- PRODUCT ENDPOINTS ---
@app.route('/api/v2/products', methods=['GET'])
def get_products_v2():
    """
    get products with optional category filter and dynamic fields
    ---
    parameters:
      - name: category
        in: query
        type: string
        required: false
      - name: include
        in: query
        type: string
        required: false
        description: comma-separated fields to include (description,stock,rating)
      - name: getDescription
        in: query
        type: string
        required: false
        description: backward-compatible flag to include description=true
    responses:
        200:
            description: list of products
    """

    category = request.args.get('category')
    include_fields = {
        field.strip().lower()
        for field in request.args.get('include', '').split(',')
        if field.strip()
    }

    include_description = (
        'description' in include_fields
        or request.args.get('getDescription', '').lower() == 'true'
    )
    include_stock = 'stock' in include_fields
    include_rating = 'rating' in include_fields

    filtered_products = products
    if category:
        filtered_products = [p for p in products if p["category"] == category]

    data = [
        serialize_product(
            p,
            include_description=include_description,
            include_stock=include_stock,
            include_rating=include_rating
        )
        for p in filtered_products
    ]

    return jsonify({
        "version": "v2",
        "count": len(data),
        "included_fields": sorted(list(include_fields)),
        "data": data
    })


@app.route('/api/v2/products/<int:product_id>', methods=['GET'])
def get_product_v2(product_id):
    """
    get product by ID (v2) with dynamic fields
    ---
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: include
        in: query
        type: string
        required: false
        description: comma-separated fields to include (description,stock,rating)
    responses:
      200:
        description: product details
      404:
        description: product not found
    """
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    include_fields = {
        field.strip().lower()
        for field in request.args.get('include', '').split(',')
        if field.strip()
    }

    return jsonify(
        serialize_product(
            product,
            include_description='description' in include_fields,
            include_stock='stock' in include_fields,
            include_rating='rating' in include_fields
        )
    )

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    get product by ID
    ---
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: product details
      404:
        description: product not found
    """
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# --- ORDER ENDPOINTS ---
@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    """
    get orders
    ---
    responses:
      200:
        description: list of orders
    """
    return jsonify(orders)

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    """
    create a new order
    ---
    parameters:
      - name: order
        in: body
        type: object
        required: true
    responses:
      201:
        description: order created
    """
    new_order = request.json
    new_order["id"] = len(orders) + 501
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route('/api/v1/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """
    get orders for a specific user
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: list of user's orders
    """    
    user_orders = [o for o in orders if o["user_id"] == user_id]
    return jsonify(user_orders)

if __name__ == '__main__':
    # Chạy server ở chế độ debug để thực hành
    app.run(debug=True, port=5000)
