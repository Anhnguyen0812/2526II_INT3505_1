from flask import Flask, jsonify, request, session, make_response
from flasgger import Swagger
from functools import wraps
import os
import time
import jwt
import datetime

app = Flask(__name__)
# Thiết lập Secret Key để mã hóa Session và JWT
app.secret_key = "my_secret_key_12345" 
SECRET_KEY = app.secret_key

# Cấu hình Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

template = {
    "securityDefinitions": {
        "basicAuth": {
            "type": "basic"
        },
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Nhập JWT Token theo định dạng: Bearer <token>"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=template)

# Dữ liệu tài khoản giả lập
users = {
    "admin": "admin123",
    "user": "user123"
}

def require_auth(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Kiểm tra JWT Token trong Header Authorization
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Thiếu mã xác thực!"}), 401
            
            try:
                # Định dạng là 'Bearer <token>'
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                current_user = payload['sub']
                user_role = payload.get('role', 'user')
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token đã hết hạn!"}), 401
            except (jwt.InvalidTokenError, IndexError):
                return jsonify({"message": "Token không hợp lệ!"}), 401
            
            # Phân quyền đơn giản: Nếu là admin thì được làm mọi thứ
            if role == "admin" and user_role != "admin":
                return jsonify({"message": "Bạn không có quyền admin!"}), 403
            
            request.user = current_user
            request.user_role = user_role
            return f(*args, **kwargs)
        return decorated
    return decorator

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

# 1. Lấy danh sách tất cả sách (GET) - Ai cũng có thể xem
@app.route('/api/books', methods=['GET'])
@require_auth()
def get_books():
    """
    Lấy danh sách tất cả các sách trong thư viện (Yêu cầu JWT Token)
    ---
    security:
      - bearerAuth: []
    responses:
      200:
        description: Danh sách các đầu sách
    """
    return jsonify(books), 200

# 2. Lấy chi tiết một cuốn sách (GET) - Cacheable theo chuẩn REST (Browser Cache)
@app.route('/api/books/<int:book_id>', methods=['GET'])
@require_auth()
def get_book(book_id):
    """
    Lấy thông tin chi tiết một cuốn sách (Sử dụng Browser Cache)
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Thông tin cuốn sách (Kèm header Cache-Control)
        headers:
          Cache-Control:
            type: string
            description: max-age=300 (Lưu tại trình duyệt trong 300 giây)
      404:
        description: Không tìm thấy sách
    """
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        return jsonify({"message": "Không tìm thấy sách"}), 404
    
    # Tạo response object
    response = make_response(jsonify(book))
    
    # Tuân thủ ràng buộc "Cacheable" của REST API
    # Server chỉ định cho trình duyệt lưu cache kết quả này trong 300 giây
    response.headers['Cache-Control'] = 'public, max-age=300'
    
    return response, 200

# 3. Thêm sách mới (POST) - Chỉ Admin
@app.route('/api/books', methods=['POST'])
@require_auth(role="admin")
def create_book():
    """
    Thêm một cuốn sách mới vào thư viện (Chỉ Admin JWT)
    ---
    security:
      - bearerAuth: []
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
      403:
        description: Không có quyền admin
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

# 4. Cập nhật thông tin sách (PUT) - Chỉ Admin
@app.route('/api/books/<int:book_id>', methods=['PUT'])
@require_auth(role="admin")
def update_book(book_id):
    """
    Cập nhật toàn bộ thông tin một cuốn sách (Chỉ Admin JWT)
    ---
    security:
      - bearerAuth: []
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
      403:
        description: Không có quyền admin
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

# 5. Xóa sách (DELETE) - Chỉ Admin
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@require_auth(role="admin")
def delete_book(book_id):
    """
    Xóa một cuốn sách khỏi thư viện (Chỉ Admin JWT)
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Đã xóa thành công
      403:
        description: Không có quyền admin
    """
    global books
    books = [b for b in books if b['id'] != book_id]
    return '', 204

# web session: Stateful (Session ID lưu trong Cookie) vs Stateless (Token-based, không lưu trạng thái trên server)

# 6. Đăng nhập để lấy JWT Token (Stateless)
@app.route('/api/login', methods=['POST'])
def login():
    """
    Đăng nhập hệ thống để nhận JWT Token (Stateless)
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Đăng nhập thành công, trả về JWT Token
        schema:
          type: object
          properties:
            token:
              type: string
    """
    auth = request.authorization
    if not auth or auth.username not in users or users[auth.username] != auth.password:
        return jsonify({"message": "Xác thực thất bại!"}), 401

    role = 'admin' if auth.username == 'admin' else 'user'
    
    # Tạo JWT Token (Stateless)
    payload = {
        'sub': auth.username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        "message": f"Chào {auth.username}, đây là Token của bạn!",
        "token": token
    }), 200

# 7. Lấy thông tin từ JWT Token (Stateless)
@app.route('/api/me', methods=['GET'])
@require_auth()
def profile():
    """
    Lấy thông tin người dùng từ JWT Token (Stateless)
    ---
    security:
      - bearerAuth: []
    responses:
      200:
        description: Thông tin người dùng từ Token
      401:
        description: Token không hợp lệ hoặc đã hết hạn
    """
    return jsonify({
        "username": request.user,
        "role": request.user_role,
        "status": "Đang hoạt động (Stateless JWT)"
    }), 200

# 8. Đăng xuất (Client chỉ cần xóa Token)
@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Đăng xuất (Client tự xóa Token, Server không cần làm gì vì stateless)
    ---
    responses:
      200:
        description: Hướng dẫn đăng xuất
    """
    return jsonify({"message": "Đã đăng xuất! Hãy xóa JWT Token ở phía Client."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
