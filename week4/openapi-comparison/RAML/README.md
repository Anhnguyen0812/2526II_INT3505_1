# RAML 1.0 Format

## Mô tả

**RAML** (RESTful API Modeling Language) là một ngôn ngữ được thiết kế riêng để mô tả REST API một cách rõ ràng, dễ đọc và dễ bảo trì.

### Ưu điểm
- ✅ Cú pháp đơn giản, dễ đọc hơn OpenAPI
- ✅ Hỗ trợ kế thừa (extends) và reuse types hiệu quả
- ✅ Tích hợp tốt với MuleSoft API Platform
- ✅ File YAML rõ ràng với ít boilerplate
- ✅ Hỗ trợ tốt cho các schema phức tạp

### Nhược điểm
- ❌ Cộng đồng nhỏ hơn OpenAPI
- ❌ Support tool ít hơn (chủ yếu MuleSoft)
- ❌ Việc generate SDK/server code ít công cụ hỗ trợ

## Cài đặt & Chạy

### 1. Xem spec với API Designer (Online)

Truy cập: https://apidesigner.mulesoft.com

Paste nội dung `api.raml` để xem trực tiếp

### 2. Chạy RAML API Designer Local

```bash
# Cài Node.js
node --version

# Cài API Designer CLI
npm install -g api-designer

# Chạy trong folder chứa api.raml
api-designer

# Truy cập tại: http://localhost:3000
```

### 3. Validate RAML spec

```bash
# Cài amf (AMF - API Modeling Framework)
npm install -g @apidom/cli

# Validate
apidom api.raml
```

### 4. VS Code Extension

- Cài extension: **RAML**
- Mở file `api.raml`
- Syntax highlighting và validation tự động

### 5. Generate Mock Server (RAML to Mock Server)

```bash
# Cài prism
npm install -g @stoplight/prism-cli

# Chạy mock server từ RAML (chuyển đổi sang OpenAPI trước)
prism mock api.raml

# Mock server sẽ chạy tại: http://localhost:4010
```

### 6. Convert RAML to OpenAPI

```bash
# Cài api-spec-converter
npm install -g api-spec-converter

api-spec-converter --from raml --to swagger_2 api.raml > swagger.json
# hoặc
api-spec-converter --from raml --to openapi_3 api.raml > openapi.json
```

## Cấu trúc File RAML

```yaml
#%RAML 1.0                # RAML version
title:                    # Tên API
version:                  # Phiên bản
description:              # Mô tả
baseUri:                  # Base URL
mediaType:                # Default media type

types:                    # Định nghĩa kiểu dữ liệu (schemas)
  Schema1:
    type: object
    properties: ...

traits:                   # Reusable traits (giống interceptor)
  secured:
    headers:
      Authorization:

resourceTypes:            # Reusable resource patterns

/path:                    # Resource (endpoint)
  displayName:            # Tên hiển thị
  description:            # Mô tả
  get/post/put/delete:    # HTTP methods
    description:
    queryParameters:
    body:
    responses:
  /{id}:                  # Sub-resource
    uriParameters:
```

## Ví dụ Test

### cURL

```bash
# GET danh sách sách
curl http://localhost:5000/api/books

# GET sách theo ID
curl http://localhost:5000/api/books/1

# Search sách
curl "http://localhost:5000/api/books?q=Clean"

# POST tạo sách mới
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Clean Code",
    "author":"Robert Martin",
    "published_year":2008
  }'

# PUT cập nhật sách
curl -X PUT http://localhost:5000/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code by Robert"}'

# DELETE xóa sách
curl -X DELETE http://localhost:5000/api/books/1
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

### Postman (cần convert sang OpenAPI trước)

```bash
# Convert RAML -> OpenAPI
api-spec-converter --from raml --to openapi_3 api.raml > openapi.json

# Import vào Postman
# File → Import → Chọn openapi.json
```

## So sánh với OpenAPI

| Tiêu chí | RAML | OpenAPI |
|---------|------|---------|
| Cú pháp | Đơn giản, gọn gàng | Chi tiết, dài hơn |
| Kế thừa | Hỗ trợ tốt (extends) | Có nhưng hạn chế hơn |
| Cộng đồng | Nhỏ hơn, chủ yếu MuleSoft | Lớn hơn, chuẩn công nghiệp |
| Tool support | MuleSoft, một số online tools | Rất phong phú (Swagger, Postman, etc.) |
| YAML/JSON | Chủ yếu YAML | Cả hai |
| Thích hợp cho | API phức tạp, nội bộ | Public API, chuẩn công nghiệp |

## Tài liệu Tham Khảo

- [RAML 1.0 Official Spec](https://github.com/raml-org/raml-spec/blob/master/versions/raml-10/raml-10.md)
- [MuleSoft API Designer](https://www.mulesoft.com/exchange/)
- [AMF Documentation](https://a.ml/)
- [Prism Mock Server](https://stoplight.io/open-source/prism)
