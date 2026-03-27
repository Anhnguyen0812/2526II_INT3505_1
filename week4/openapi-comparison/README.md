# OpenAPI Comparison - 4 API Definition Formats

So sánh 4 định dạng phổ biến để mô tả REST API: **OpenAPI**, **RAML**, **API Blueprint**, và **TypeSpec**.

## Cấu trúc Folder

```
openapi-comparison/
├── OpenAPI/
│   ├── openapi.yaml          # OpenAPI 3.0.3 spec
│   └── README.md             # Hướng dẫn cài đặt & chạy
├── RAML/
│   ├── api.raml              # RAML 1.0 spec
│   └── README.md             # Hướng dẫn cài đặt & chạy
├── API_Blueprint/
│   ├── api.apib              # API Blueprint spec
│   └── README.md             # Hướng dẫn cài đặt & chạy
├── TypeSpec/
│   ├── api.tsp               # TypeSpec spec
│   └── README.md             # Hướng dẫn cài đặt & chạy
└── README.md                 # File này
```

## Tóm Tắt 4 Format

### 1. OpenAPI 3.0.3

**Chuẩn công nghiệp, support tool tốt nhất**

- Được hỗ trợ rộng rãi (Swagger UI, Postman, IDE, etc.)
- Có thể generate SDK/server code tự động
- Format YAML và JSON đều được hỗ trợ
- Cú pháp lặp lại, file dài
- Xem chi tiết: [OpenAPI/README.md](OpenAPI/README.md)

### 2. RAML 1.0

**Cân bằng tốt, dễ dùng hơn OpenAPI**

- Cú pháp sạch sẽ, dễ đọc
- Hỗ trợ tốt inheritance/reuse (extends)
- Được MuleSoft hỗ trợ mạnh
- Cộng đồng nhỏ hơn OpenAPI
- Xem chi tiết: [RAML/README.md](RAML/README.md)

### 3. API Blueprint

**Dễ viết nhất, giống Markdown**

- Cú pháp giống Markdown, rất dễ học
- Tuyệt vời cho tài liệu đơn giản
- Dredd testing tool rất tiện
- Hạn chế với schema phức tạp
- Xem chi tiết: [API_Blueprint/README.md](API_Blueprint/README.md)

### 4. TypeSpec

**Microsoft format, generate OpenAPI tự động**

- TypeScript-like syntax, dễ học
- Auto-generate OpenAPI 3.0/3.1
- Validation decorators (@minLength, @maxValue, etc.)
- Microsoft support (Azure ecosystem)
- Có thể generate code (Python, TypeScript, Java, C#)
- Cộng đồng còn nhỏ (format mới)
- IDE support đang phát triển
- Xem chi tiết: [TypeSpec/README.md](TypeSpec/README.md)

## Bảng So Sánh Chi Tiết

| Tiêu Chí | OpenAPI | RAML | API Blueprint | TypeSpec |
|---------|---------|------|---------------|----------|
| **Cú pháp** | YAML/JSON | YAML | Markdown-like | TypeScript-like |
| **Độ dễ dùng** | Trung bình | Tốt | Rất tốt | Tốt |
| **Complex schemas** | Tốt | Tốt | Hạn chế | Tuyệt vời |
| **Kế thừa** | Giới hạn | Tốt | N/A | Tốt |
| **Cộng đồng** | Rất lớn | Trung bình | Nhỏ | Growing(Microsoft) |
| **Tool support** | Rất nhiều | Trung bình | Ít | Phát triển |
| **IDE support** | Tốt | Trung bình | Ít | Tốt |
| **Validation** | Giới hạn | Giới hạn | Kém | Tốt (@decorators) |
| **Auto-generate OpenAPI** | N/A (là standard) | Có | Có (convert) | **Native** |
| **Generate Code** | Tốt | Trung bình | Kém | Tốt |
| **Mock server** | Có | Có | Dredd, Prism | Prism (from generated) |
| **Thích hợp cho** | Public API, standard | API phức tạp | Tài liệu đơn giản | Modern APIs, Azure |

## Nhanh Chóng Bắt Đầu

### OpenAPI

```bash
cd OpenAPI
# Xem: https://editor.swagger.io
# Paste openapi.yaml vào
```

### RAML

```bash
cd RAML
# Xem: https://apidesigner.mulesoft.com
# Paste api.raml vào
```

### API Blueprint

```bash
cd API_Blueprint
# Xem: https://apiary.io
# Paste api.apib vào
```

### TypeSpec

```bash
cd TypeSpec
# Xem: https://typespec.io/playground
# Paste api.tsp vào
# Hoặc chạy locally:
npm install
npm run build
```

## Cài Đặt & Kiểm Tra Toàn Bộ

### Cài tất cả tools

```bash
# Node.js
node --version

# OpenAPI Generator CLI
npm install -g @openapitools/openapi-generator-cli

# RAML Validator
npm install -g @apidom/cli

# API Blueprint Dredd
npm install -g dredd

# Mock Server
npm install -g @stoplight/prism-cli

# Format Converter
npm install -g api-spec-converter
```

### Test cả 4 spec

```bash
# Assuming server running at http://localhost:5000

# Test OpenAPI
cd OpenAPI
dredd openapi.yaml http://localhost:5000

# Test RAML (convert first)
cd ../RAML
api-spec-converter --from raml --to openapi_3 api.raml > temp.json
dredd temp.json http://localhost:5000

# Test API Blueprint
cd ../API_Blueprint
dredd api.apib http://localhost:5000

# Test TypeSpec (generate OpenAPI first, then test)
cd ../TypeSpec
npm run build
dredd tsp-output/openapi.yaml http://localhost:5000
```

## Recommendation

### Chọn format nào?

1. **OpenAPI** - Nếu:
   - Cần public API sẽ được nhiều tool, client sử dụng
   - Muốn SDK generation tự động
   - Toàn công ty dùng Swagger ecosystem
   - Cần standardization & enterprise support

2. **RAML** - Nếu:
   - API phức tạp với schema kế thừa
   - Dùng MuleSoft platform
   - Team muốn cú pháp sạch sẽ hơn OpenAPI
   - Nội bộ, không cần public khoa học

3. **API Blueprint** - Nếu:
   - Tài liệu API đơn giản, dễ hiểu
   - Team muốn Markdown-like format
   - Ưu tiên tài liệu developer-friendly

4. **TypeSpec** - Nếu:
   - Dùng TypeScript project
   - Muốn type safety tối đa + code = spec
   - Nhu cầu auto-generate OpenAPI 3.0/3.1
   - Cần validation decorators mạnh mẽ
   - Tích hợp Azure/Microsoft ecosystem

### Nếu muốn production-ready?
→ **Dùng OpenAPI** + kết hợp Swagger UI + Postman.
→ Hoặc **TypeSpec** nếu TypeScript project + cần auto-generation.
## Tips Sử Dụng

### Nếu bạn không biết chọn gì?
→ **Dùng OpenAPI** vì nó chuẩn công nghiệp, support tool phong phú nhất.

### Nếu muốn schema sạch sẽ?
→ **Dùng RAML** vì syntax rõ ràng hơn OpenAPI.

### Nếu muốn dễ viết?
→ **Dùng API Blueprint** vì giống Markdown.

### Nếu muốn production-ready?
→ **Dùng OpenAPI** + kết hợp Swagger UI + Postman.

## Tài Liệu Tham Khảo

- [OpenAPI 3.0 Spec](https://spec.openapis.org/oas/v3.0.3)
- [RAML 1.0 Spec](https://github.com/raml-org/raml-spec)
- [API Blueprint](https://apiblueprint.org/)
- [TypeSpec - Official Docs](https://typespec.io/)
- [TypeSpec Playground](https://typespec.io/playground)
- [API Spec Converter](https://www.npmjs.com/package/api-spec-converter)

## Chạy Mock Server Cho Tất Cả

```bash
# OpenAPI (via Prism)
cd OpenAPI
prism mock openapi.yaml

# RAML (via Prism)
cd ../RAML
prism mock api.raml

# API Blueprint (via Prism)
cd ../API_Blueprint
prism mock api.apib

# TypeSpec (generate OpenAPI trước, sau đó mock)
cd ../TypeSpec
tsp compile api.tsp --emit=@typespec/openapi3
prism mock tsp-output/openapi.yaml
```

Mỗi mock server sẽ chạy tại `http://localhost:4010` (thay đổi port nếu có conflict)

## Ví Dụ Thực Tế

Giả sử bạn muốn test endpoint GET /api/books?q=Clean

### OpenAPI (Swagger UI)
```bash
cd OpenAPI
# Mở http://localhost:5000/docs
# Click "Try it out"
# Nhập q=Clean, click Execute
```

### RAML (API Designer)
```bash
cd RAML
npm install -g api-designer
api-designer
# Mở http://localhost:3000
# View spec + generate code
```

### API Blueprint (Dredd Testing)
```bash
cd API_Blueprint
dredd api.apib http://localhost:5000
```

### TypeSpec (Generate & Test)
```bash
cd TypeSpec
npm run build
# Xem generated OpenAPI tại tsp-output/openapi.yaml
dredd tsp-output/openapi.yaml http://localhost:5000
```

---

Mỗi folder chứa file spec và README chi tiết về cách setup, chạy, test từng format.
