# TypeSpec Format

## Mô Tả

**TypeSpec** (trước đây gọi là Cadl) là một định dạng ngôn ngữ mô tả API được tạo bởi **Microsoft**. TypeSpec cho phép bạn định nghĩa API models, services, và business logic một cách tường minh, rõ ràng, và có thể tự động generate OpenAPI specs.

### Ưu Điểm
- Ngôn ngữ lập trình giống TypeScript, dễ học
- Có thể generate OpenAPI/OpenAPI 3.1 tự động
- Hỗ trợ tốt validation decorators (@minValue, @maxLength, etc.)
- Có ý định của Microsoft (lâu dài support)
- Rất rõ ràng, tường minh (không implicit)
- Hỗ trợ tốt inheritance và composition
- Có thể generate code cho nhiều language

### Nhược Điểm
- Cộng đồng còn nhỏ (format mới)
- Tool support ít hơn OpenAPI hiện tại
- Cần cài @typespec compiler
- IDE support vẫn đang phát triển

## Cài Đặt & Chạy

### 1. Cài Node.js & TypeSpec CLI

```bash
# Kiểm tra Node.js
node --version
npm --version

# Cài TypeSpec CLI globally
npm install -g @typespec/compiler

# Verify installation
tsp --version
```

### 2. Cài Dependencies

```bash
# Tạo package.json nếu chưa có
npm init -y

# Cài TypeSpec packages
npm install @typespec/compiler
npm install @typespec/http
npm install @typespec/rest
npm install @typespec/openapi3

# Cài emitter để generate OpenAPI
npm install @typespec/openapi3 -D
```

### 3. Generate OpenAPI from TypeSpec

```bash
# Validate TypeSpec file
tsp compile api.tsp

# Generate OpenAPI 3.0
tsp compile api.tsp --emit=@typespec/openapi3

# Output sẽ được lưu vào thư mục tuy chọn
# (default: ./tsp-output/openapi.yaml)
```

### 4. Xem Generated OpenAPI

```bash
# Sau khi generate, mở openapi.yaml với Swagger Editor
# https://editor.swagger.io

# Copy nội dung từ:
# tsp-output/openapi.yaml

# Hoặc chạy Swagger UI local
docker run -p 8080:8080 -e SWAGGER_JSON=/foo/openapi.yaml \
  -v $(pwd)/tsp-output:/foo swaggerapi/swagger-ui
```

### 5. VS Code Extension

- Cài extension: **TypeSpec for VS Code** (Microsoft)
- Mở file `api.tsp`
- Syntax highlighting, validation, autocomplete tự động
- Hover để xem documentation

### 6. Watch Mode (Auto Compile)

```bash
# Compile tự động khi file thay đổi
tsp compile api.tsp --watch

# Terminal sẽ output errors/warnings realtime
```

### 7. Setup tsp-config.yaml

Tạo file `tsp-config.yaml` để cấu hình compiler:

```yaml
emit:
  - "@typespec/openapi3"

options:
  "@typespec/openapi3":
    output-file: "openapi.yaml"
```

Sau đó chạy:
```bash
tsp compile
```

### 8. Generate Python Client/Server

```bash
# Cài Python emitter
npm install @typespec/python -D

# Generate Python models
tsp compile api.tsp --emit=@typespec/python
```

## Cấu Trúc File TypeSpec

```typespec
import "@typespec/http";           // HTTP decorators
import "@typespec/rest";            // REST patterns
import "@typespec/openapi3";        // OpenAPI 3.0 support

@service({ ... })                  // Service metadata
@baseUri("...")                     // Base URL
namespace BookManagementAPI;        // Namespace

model Book { ... }                  // Data models
model CreateBookRequest { ... }

@tag("Books")                       // Grouping
@route("/api/books")                // Base route
interface BooksService {            // Service definition
  @get
  @doc("...")
  listBooks(...): Book[];           // Operations
  
  @post
  @statusCode(201)
  createBook(...): Book;
}

@error
model BadRequest { ... }            // Error definitions
```

## Ví Dụ Test

### 1. Generate & Validate

```bash
# Compile file
tsp compile api.tsp

# Xem output
cat tsp-output/openapi.yaml
```

### 2. Swagger UI Test

```bash
# Copy generated openapi.yaml
cp tsp-output/openapi.yaml ./openapi.yaml

# Mở https://editor.swagger.io
# Paste nội dung openapi.yaml

# Try it out trực tiếp trên browser
```

### 3. cURL Test

```bash
# Giả sử server chạy tại http://localhost:5000

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
  -d '{"title":"Clean Code (Updated)"}'

# DELETE xóa sách
curl -X DELETE http://localhost:5000/api/books/1
```

### 4. HTTP Client (VS Code)

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

Run từng request bằng nút "Send Request"

## TypeSpec Decorators (Attributes)

```typespec
// Validation
@minLength(1)      // Minimum string length
@maxLength(100)    // Maximum string length
@minValue(0)       // Minimum numeric value
@maxValue(1000)    // Maximum numeric value
@pattern("^[a-z]+$")  // Regex pattern

// Documentation
@doc("Description")    // Inline documentation
@example("value")      // Example value

// HTTP
@get, @post, @put, @delete, @patch
@route("/path")        // Route path
@path                  // Path parameter
@query                 // Query parameter
@header                // Header parameter
@body                  // Request body
@statusCode(201)       // HTTP status code

// API Organization
@tag("TagName")        // Group operations
@service({ ... })      // Service metadata
@baseUri("...")        // Base URL

// Data
@doc, @example        // Documentation
? (optional)          // Optional fields
... (spread)          // Spread operator
```

## So Sánh TypeSpec với Các Format Khác

| Tiêu Chí | TypeSpec | OpenAPI | RAML | API Blueprint |
|---------|----------|---------|------|---------------|
| **Cú pháp** | TypeScript-like | YAML/JSON | YAML | Markdown-like |
| **Dễ học** | Tốt (nếu biết TS) | Trung bình | Trung bình | Rất dễ |
| **Validation** | Tốt (@decorators) | Giới hạn | Giới hạn | Kém |
| **Generate OpenAPI** | Native | N/A (là standard) | Có | Có (convert) |
| **IDE Support** | Tốt | Trung bình | Ít | Ít |
| **Tính tường minh** | Rất cao | Cao | Trung bình | Thấp |
| **Cộng đồng** | Growing (Microsoft) | Rất lớn | Trung bình | Nhỏ |
| **Thích hợp cho** | Modern APIs | Public APIs | Enterprise | Tài liệu |
| **Dự kiến tương lai** | Sẽ tăng | Stable | Stable | Ít phát triển |

## Lợi Ích TypeSpec

1. **Tự Generate OpenAPI**
   - Write once, generate OpenAPI automatically
   - Luôn sync (không cần update 2 file)

2. **Type Safety & Validation**
   - @minLength, @maxValue decorators
   - Tự generate validators

3. **Rõ Ràng & Tường Minh**
   - Không có implicit behavior
   - Dễ hiểu ngay từ cái nhìn đầu

4. **Microsoft Support**
   - Part of Azure API ecosystem
   - Long-term support guaranteed

5. **Generate Code**
   - Python, TypeScript, Java, C#, etc.
   - CLI tools full-featured

## Khi Nào Dùng TypeSpec

Dùng TypeSpec nếu:
- Muốn write API spec một lần, generate toàn bộ
- Ưu tiên tường minh, rõ ràng
- Dùng Azure/Microsoft ecosystem
- Team biết TypeScript
- Cần validation decorators mạnh

Không dùng nếu:
- Cộng đồng tool support là priority
- Cần widely-supported format (OpenAPI)
- Tài liệu đơn giản (dùng API Blueprint)
- Non-TypeScript ecosystem

## Lộ Trình Học TypeSpec

1. Đọc `api.tsp` spec (giống TypeScript)
2. Hiểu decorators (@get, @post, @route, @doc)
3. Cài TypeSpec CLI
4. Compile thử: `tsp compile api.tsp`
5. Xem generated OpenAPI
6. Modify api.tsp, regenerate
7. Integrate vào project

## Quick Start

```bash
# 1. Cài
npm install -g @typespec/compiler

# 2. Copy api.tsp
cp api.tsp .

# 3. Compile
tsp compile api.tsp

# 4. Xem kết quả
cat tsp-output/openapi.yaml

# 5. Validate
tsp compile api.tsp --emit=@typespec/openapi3
```

## Tài Liệu Tham Khảo

- [TypeSpec Official](https://typespec.io/)
- [TypeSpec GitHub](https://github.com/microsoft/typespec)
- [TypeSpec Documentation](https://typespec.io/docs)
- [TypeSpec Playground](https://typespec.io/playground)
- [TypeSpec Examples](https://github.com/microsoft/typespec/tree/main/packages/samples)

---

**TypeSpec** = TypeScript-like language để define APIs + auto-generate OpenAPI specs
