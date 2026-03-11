from flask import Flask, jsonify, request

app = Flask(__name__)

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
    return jsonify(users)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# --- PRODUCT ENDPOINTS ---
@app.route('/api/v1/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    if category:
        filtered = [p for p in products if p["category"] == category]
        return jsonify(filtered)
    return jsonify(products)

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Lấy chi tiết sản phẩm"""
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# --- ORDER ENDPOINTS ---
@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    new_order = request.json
    new_order["id"] = len(orders) + 501
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route('/api/v1/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    user_orders = [o for o in orders if o["user_id"] == user_id]
    return jsonify(user_orders)

if __name__ == '__main__':
    # Chạy server ở chế độ debug để thực hành
    app.run(debug=True, port=5000)
