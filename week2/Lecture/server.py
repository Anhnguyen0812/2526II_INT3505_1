from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Dữ liệu giả lập cho Thư viện
books = [
    {"id": 1, "title": "Sách Lập Trình Python", "author": "Nguyễn Văn A", "available": True},
    {"id": 2, "title": "Cấu trúc dữ liệu và giải thuật", "author": "Trần Thị B", "available": False}
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Chào mừng bạn đến với Hệ thống Quản lý Thư viện API!",
        "endpoints": {
            "books_list": "/api/books",
            "swagger_docs": "/apidocs"
        }
    })

# 1. Lấy danh sách tất cả sách (GET)
@app.route('/api/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách tất cả các sách trong thư viện
    ---
    responses:
      200:
        description: Danh sách các đầu sách
    """
    return jsonify(books), 200

# 2. Lấy chi tiết một cuốn sách (GET)
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Lấy thông tin chi tiết một cuốn sách theo ID
    ---
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Thông tin cuốn sách
      404:
        description: Không tìm thấy sách
    """
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        return jsonify({"message": "Không tìm thấy sách"}), 404
    return jsonify(book), 200

# 3. Thêm sách mới (POST)
@app.route('/api/books', methods=['POST'])
def create_book():
    """
    Thêm một cuốn sách mới vào thư viện
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            author:
              type: string
    responses:
      201:
        description: Sách được tạo thành công
    """
    if not request.json or not 'title' in request.json:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400
    
    new_book = {
        "id": books[-1]['id'] + 1 if books else 1,
        "title": request.json['title'],
        "author": request.json.get('author', 'Ẩn danh'),
        "available": True
    }
    books.append(new_book)
    return jsonify(new_book), 201

# 4. Cập nhật thông tin sách (PUT)
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Cập nhật toàn bộ thông tin một cuốn sách
    ---
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            author:
              type: string
            available:
              type: boolean
    responses:
      200:
        description: Cập nhật thành công
    """
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        return jsonify({"message": "Không tìm thấy sách"}), 404
    
    data = request.json
    book.update({
        "title": data.get('title', book['title']),
        "author": data.get('author', book['author']),
        "available": data.get('available', book['available'])
    })
    return jsonify(book), 200

# 5. Xóa sách (DELETE)
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Xóa một cuốn sách khỏi thư viện
    ---
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Đã xóa thành công
    """
    global books
    books = [b for b in books if b['id'] != book_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)
