# API Blueprint Format

## Mô tả

**API Blueprint** là một định dạng mô tả REST API sử dụng ngôn ngữ giống Markdown, cho phép người lập trình viết tài liệu API một cách trực quan và dễ đọc.

### Ưu điểm
- ✅ Cú pháp giống Markdown, rất thân thiện với developer
- ✅ Rất dễ viết và bảo trì tài liệu
- ✅ Hỗ trợ tốt cho mock server generation
- ✅ File nhỏ gọn, dễ hiểu từ cái nhìn đầu tiên
- ✅ Xuất sắc cho tài liệu API tiếng Anh/tự nhiên

### Nhược điểm
- ❌ Cộng đồng nhỏ, ít công cụ hỗ trợ so với OpenAPI
- ❌ Không phù hợp cho schema phức tạp
- ❌ Validation không mạnh bằng OpenAPI
- ❌ Ít công cụ generate SDK/server code

## Cài đặt & Chạy

### 1. Xem spec với Apiary (Online)

Truy cập: https://apiary.io

Tạo account và paste nội dung `api.apib` để xem trực tiếp

### 2. Chạy Dredd (API Testing Tool)

```bash
# Cài Node.js
node --version

# Cài Dredd (gồm middleware để render API Blueprint)
npm install -g dredd

# Chạy Dredd
dredd api.apib http://localhost:5000

# Dredd sẽ test tất cả endpoint theo spec
```

### 3. Chạy Mock Server (Prism)

```bash
# Cài Prism
npm install -g @stoplight/prism-cli

# Chạy mock server từ API Blueprint (cần convert sang OpenAPI trước)
# hoặc Prism có thể xử lý trực tiếp tệp apib:
prism mock api.apib

# Mock server sẽ chạy tại: http://localhost:4010
```

### 4. VS Code Extension

- Cài extension: **API Blueprint Support** hoặc **API Element One**
- Mở file `api.apib`
- Xem syntax highlighting và preview

### 5. CLI Tools - Dredd CLI

```bash
# Điểm cuối API
dredd api.apib http://localhost:5000 --details

# Xem báo cáo chi tiết
dredd api.apib http://localhost:5000 --output report.json
```

### 6. Generate Mock từ CLI

```bash
# Cài protagonist (parser API Blueprint)
npm install -g protagonist

# Cài json-server để tạo mock
npm install -g json-server

# Tạo mock data từ API Blueprint
protagonist api.apib
```

### 7. Convert API Blueprint sang OpenAPI

```bash
# Cài swagger-api/swagger-tools
npm install -g api-spec-converter

# Convert
api-spec-converter --from apib --to openapi_3 api.apib > openapi.json

# Sau đó dùng OpenAPI tools
```

## Cấu trúc File API Blueprint

```apib
FORMAT: 1A          # Version
HOST: base_url      # Base URL

# API Title         # Tiêu đề API

Description         # Mô tả API

# Group Name        # Nhóm endpoint

## Resource [/path]         # Resource definition
Description

### Action [METHOD]         # Action (GET, POST, etc.)
Description

+ Parameters        # Parameters
+ Request          # Request body
+ Response         # Response body

# Data Structures   # Định nghĩa data models

## Model Name (object)
+ field: value (type) - Description
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

### Dredd Testing

```bash
# Chạy test qua Dredd
dredd api.apib http://localhost:5000

# Output:
# pass - GET /api/books
# pass - POST /api/books
# pass - GET /api/books/{book_id}
# pass - PUT /api/books/{book_id}
# pass - DELETE /api/books/{book_id}
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

## So sánh Format Spec

| Tiêu chí | API Blueprint | RAML | OpenAPI |
|---------|---------------|------|---------|
| Cú pháp | Markdown-like | YAML | YAML/JSON |
| Độ dễ đọc | Rất dễ | Trung bình | Trung bình-khó |
| Phức tạp schema | Hạn chế | Tốt | Tốt |
| Cộng đồng | Nhỏ | Trung bình | Lớn |
| Tool support | Ít | Trung bình | Rất nhiều |
| Mock server | Dredd, Prism | Tốt | Tốt |
| Testing | Dredd | Đủ | Đủ |
| Thích hợp cho | Tài liệu đơn giản | API phức tạp | Chuẩn công nghiệp |

## So sánh 3 Format

### API Blueprint
```apib
### Get Books [GET /api/books]

+ Response 200 (application/json)
    + Attributes (array[Book])
```

### RAML
```yaml
/api/books:
  get:
    responses:
      200:
        body:
          application/json:
            type: Book[]
```

### OpenAPI
```yaml
/api/books:
  get:
    responses:
      '200':
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Book'
```

**API Blueprint** dễ đọc nhất nhưng thiếu validation mạnh
**RAML** cân bằng tốt giữa tính linh hoạt và dễ dùng
**OpenAPI** chuẩn công nghiệp, support tool phong phú nhất

## Tài liệu Tham Khảo

- [API Blueprint Official](https://apiblueprint.org/)
- [Apiary.io](https://apiary.io/)
- [Dredd Testing Tool](https://dredd.org/)
- [API Blueprint Syntax](https://apiblueprint.org/documentation/)
