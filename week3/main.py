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
    {"id": 101, "name": "Laptop Dell XPS", "price": 1200, "category": "electronics"},
    {"id": 102, "name": "iPhone 15 Pro", "price": 999, "category": "electronics"}
]

orders = [
    {"id": 501, "user_id": 1, "product_ids": [101], "status": "shipped"},
    {"id": 502, "user_id": 2, "product_ids": [102], "status": "pending"}
]

# API versioning: /api/v1/...

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
def get_products():
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
    if category:
        filtered = [p for p in products if p["category"] == category]
        return jsonify(filtered)
    return jsonify(products)

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
