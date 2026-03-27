# OpenAPI 3.0.3 Format

## Mô tả

**OpenAPI** (trước đây là Swagger) là đặc tả tiêu chuẩn công nghiệp để mô tả REST API.

### Ưu điểm
- ✅ Chuẩn công nghiệp, hỗ trợ rộng rãi
- ✅ Tích hợp tốt với Swagger UI, Swagger Editor
- ✅ Có thể generate client SDK/server code tự động
- ✅ Hỗ trợ security schemes (OAuth, JWT, etc.)
- ✅ Format YAML và JSON đều được hỗ trợ

### Nhược điểm
- ❌ Cú pháp dài, phức tạp hơn RAML
- ❌ Không hỗ trợ inheritance (schema composition hạn chế)

## Cài đặt & Chạy

### 1. Xem spec với Swagger Editor (Online)

Mở https://editor.swagger.io và paste nội dung `openapi.yaml`

### 2. Chạy Swagger UI Local

```bash
# Cài Docker
docker --version

# Chạy Swagger UI container
docker run -p 8080:8080 -e SWAGGER_JSON=/foo/openapi.yaml -v $(pwd):/foo swaggerapi/swagger-ui

# Truy cập tại: http://localhost:8080
```

### 3. VS Code Extension

- Cài extension: **OpenAPI (Swagger) Editor** (42Crunch)
- Mở file `openapi.yaml`
- Xem preview trực tiếp

### 4. Generate Python Flask Server

```bash
# Cài openapi-generator-cli
npm install -g @openapitools/openapi-generator-cli

# Generate server
openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./generated_server

# Cài dependencies
cd generated_server
pip install -r requirements.txt

# Chạy server
python -m openapi_server
```

### 5. Generate TypeScript Client

```bash
# Generate client
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./generated_client

# Cài dependencies
cd generated_client
npm install

# Dùng trong project TypeScript/React
```

### 6. Postman Import

- Mở Postman
- File → Import
- Chọn `openapi.yaml`
- Tự động import tất cả endpoint

## Cấu trúc File

```yaml
openapi: 3.0.3             # Phiên bản OpenAPI
info:                      # Thông tin API
  title:
  version:
  description:
servers:                   # Danh sách server (local, staging, prod)
tags:                      # Nhóm endpoint
paths:                     # Các endpoint
  /path:
    get/post/put/delete:   # HTTP methods
      parameters:          # Query params, path params
      requestBody:         # Request body schema
      responses:           # Response schemas và status codes
components:                # Reusable schemas & parameters
  schemas:
  parameters:
  securitySchemes:
```

## Ví dụ Test

### cURL

```bash
# GET danh sách sách
curl http://localhost:5000/api/books

# GET sách theo ID
curl http://localhost:5000/api/books/1

# POST tạo sách mới
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","published_year":2008}'

# PUT cập nhật sách
curl -X PUT http://localhost:5000/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code by Robert"}'

# DELETE xóa sách
curl -X DELETE http://localhost:5000/api/books/1
```

### cURL với Search Query

```bash
curl "http://localhost:5000/api/books?q=Clean"
```

### HTTP Client (VS Code)

Tạo file `test.http`:

```http
### Get all books
GET http://localhost:5000/api/books

### Search books
GET http://localhost:5000/api/books?q=Clean

### Get book by ID
GET http://localhost:5000/api/books/1

### Create book
POST http://localhost:5000/api/books
Content-Type: application/json

{
  "title": "Design Patterns",
  "author": "Gang of Four",
  "published_year": 1994
}

### Update book
PUT http://localhost:5000/api/books/1
Content-Type: application/json

{
  "title": "Clean Code (Updated)"
}

### Delete book
DELETE http://localhost:5000/api/books/1
```

Chạy bằng nút Run trên mỗi request hoặc Ctrl+Alt+R

## Xem Swagger UI từ API

Nếu server implement `/docs` endpoint:

```bash
python main.py
# Truy cập http://localhost:5000/docs
```

## Tài liệu Tham Khảo

- [OpenAPI.Tools](https://tools.openapis.org/)
- [Swagger.io](https://swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Official OpenAPI 3.0 Spec](https://spec.openapis.org/oas/v3.0.3)
