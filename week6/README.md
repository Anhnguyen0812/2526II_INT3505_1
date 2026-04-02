# Week 6 - Authentication và Authorization (Flask + Swagger)

## Mục tiêu buổi học
Buổi học này tập trung vào 2 chủ đề chính:
- Authentication: xác thực danh tính người dùng bằng JWT.
- Authorization: phân quyền truy cập bằng scopes và roles.

Nội dung đã được triển khai trong file [main.py](main.py).

## Kiến thức cần đạt
- Phân biệt JWT và OAuth 2.0:
  - JWT là định dạng token (self-contained claims).
  - OAuth 2.0 là framework ủy quyền (delegated authorization).
  - OAuth 2.0 có thể phát hành access token dạng JWT.
- Hiểu các khái niệm:
  - Bearer token: token gửi qua header Authorization.
  - Refresh token: token cấp lại access token mới khi access token hết hạn.
  - Scopes: quyền thao tác chi tiết theo endpoint/chức năng.
  - Roles: vai trò người dùng (ví dụ user, admin).

## Tổng quan file main.py
API được xây dựng bằng Flask, tài liệu API được public qua Swagger (flasgger).

Các thành phần chính trong [main.py](main.py):
- Cấu hình JWT:
  - JWT_SECRET, JWT_ALGORITHM, thời gian sống access/refresh token.
- Hàm cấp và giải mã token:
  - issue_token(...)
  - decode_token(...)
- Middleware xác thực + phân quyền:
  - auth_required(required_scopes, required_roles)
- Cơ chế refresh token rotation:
  - Mỗi refresh token chỉ dùng 1 lần, token cũ bị vô hiệu.
- Cơ chế revoke access token:
  - Lưu jti vào denylist khi logout.
- Endpoint security audit:
  - Báo cáo rủi ro token leakage và replay attack.

## Các endpoint đã có
- GET /: thông tin tổng quan API.
- POST /auth/login: đăng nhập, nhận access token + refresh token.
- POST /auth/refresh: cấp token mới bằng refresh token.
- POST /auth/logout: revoke access token hiện tại.
- GET /users: cần scope users:read.
- POST /users: cần scope users:write và role admin.
- GET /security/audit: cần scope audit:read và role admin.
- GET /auth/compare: trả về so sánh JWT vs OAuth 2.0.

## Luồng xác thực và phân quyền
1. Client gọi POST /auth/login với username/password.
2. Server trả về access token ngắn hạn + refresh token dài hạn.
3. Client gửi access token qua header:
   - Authorization: Bearer <access_token>
4. Middleware kiểm tra:
   - token hợp lệ, chưa hết hạn, đúng loại access,
   - có đủ scope,
   - role hợp lệ nếu endpoint yêu cầu.
5. Khi access token hết hạn:
   - client gọi POST /auth/refresh để lấy cặp token mới.

## Security audit (rủi ro và khắc phục)
### 1. Token leakage (Lộ lọt token)
Rủi ro:
- Log server vô tình ghi Authorization header.
- Token bị lưu ở localStorage và bị lộ qua XSS.
- Token bị gửi qua URL/query string.

Khắc phục đề xuất:
- Không log token thô.
- Ưu tiên HttpOnly Secure cookie nếu phù hợp.
- Chỉ gửi token trong Authorization header.
- Bắt buộc HTTPS trên mọi môi trường production.

### 2. Replay attack (Tấn công phát lại)
Rủi ro:
- Token bị đánh cắp có thể bị dùng lại đến khi hết hạn.

Khắc phục đề xuất:
- Giảm thời gian sống access token (5-15 phút).
- Dùng refresh token rotation.
- Revoke token bằng denylist khi nghi ngờ session bị compromise.
- Theo dõi bất thường và thu hồi token sớm.

## Hướng dẫn chạy nhanh
Yêu cầu:
- Python 3.9+
- Flask
- PyJWT
- flasgger

Cài thư viện:

```bash
pip install flask PyJWT flasgger
```

Chạy API:

```bash
python main.py
```

Mở Swagger UI:
- http://127.0.0.1:5000/apidocs

## Tài khoản demo
Khai báo trong [main.py](main.py):
- user thường:
  - username: alice
  - password: alice123
  - scopes: users:read
- admin:
  - username: admin
  - password: admin123
  - scopes: users:read, users:write, audit:read

## Ghi chú học tập
- Đây là demo cho mục đích học Authentication/Authorization.
- Chưa phải kiến trúc production đầy đủ (chưa có DB, hash password, quản lý session phân tán, rate limit, v.v.).
- Khi đưa vào production cần bổ sung:
  - Hash password (bcrypt/argon2)
  - Secret manager
  - Logging sanitize
  - TLS + CORS + CSRF policy phù hợp
  - Monitoring và alert bảo mật
