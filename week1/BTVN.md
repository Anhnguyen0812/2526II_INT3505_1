# Tuần 1: Giới thiệu về API và Web Services

**Bài tập về nhà**: Tìm và phân tích 3 API công khai 

# 1. Spotify Web API

## Mục đích

Spotify Web API cho phép các nhà phát triển lấy dữ liệu từ nội dung âm nhạc của Spotify và quản lý danh sách phát của người dùng:

- Lấy thông tin Album, Artist, Track
- Quản lý Playlist (Tạo, Thêm bài hát)
- Kiểm soát Player (Play, Pause, Next)
- Lấy thông tin User Profile và Follower

Được dùng để xây dựng:
- Ứng dụng nghe nhạc tùy chỉnh
- Công cụ phân tích xu hướng âm nhạc
- Bot Discord phát nhạc

---

## Ví dụ endpoint

### Lấy thông tin một Album

```
GET https://api.spotify.com/v1/albums/{id}
```

Ví dụ:

```
GET https://api.spotify.com/v1/albums/4aawyAB9vmq7uQrQ7Y9y7F
```

---

## Ví dụ Response

```json
{
  "album_type": "album",
  "artists": [
    {
      "name": "Bruno Mars",
      "type": "artist",
      "uri": "spotify:artist:0du5Z0ST9R70Ju8oqzbeG7"
    }
  ],
  "id": "4aawyAB9vmq7uQrQ7Y9y7F",
  "name": "24K Magic",
  "release_date": "2016-11-17",
  "total_tracks": 9,
  "type": "album"
}
```

---

## Authentication

Spotify hỗ trợ OAuth 2.0:

1. Authorization Code Flow (Cho user data)
2. Client Credentials Flow (Chỉ cho public data)

Header:
```
Authorization: Bearer <access_token>
```

---

## Rate Limit

Spotify sử dụng rate limit dựa trên số lượng request trong một khoảng thời gian ngắn. Nếu vượt quá, API trả về mã lỗi `429 Too Many Requests`.

Header trả về:
```
Retry-After: <seconds>
```

---

# 2. OpenStreetMap API (Nominatim)

## Mục đích

OpenStreetMap (OSM) là một bản đồ thế giới miễn phí và có thể chỉnh sửa. API Nominatim của nó được dùng để:

- Geocoding (Chuyển địa chỉ thành tọa độ)
- Reverse Geocoding (Chuyển tọa độ thành địa chỉ)
- Tìm kiếm địa điểm theo tên

Ứng dụng:
- Tìm kiếm vị trí trên bản đồ mã nguồn mở
- Tự động điền địa chỉ trong form
- Lưu trữ dữ liệu vị trí không tốn phí bản quyền

---

## Ví dụ endpoint

### Search địa danh

```
GET https://nominatim.openstreetmap.org/search
```

Query parameters:
```
?q=Hanoi
&format=json
&addressdetails=1
```

---

## Ví dụ Request

```
GET https://nominatim.openstreetmap.org/search?q=Hanoi&format=json
```

---

## Response

```json
[
  {
    "place_id": 259685164,
    "licence": "Data © OpenStreetMap contributors, ODbL 1.0.",
    "lat": "21.0283334",
    "lon": "105.854041",
    "display_name": "Hồ Hoàn Kiếm, Tràng Tiền, Hoàn Kiếm, Hà Nội, 100000, Việt Nam",
    "type": "attraction",
    "importance": 0.8
  }
]
```

---

## Authentication

**Không yêu cầu API Key**.

Tuy nhiên, cần phải cung cấp `User-Agent` hợp lệ trong header để nhận diện ứng dụng và tuân thủ [Usage Policy](https://operations.osmfoundation.org/policies/nominatim/).

---

## Rate Limit

Quy định chung:
- Tối đa **1 request/giây**.
- Không được phép "heavy usage" (cào dữ liệu số lượng lớn).

---

## REST Design

| REST Principle | Implementation |
| --- | --- |
| Resource | `/search`, `/reverse` |
| Method | GET |
| Query params | q, format, lat, lon |
| Format | JSON, XML, HTML |

---

# 3. JSONPlaceholder API

## Mục đích

Là một REST API giả, phổ biến dành cho các nhà phát triển để test và prototyping:

- Cung cấp dữ liệu mẫu: Posts, Comments, Albums, Photos, Todos, Users
- Hỗ trợ đầy đủ các phương thức HTTP (GET, POST, PUT, PATCH, DELETE)

Ứng dụng:
- Học cách gọi API trong Frontend (React, Vue, v.v.)
- Test giao diện khi chưa có Backend thực sự
- Làm ví dụ minh họa trong tài liệu hướng dẫn

---

## Ví dụ endpoint

### Lấy danh sách bài viết

```
GET https://jsonplaceholder.typicode.com/posts
```

---

## Request (Tạo bài viết mới)

```
POST https://jsonplaceholder.typicode.com/posts
```

Body:
```json
{
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

---

## Response

```json
{
  "id": 101,
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

---

## Authentication

**Không yêu cầu Authentication**. Bất kỳ ai cũng có thể truy cập ngay lập tức.

---

## Rate Limit

Không giới hạn cụ thể cho mục đích test, nhưng dữ liệu tạo mới qua POST/PUT sẽ không thực sự được lưu vào database (chỉ giả lập trả về response thành công).

---

## REST Design

| Feature | Implementation |
| --- | --- |
| Resource | `/posts`, `/users`, `/todos` |
| HTTP methods | Đầy đủ RESTful |
| Stateless | Có |
| Format | JSON |
