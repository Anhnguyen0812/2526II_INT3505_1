# Buổi 11-12: API Design Patterns

## Mục tiêu

- Hiểu các mẫu thiết kế API phổ biến: CRUD, Query, HATEOAS, Event-driven, Webhook.
- Biết khi nào dùng REST, khi nào dùng gRPC hoặc GraphQL.
- Thiết kế API kết hợp nhiều patterns trong một hệ thống.
- Triển khai webhook để tích hợp hệ thống bên ngoài.

## Tổng quan nội dung

Buổi này gồm 2 phần: (1) lý thuyết các mẫu thiết kế và tiêu chí chọn công nghệ, (2) thực hành một API mẫu có CRUD + Query + HATEOAS + Webhook.

Code mẫu ở [week11-12/main.py](week11-12/main.py).

## 1) Các mẫu thiết kế API

### CRUD Pattern

- Cung cấp 4 thao tác cơ bản: Create, Read, Update, Delete.
- Ví dụ: `POST /articles`, `GET /articles/{id}`, `PUT /articles/{id}`, `DELETE /articles/{id}`.
- Phù hợp cho tài nguyên rõ ràng và vòng đời đơn giản.

### Query Pattern

- Cho phép tìm kiếm, lọc, phân trang bằng query params.
- Ví dụ: `GET /articles?status=published&q=design&page=1&limit=10`.
- Cần đặt quy ước chuẩn cho filter, sort, pagination để API nhất quán.

### HATEOAS Pattern

- Trả về liên kết (links) trong response giúp client biết bước tiếp theo.
- Ví dụ trong response của `GET /articles` sẽ có `self`, `update`, `delete`, `list`.
- Lợi ích: giảm phụ thuộc vào tài liệu tĩnh, API tự mô tả.

### Event-driven Pattern

- API phát sự kiện khi dữ liệu thay đổi (create/update/delete).
- Giúp các hệ thống khác phản ứng theo thời gian thực.
- Webhook là một cách phổ biến để truyền sự kiện ra ngoài.

### Webhook Pattern

- Một hệ thống gửi HTTP request đến hệ thống khác khi có sự kiện.
- Ví dụ: `article.created` gửi tới các subscriber đã đăng ký.
- Cần xác thực chữ ký, retry, và idempotency.

## 2) Khi nào dùng REST, gRPC, GraphQL

- REST: phù hợp cho hệ thống mở, client đa dạng, dễ cache, dễ debug.
- gRPC: phù hợp microservices nội bộ, hiệu năng cao, schema chặt chẽ.
- GraphQL: phù hợp khi client cần linh hoạt dữ liệu, giảm số lượng request.

Nguyên tắc chọn:

- Hệ thống public API: ưu tiên REST.
- Hệ thống nội bộ: cân nhắc gRPC.
- Nhiều client cần data khác nhau: cân nhắc GraphQL.

## 3) Thực hành API mẫu

### Cấu trúc endpoint chính

- `GET /health`
- `GET /articles` (Query + HATEOAS)
- `POST /articles` (CRUD)
- `GET /articles/{id}`
- `PUT /articles/{id}`
- `DELETE /articles/{id}`
- `POST /webhooks/subscriptions`
- `GET /webhooks/subscriptions`
- `DELETE /webhooks/subscriptions/{id}`
- `POST /webhooks/receiver`

### Cơ chế Webhook Sender

- Khi tạo/cập nhật/xóa article, API sẽ gửi event.
- Payload gồm `id`, `type`, `created_at`, `data`.
- Header kèm `X-Webhook-Id`, `X-Webhook-Timestamp`, `X-Webhook-Signature`.
- Retry 3 lần nếu lỗi.

### Cơ chế Webhook Receiver

- Kiểm tra chữ ký bằng shared secret.
- Dùng `X-Webhook-Id` để tránh xử lý trùng (idempotency).

## 4) Cài đặt và chạy thử

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

Swagger UI: http://localhost:8000/apidocs/

### Ví dụ gọi API

Tạo bài viết:

```bash
curl -X POST http://localhost:8000/articles \
  -H "Content-Type: application/json" \
  -d '{"title": "Design Patterns", "status": "published"}'
```

Đăng ký webhook:

```bash
curl -X POST http://localhost:8000/webhooks/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:8000/webhooks/receiver", "events": ["article.created"]}'
```

## 5) Checklist thiết kế API

- Đặt tên resource theo danh từ số nhiều.
- Dùng HTTP verbs đúng ngữ nghĩa.
- Trả mã lỗi phù hợp (`400`, `404`, `409`, `422`).
- Hỗ trợ filter, sort, pagination nhất quán.
- Trả metadata và links khi cần (HATEOAS).
- Bảo mật webhook bằng chữ ký + idempotency.

## 6) Phân tích API Stripe, GitHub

### Stripe

- Dùng REST API, resource rõ ràng (`/customers`, `/charges`).
- Webhook events giàu metadata, hỗ trợ retry, chữ ký.
- Có idempotency key cho các request write.

### GitHub

- REST API phổ biến, có GraphQL API cho truy vấn linh hoạt.
- Webhook events cho repo, issue, pull request.
- HATEOAS có xuất hiện trong link header ở một số endpoint.

## 7) Câu hỏi ôn tập + gợi ý trả lời

1. Khi nào nên dùng Query pattern thay vì tạo endpoint mới?
   - Khi chỉ cần lọc/tìm kiếm trên cùng resource.
2. HATEOAS giúp ích gì cho client?
   - Client tự khám phá hành động tiếp theo mà không hard-code URL.
3. Vì sao webhook cần chữ ký?
   - Đảm bảo request đến từ nguồn tin cậy, chống giả mạo.
4. Khi nào nên dùng GraphQL?
   - Khi client cần dữ liệu linh hoạt và tránh over-fetch/under-fetch.
