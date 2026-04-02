# Week 6 - Authentication va Authorization (Flask + Swagger)

## Muc tieu buoi hoc
Buoi hoc nay tap trung vao 2 chu de chinh:
- Authentication: xac thuc danh tinh nguoi dung bang JWT.
- Authorization: phan quyen truy cap bang scopes va roles.

Noi dung da duoc trien khai trong file [main.py](main.py).

## Kien thuc can dat
- Phan biet JWT va OAuth 2.0:
  - JWT la dinh dang token (self-contained claims).
  - OAuth 2.0 la framework uy quyen (delegated authorization).
  - OAuth 2.0 co the phat hanh access token dang JWT.
- Hieu cac khai niem:
  - Bearer token: token gui qua header Authorization.
  - Refresh token: token cap lai access token moi khi access token het han.
  - Scopes: quyen thao tac chi tiet theo endpoint/chuc nang.
  - Roles: vai tro nguoi dung (vi du user, admin).

## Tong quan file main.py
API duoc xay dung bang Flask, tai lieu API duoc public qua Swagger (flasgger).

Cac thanh phan chinh trong [main.py](main.py):
- Cau hinh JWT:
  - JWT_SECRET, JWT_ALGORITHM, thoi gian song access/refresh token.
- Ham cap va giai ma token:
  - issue_token(...)
  - decode_token(...)
- Middleware xac thuc + phan quyen:
  - auth_required(required_scopes, required_roles)
- Co che refresh token rotation:
  - Moi refresh token chi dung 1 lan, token cu bi vo hieu.
- Co che revoke access token:
  - Luu jti vao denylist khi logout.
- Endpoint security audit:
  - Bao cao rui ro token leakage va replay attack.

## Cac endpoint da co
- GET /: thong tin tong quan API.
- POST /auth/login: dang nhap, nhan access token + refresh token.
- POST /auth/refresh: cap token moi bang refresh token.
- POST /auth/logout: revoke access token hien tai.
- GET /users: can scope users:read.
- POST /users: can scope users:write va role admin.
- GET /security/audit: can scope audit:read va role admin.
- GET /auth/compare: tra ve so sanh JWT vs OAuth 2.0.

## Luong xac thuc va phan quyen
1. Client goi POST /auth/login voi username/password.
2. Server tra ve access token ngan han + refresh token dai han.
3. Client gui access token qua header:
   - Authorization: Bearer <access_token>
4. Middleware kiem tra:
   - token hop le, chua het han, dung loai access,
   - co du scope,
   - role hop le neu endpoint yeu cau.
5. Khi access token het han:
   - client goi POST /auth/refresh de lay cap token moi.

## Security audit (rui ro va khac phuc)
### 1. Token leakage
Rui ro:
- Log server vo tinh ghi Authorization header.
- Token bi luu o localStorage va bi lo qua XSS.
- Token bi gui qua URL/query string.

Khac phuc de xuat:
- Khong log token tho.
- Uu tien HttpOnly Secure cookie neu phu hop.
- Chi gui token trong Authorization header.
- Bat buoc HTTPS tren moi moi truong production.

### 2. Replay attack
Rui ro:
- Token bi danh cap co the bi dung lai den khi het han.

Khac phuc de xuat:
- Giam thoi gian song access token (5-15 phut).
- Dung refresh token rotation.
- Revoke token bang denylist khi nghi ngo session bi compromise.
- Theo doi bat thuong va thu hoi token som.

## Huong dan chay nhanh
Yeu cau:
- Python 3.9+
- Flask
- PyJWT
- flasgger

Cai thu vien:

```bash
pip install flask PyJWT flasgger
```

Chay API:

```bash
python main.py
```

Mo Swagger UI:
- http://127.0.0.1:5000/apidocs

## Tai khoan demo
Khai bao trong [main.py](main.py):
- user thuong:
  - username: alice
  - password: alice123
  - scopes: users:read
- admin:
  - username: admin
  - password: admin123
  - scopes: users:read, users:write, audit:read

## Ghi chu hoc tap
- Day la demo cho muc dich hoc Authentication/Authorization.
- Chua phai kien truc production day du (chua co DB, hash password, quan ly session phan tan, rate limit, v.v.).
- Khi dua vao production can bo sung:
  - Hash password (bcrypt/argon2)
  - Secret manager
  - Logging sanitize
  - TLS + CORS + CSRF policy phu hop
  - Monitoring va alert bao mat
