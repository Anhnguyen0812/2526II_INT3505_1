# Buổi 10: Service Operation - Security & Monitoring

## Mục tiêu

- Deploy API lên môi trường production
- Thiết lập monitoring (logs, metrics, tracing), rate limiting, circuit breaker
- Thiết lập hệ thống quan sát (observability) cho API
- Đảm bảo bảo mật production (WAF, rate limiting, audit logs)

## Tổng quan bài học

3 trụ cột vận hành dịch vụ:

1. Observability: log, metrics, tracing để hiểu hệ thống đang hoạt động thế nào.
2. Security: bảo vệ API trong production (WAF, rate limit, audit log, API key).
3. Reliability: giảm sự cố lan truyền (circuit breaker, retry có kiểm soát).

Trong thực hành, chúng ta xây dựng một API Flask có Swagger UI, ghi log, xuất metrics Prometheus, và áp rate limit cho endpoint. Code mẫu ở [week10/main.py](week10/main.py).

## Nội dung thực hành

- Logging + monitoring cơ bản (Prometheus)
- Rate limit cho endpoint
- API key cho endpoint nhạy cảm
- Deploy lên Vercel với Flask + Swagger UI

## Cấu trúc endpoint

- `GET /health`: kiểm tra sống còn, giới hạn 120 req/phút.
- `GET /items`: dữ liệu demo, giới hạn 10 req/phút.
- `POST /items`: tạo item demo, giới hạn 5 req/phút, hỗ trợ API key.
- `GET /metrics`: xuất metrics Prometheus.

## Chuẩn bị môi trường

- Python 3.10+ (khuyến nghị 3.11)
- Tạo virtualenv và cài dependency

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Chạy local

```bash
python main.py
```

Mở trình duyệt:

- Swagger UI: http://localhost:8000/apidocs/
- Health: http://localhost:8000/health
- Items: http://localhost:8000/items
- Metrics: http://localhost:8000/metrics

## Ví dụ gọi API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/items
```

Gọi `POST /items`:

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "gamma"}'
```

Nếu bật API key:

```bash
export API_KEY="demo-secret"
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-secret" \
  -d '{"name": "delta"}'
```

## Giải thích chi tiết theo nội dung

### 1) Logging và Audit Log

- Mục tiêu: biết ai gọi, gọi khi nào, mất bao lâu, kết quả ra sao.
- Trường log quan trọng: `request_id`, method, path, status, latency, ip, user_agent.
- Lợi ích: truy vết lỗi, hỗ trợ điều tra sự cố, đối soát audit.

Ví dụ log:

```
2026-05-14 10:00:00 INFO week10-service request_id=abc123 request completed method=GET path=/items status=200 latency=0.0123 ip=127.0.0.1 ua=curl/8.4.0
```

### 2) Metrics (Prometheus)

- `http_requests_total`: tổng số request theo method, path, status.
- `http_request_duration_seconds`: histogram độ trễ theo method, path.
- `auth_failures_total`: số lần fail API key.
- `rate_limit_hits_total`: số lần bị rate limit.

Prometheus sẽ scrape tại `GET /metrics`.

### 3) Rate Limiting

- Mục tiêu: chống abuse, giảm nguy cơ DDoS nhẹ, bảo vệ tài nguyên.
- Cấu hình trong code: giới hạn mặc định 60 req/phút, endpoint riêng có ngưỡng khác.
- Production nên dùng Redis để lưu rate limit state thay vì memory.

### 4) API Key cơ bản

- Cơ chế: so sánh `X-API-Key` với biến môi trường `API_KEY`.
- Mục tiêu học: hiểu cách bảo vệ endpoint nhạy cảm.
- Production cần cơ chế xác thực mạnh hơn (JWT/OAuth2) và rotation khóa.

### 5) Observability tổng thể

- Logs: phục vụ điều tra sự cố.
- Metrics: theo dõi sức khỏe, thiết lập alert.
- Tracing: giúp nhìn thấy luồng request xuyên dịch vụ (OpenTelemetry).

### 6) Circuit Breaker (khái niệm)

- Dùng khi gọi service bên ngoài có thể lỗi/timeout.
- Khi lỗi vượt ngưỡng, tạm ngừng gọi để bảo vệ hệ thống.
- Có thể dùng gateway hoặc thư viện (ví dụ: pybreaker) ở tầng app.

## Biến môi trường

- `PORT`: cổng chạy server (mặc định 8000).
- `LOG_LEVEL`: mức log (INFO, DEBUG, ...).
- `API_KEY`: bật bảo vệ cho `POST /items` nếu có giá trị.
- `RATE_LIMIT_STORAGE_URI`: nơi lưu rate limit state, mặc định `memory://`.

## Deploy lên Vercel (Flask + Swagger)

1. Kiểm tra có [week10/requirements.txt](week10/requirements.txt).
2. (Tùy chọn) Tạo file `vercel.json` tại week10:

```json
{
  "version": 2,
  "builds": [{ "src": "main.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "main.py" }]
}
```

3. Chạy `vercel` trong folder week10 và deploy.
4. Sau khi deploy: Swagger UI ở `/apidocs/`, metrics ở `/metrics`.

## Câu hỏi ôn tập

- Rate limit nên đặt ở gateway hay ở service? Vì sao?
- Log nào là quan trọng nhất để điều tra sự cố?
- Khi nào cần bật circuit breaker cho endpoint?
- Metrics nào nên dùng để cảnh báo sớm (latency, error rate, throughput)?

## Gợi ý trả lời câu hỏi ôn tập

1. Rate limit nên đặt ở gateway và/hoặc service.

- Gateway giúp chặn sớm, giảm tải cho toàn hệ thống và áp dụng chính sách thống nhất.
- Service vẫn nên có rate limit để tự bảo vệ khi gateway bị bypass hoặc không đủ chi tiết.

2. Log quan trọng nhất để điều tra sự cố:

- `request_id` để liên kết mọi log liên quan.
- Method, path, status, latency để xác định điểm lỗi.
- IP, user_agent để truy vết nguồn gây lỗi hoặc hành vi bất thường.
- Error message/stacktrace cho lỗi 5xx.

3. Khi nào cần bật circuit breaker:

- Khi endpoint phụ thuộc dịch vụ bên ngoài hay bị timeout/5xx liên tục.
- Khi retry làm tăng tải và gây "thác lỗi" (failure cascade).
- Khi cần bảo vệ tài nguyên nội bộ để dịch vụ chính vẫn phản hồi.

4. Metrics dùng để cảnh báo sớm:

- Error rate tăng đột biến (tỷ lệ 5xx/4xx bất thường).
- Latency p95/p99 vượt ngưỡng (dịch vụ bắt đầu chậm).
- Throughput (RPS) giảm mạnh hoặc tăng bất thường.
