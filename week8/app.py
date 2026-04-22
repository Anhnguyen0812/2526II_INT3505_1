from flask import Flask, jsonify, request

app = Flask(__name__)

# Dữ liệu giả lập
items = [
    {"id": 1, "name": "Laptop", "price": 1000},
    {"id": 2, "name": "Phone", "price": 500}
]

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint kiểm tra trạng thái hệ thống"""
    return jsonify({"status": "healthy", "message": "API is running"}), 200

@app.route('/items', methods=['GET'])
def get_items():
    """Lấy danh sách tất cả sản phẩm"""
    return jsonify(items), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Lấy thông tin chi tiết một sản phẩm theo ID"""
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 44

@app.route('/items', methods=['POST'])
def create_item():
    """Tạo sản phẩm mới"""
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    new_item = {
        "id": len(items) + 1,
        "name": data['name'],
        "price": data['price']
    }
    items.append(new_item)
    return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Cập nhật sản phẩm hiện có"""
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    data = request.get_json()
    item['name'] = data.get('name', item['name'])
    item['price'] = data.get('price', item['price'])
    
    return jsonify(item), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Xóa sản phẩm"""
    global items
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    items = [i for i in items if i["id"] != item_id]
    return jsonify({"message": "Item deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
