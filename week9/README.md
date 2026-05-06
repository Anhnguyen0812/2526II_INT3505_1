# Buổi 9 - API Versioning và Lifecycle Management

## Mục tiêu

- Hiểu 3 chiến lược versioning phổ biến: URL, header, query parameter.
- Biết xử lý breaking changes mà không làm gián đoạn tích hợp hiện có.
- Lập migration plan rõ ràng khi nâng cấp API.
- Viết thông báo deprecation cho developers.

## Kiến trúc demo

- `GET /api/v1/payments`: versioning bằng URL, có deprecation headers.
- `GET /api/v2/payments`: version mới, schema mới.
- `GET /api/payments`: versioning bằng header `X-API-Version` hoặc query param `?version=v1|v2`.
- `GET /api/lifecycle/migration-plan`: kế hoạch nâng cấp từ v1 sang v2.
- `GET /api/lifecycle/deprecation-notice`: thông báo deprecated cho developer.
- `GET /apidocs/`: Swagger UI cho toàn bộ API.

## Breaking changes trong case study thanh toán

- `amount` ở v1 là số tiền dạng decimal, còn v2 dùng `amount_minor` theo đơn vị nhỏ nhất.
- `source` ở v1 được đổi thành `payment_method` ở v2.
- Trạng thái xử lý được mô tả theo flow mới, do đó client cũ cần cập nhật mapping.

## Chiến lược lifecycle

1. Audit các client đang dùng v1.
2. Chạy song song v1 và v2 trong một khoảng thời gian.
3. Chuyển client mới sang v2.
4. Gửi deprecation notice và sunset headers cho v1.
5. Gỡ bỏ v1 sau ngày sunset.

## Chạy

```bash
pip install -r requirements.txt
python main.py
```

Mở trình duyệt tại:

- `http://localhost:5000/`
- `http://localhost:5000/apidocs/`

## Ví dụ gọi API

### Tạo payment v1

```bash
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{"amount":49.99,"currency":"USD","source":"card","customer_reference":"ORD-10001"}'
```

### Tạo payment v2

```bash
curl -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -d '{"amount_minor":4999,"currency":"USD","payment_method":"card","customer_reference":"ORD-10001"}'
```

### Đọc payment bằng header versioning

```bash
curl http://localhost:5000/api/payments -H "X-API-Version: v2"
```

### Đọc payment bằng query param

```bash
curl "http://localhost:5000/api/payments?version=v1"
```

## Ghi chú

- URL versioning dễ nhận biết và dễ document nhất.
- Header versioning phù hợp khi muốn giữ URL đẹp và linh hoạt rollout theo client.
- Query param versioning dễ test nhanh, nhưng nên dùng có chủ ý vì dễ bị bỏ qua nếu không kiểm soát chặt.
- Deprecation không chỉ là thông báo, mà còn cần có sunset date, migration guide và theo dõi traffic.
