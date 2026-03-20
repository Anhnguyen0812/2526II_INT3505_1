# Week 4 - Book Management API

## Mô tả

API quản lý sách sử dụng Flask, được mô tả bằng OpenAPI 3.0.3 và deploy lên Vercel.

## Cấu trúc dự án

```
week4/
├── main.py                 # Flask application chính
├── openapi.yaml            # OpenAPI specification
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
├── gencode_test/           # Folder gen code bằng OpenAPI Generator
│   ├── server/             # Generated Flask server (đầy đủ boilerplate)
│   │   ├── openapi_server/    # Thư mục code chính
│   │   ├── test/              # Unit tests được generate
│   │   └── requirements.txt    # Dependencies cho generated code
│   └── openapitools.json   # OpenAPI Generator config
└── README.md               # File này
```

## Swagger UI & Testing

### 2 Server Available

OpenAPI spec cung cấp 2 server để test:

1. **Local Development** (http://localhost:5000)
   - Dùng khi chạy app locally
   - Swagger UI: http://localhost:5000/docs

2. **Deployed API** (https://week4-smoky.vercel.app)
   - Dùng khi test trên production
   - Swagger UI: https://week4-smoky.vercel.app/docs

### Cách chọn Server trên Swagger

- Mở `/docs` endpoint
- Tìm dropdown **Servers** ở top right (hoặc ở mục info)
- Chọn môi trường muốn test
- Các nút **Try it out** sẽ gửi request đến server đã chọn

## Dependencies

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy app
python main.py
```

### requirements.txt chứa:
- **Flask==3.0.3** - Web framework
- **Werkzeug==3.0.3** - WSGI utilities

## API Endpoints

Tất cả endpoint đều bắt đầu bằng `/api/books`:

- `GET /api/books` - Lấy danh sách sách (support tìm kiếm qua `?q=keyword`)
- `POST /api/books` - Tạo sách mới
- `GET /api/books/{book_id}` - Lấy chi tiết sách
- `PUT /api/books/{book_id}` - Cập nhật sách
- `DELETE /api/books/{book_id}` - Xóa sách

Chi tiết đầy đủ ở `openapi.yaml` hoặc mở `/docs` Swagger UI.

## Generated Code (gencode_test/server/)

Folder `gencode_test/server/` được tạo bằng **OpenAPI Generator CLI**:

```bash
openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./server
```

### Cấu trúc generated code:

- `openapi_server/` - Generated Flask controllers và models
- `test/` - Unit tests tự động sinh
- `setup.py` - Package setup
- `Dockerfile` - Container config
- `requirements.txt` - Dependencies cho generated server

### Lưu ý:
- Generated code là boilerplate đầy đủ nhất
- File `main.py` ở root là custom implementation tối ưu hơn
- Dùng `main.py` để deploy lên Vercel

## Deployment trên Vercel

**vercel.json** cấu hình:
- Build: Compiles Python runtime
- Routes: Tất cả request → `main.py`

Deploy:
```bash
vercel --prod
```

Hoặc tạo preview:
```bash
vercel
```

## Test API

### Local
```bash
# Terminal 1: Chạy app
python main.py

# Terminal 2: Test
curl http://localhost:5000/api/books
```

### Production
```bash
curl https://week4-smoky.vercel.app/api/books
```

### Swagger UI
- Local: http://localhost:5000/docs
- Production: https://week4-smoky.vercel.app/docs
