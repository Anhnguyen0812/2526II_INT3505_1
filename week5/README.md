# Tuần 5 - Thực Hành Thiết Kế API Thư Viện

## 1. Mục tiêu kiến thức cần đạt

### 1.1 Thiết kế cây tài nguyên phù hợp domain
Bạn cần biết cách mô hình API theo tài nguyên (resource) thay vì theo hành động (action).  
Ví dụ với domain thư viện:

- `/books`: danh sách sách
- `/books/{book_id}`: chi tiết một sách
- `/members`: danh sách thành viên
- `/members/{member_id}`: thông tin một thành viên
- `/members/{member_id}/loans`: danh sách phiếu mượn của một thành viên
- `/members/{member_id}/loans/{loan_id}`: chi tiết một phiếu mượn của thành viên đó

Ý tưởng chính: quan hệ cha-con được thể hiện rõ qua URL, tương tự ví dụ `/users/{id}/orders`.

### 1.2 Hiểu các chiến lược phân trang
Bạn cần nắm được 3 chiến lược phổ biến:

1. `offset/limit`
2. `page-based`
3. `cursor`

## 2. So sánh ưu/nhược điểm các kiểu phân trang

### 2.1 Offset/Limit
**Định nghĩa:** dùng `offset` để bỏ qua bao nhiêu bản ghi đầu, và `limit` để lấy bao nhiêu bản ghi tiếp theo.

Ví dụ:
- `GET /books/search/offset?q=harry&offset=0&limit=5`

**Ưu điểm:**
- Đơn giản, dễ hiểu, dễ triển khai.
- Phù hợp cho tập dữ liệu nhỏ-vừa.

**Nhược điểm:**
- Chậm dần khi `offset` lớn (DB phải scan và bỏ qua nhiều dòng).
- Có thể bị trùng/lạc bản ghi nếu dữ liệu thay đổi liên tục giữa các lần truy vấn.

### 2.2 Page-based
**Định nghĩa:** dùng `page` và `per_page`.

Ví dụ:
- `GET /books/search/page?q=harry&page=2&per_page=5`

**Ưu điểm:**
- Thân thiện với UI (trang 1, trang 2, ...).
- Dễ trình bày tổng số trang cho người dùng.

**Nhược điểm:**
- Bản chất vẫn thường dựa trên offset, nên vẫn gặp vấn đề hiệu năng khi trang sau rất lớn.
- Dễ sai lệch nếu dữ liệu cập nhật liên tục.

### 2.3 Cursor
**Định nghĩa:** thay vì nhảy theo vị trí, ta nhảy theo mốc dữ liệu cuối cùng đã xem (`cursor`).  
Trong bài này cursor được mô phỏng bằng `book_id` cuối cùng.

Ví dụ:
- `GET /books/search/cursor?q=harry&cursor=4&limit=3`

**Ưu điểm:**
- Hiệu năng tốt hơn với tập dữ liệu lớn.
- Ổn định hơn khi dữ liệu thay đổi trong lúc phân trang (ít trùng/lạc).

**Nhược điểm:**
- Phức tạp hơn cho frontend.
- Không trực quan theo kiểu "nhảy tới trang 10".

## 3. Kỹ năng cần làm được

Sau bài này, bạn cần làm được:

1. Thiết kế data model cho domain cụ thể (thư viện).
2. Xác định và mô hình quan hệ giữa các tài nguyên:
   - Author 1-n Book
   - Category 1-n Book
   - Member 1-n Loan
   - Book 1-n Loan
3. Thiết kế endpoint tìm kiếm kết hợp phân trang.
4. Chọn chiến lược phân trang phù hợp theo bài toán:
   - Dashboard nhỏ: offset/page
   - Infinite scroll, feed lớn: cursor

## 4. Phần thực hành đã code trong main.py

File [week5/main.py](main.py) đã bao gồm:

- Data model bằng `@dataclass`:
  - `Author`
  - `Category`
  - `Book`
  - `Member`
  - `Loan`
- Dữ liệu mẫu in-memory để test nhanh.
- Endpoint nested resource:
  - `GET /members/<member_id>/loans`
  - `POST /members/<member_id>/loans`
- Endpoint tìm kiếm + phân trang:
  - `GET /books/search/offset`
  - `GET /books/search/page`
  - `GET /books/search/cursor`
- Endpoint benchmark so sánh tốc độ phân trang:
  - `GET /benchmarks/pagination`
  - `GET /benchmarks/pagination/segment`

## 5. Hướng dẫn chạy

### 5.1 Cài đặt
Từ thư mục `week5`:

```bash
pip install flask
```

### 5.2 Chạy server

```bash
python main.py
```

Mặc định server chạy tại:
- `http://127.0.0.1:8000`

## 6. Các request mẫu để test

### 6.1 Kiểm tra health

```bash
curl "http://127.0.0.1:8000/health"
```

### 6.2 Lấy danh sách sách

```bash
curl "http://127.0.0.1:8000/books"
```

### 6.3 Tìm kiếm + offset/limit

```bash
curl "http://127.0.0.1:8000/books/search/offset?q=harry&offset=0&limit=2"
```

### 6.4 Tìm kiếm + page-based

```bash
curl "http://127.0.0.1:8000/books/search/page?q=harry&page=1&per_page=2"
```

### 6.5 Tìm kiếm + cursor

Lần 1:

```bash
curl "http://127.0.0.1:8000/books/search/cursor?q=harry&limit=2"
```

Lấy `next_cursor` từ response, sau đó gọi tiếp:

```bash
curl "http://127.0.0.1:8000/books/search/cursor?q=harry&cursor=5&limit=2"
```

### 6.6 Xem danh sách loan của member

```bash
curl "http://127.0.0.1:8000/members/1/loans"
```

### 6.7 Tạo loan mới

```bash
curl -X POST "http://127.0.0.1:8000/members/1/loans" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 6, "due_date": "2026-04-10"}'
```

### 6.8 Benchmark tổng quan 1M bản ghi

```bash
curl "http://127.0.0.1:8000/benchmarks/pagination?total_records=1000000&limit=20&runs=5"
```

Response trả về 3 phần:
- `config`: cấu hình benchmark (`total_records`, `limit`, `runs_per_position`).
- `results`: kết quả tại nhiều vị trí khác nhau (đầu, giữa, cuối dữ liệu).
- `summary`: trung bình thời gian của 3 chiến lược.

Ý nghĩa các trường quan trọng trong `results`:
- `offset_ms`, `page_ms`, `cursor_ms`: thời gian trung bình (milliseconds).
- `offset_vs_cursor_ratio`: offset chậm hơn cursor bao nhiêu lần.
- `page_vs_cursor_ratio`: page chậm hơn cursor bao nhiêu lần.

### 6.9 Benchmark tại một đoạn dữ liệu bất kỳ

```bash
curl "http://127.0.0.1:8000/benchmarks/pagination/segment?position=700000&limit=20&total_records=1000000&runs=5"
```

Tham số:
- `position`: vị trí bắt đầu (0-based).
- `limit`: số bản ghi cần lấy.
- `total_records`: tổng số bản ghi mô phỏng.
- `runs`: số lần chạy để lấy trung bình.

Endpoint này hữu ích khi muốn so sánh tốc độ tại 1 điểm cụ thể (ví dụ gần cuối dữ liệu) thay vì nhìn tổng quan nhiều mốc.

### 6.10 Kết quả benchmark mẫu (đã đo)

Với cấu hình:
- `total_records = 1,000,000`
- `limit = 20`
- `runs_per_position = 5`

Kết quả trung bình:
- `avg_cursor_ms = 0.0033`
- `avg_offset_ms = 6.2539`
- `avg_page_ms = 5.9007`

Một số mốc tiêu biểu:

| Vị trí | Offset (ms) | Page (ms) | Cursor (ms) | Offset/Cursor | Page/Cursor |
|---|---:|---:|---:|---:|---:|
| 0 | 0.0076 | 0.0032 | 0.0029 | 2.62x | 1.10x |
| 10,000 | 0.1993 | 0.1953 | 0.0021 | 94.90x | 93.00x |
| 100,000 | 1.5329 | 1.6659 | 0.0038 | 403.39x | 438.39x |
| 500,000 | 9.3666 | 8.8015 | 0.0035 | 2676.17x | 2514.71x |
| 900,000 | 15.1984 | 15.1261 | 0.0038 | 3999.58x | 3980.55x |
| 999,980 | 17.4535 | 15.4943 | 0.0036 | 4848.19x | 4303.97x |

Nhận xét nhanh:
- Ở đầu tập dữ liệu, chênh lệch chưa lớn.
- Càng về cuối, offset/page chậm tăng mạnh.
- Cursor gần như ổn định ở mọi vị trí.

## 7. Giải thích vì sao tốc độ như vậy

Với dữ liệu lớn, bạn sẽ thấy xu hướng:

- `cursor_ms` gần như ổn định khi `position` tăng.
- `offset_ms` và `page_ms` tăng rõ rệt khi đi sâu vào dữ liệu.
- Tỷ lệ `offset_vs_cursor_ratio` và `page_vs_cursor_ratio` tăng mạnh ở cuối tập dữ liệu.

Lý do kỹ thuật:
- Với `offset/page`: hệ thống phải đi qua và bỏ qua nhiều bản ghi trước khi lấy được `limit` bản ghi cần trả về. Khi vị trí càng sâu, số bản ghi bị bỏ qua càng lớn nên thời gian tăng gần tuyến tính theo độ sâu trang.
- Với `cursor`: truy vấn dùng mốc cuối (`cursor`) để nhảy trực tiếp tới vùng dữ liệu kế tiếp rồi lấy `limit` bản ghi. Vì vậy chi phí xử lý gần như giữ ổn định giữa đầu và cuối tập dữ liệu.

Góc nhìn độ phức tạp (mô hình trực quan):
- `offset/page`: chi phí gần với `O(offset + limit)`.
- `cursor`: chi phí gần với `O(limit)` sau khi đã có mốc cursor phù hợp.

Kết luận thực tế:
- Dataset nhỏ hoặc chỉ xem vài trang đầu: `offset/page` vẫn dễ dùng.
- Dataset lớn, infinite scroll, feed liên tục: `cursor` phù hợp hơn về hiệu năng và độ ổn định.

## 8. Gợi ý trình bày khi báo cáo nhóm

1. Vẽ resource tree tổng quan của hệ thống.
2. Trình bày data model + quan hệ giữa các bảng/tài nguyên.
3. Demo 3 kiểu phân trang bằng endpoint đã code.
4. Nêu lý do chọn cursor cho hệ thống lớn (hiệu năng + độ ổn định).
5. Nêu trade-off: cursor khó "jump page" nhưng tốt cho infinite scroll.

## 9. Tiêu chí đánh giá kết quả thực hành

Bạn đạt yêu cầu nếu:

- Thiết kế API đúng hướng resource-oriented.
- Có endpoint tìm kiếm và phân trang hoạt động.
- Nhận biết rõ ưu/nhược điểm từng pagination strategy.
- Giải thích được khi nào dùng offset/page, khi nào dùng cursor.
