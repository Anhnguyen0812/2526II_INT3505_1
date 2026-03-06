from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Dữ liệu giả lập
tasks = [
    {"id": 1, "title": "Học Flask", "done": False},
    {"id": 2, "title": "Xây dựng API", "done": False}
]

@app.route('/', methods=['GET'])
def home():
    return "Chào mừng bạn đến với Flask API đơn giản!"

# Lấy danh sách task
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    Lấy danh sách các công việc hiện có
    ---
    responses:
      200:
        description: Danh sách các tasks
        schema:
          type: object
          properties:
            tasks:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  done:
                    type: boolean
    """
    return jsonify({"tasks": tasks})

# Thêm task mới
@app.route('/api/tasks', methods=['POST'])
def add_task():
    """
    Thêm một công việc mới
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
              example: "Học Flask"
    responses:
      201:
        description: Task đã được tạo thành công
      400:
        description: Dữ liệu không hợp lệ
    """
    if not request.json or not 'title' in request.json:
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
    
    new_task = {
        "id": tasks[-1]['id'] + 1 if tasks else 1,
        "title": request.json['title'],
        "done": False
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
