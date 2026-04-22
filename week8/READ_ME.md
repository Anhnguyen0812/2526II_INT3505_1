# Hướng dẫn Kiểm thử API (Week 8)

Tài liệu này hướng dẫn về các loại kiểm thử API, cách xây dựng bộ test tự động với Postman/Newman và đo lường hiệu năng.

## 1. Kiến thức cần đạt

### Các loại Test:
- **Unit Test (Kiểm thử đơn vị):** Kiểm tra từng hàm, phương thức nhỏ nhất trong code. (Ví dụ: test hàm tính thuế sản phẩm).
- **Integration Test (Kiểm thử tích hợp):** Kiểm tra sự tương tác giữa các thành phần/endpoint. (Ví dụ: Sau khi POST tạo mới, GET có thấy dữ liệu đó không).
- **Performance Test (Kiểm thử hiệu năng):** Đánh giá tốc độ xử lý, khả năng chịu tải của API.
  - *Response Time:* Thời gian phản hồi trung bình.
  - *Error Rate:* Tỷ lệ lỗi khi có nhiều request cùng lúc.

### Công cụ:
- **Postman:** GUI mạnh mẽ để gọi API và viết scripts kiểm thử (JavaScript).
- **Newman:** Công cụ dòng lệnh (CLI) để chạy bộ sưu tập Postman trong môi trường CI/CD.
- **Load Testing Tools:** Locust (Python), JMeter, K6, hoặc chính tab "Performance" trong Postman.

---

## 2. Thực hành

### Bước 1: Cài đặt môi trường
Đảm bảo bạn đã cài đặt Python và các thư viện cần thiết:
```bash
pip install flask
```

Cài đặt Newman (yêu cầu Node.js):
```bash
npm install -g newman
```

### Bước 2: Chạy API Flask
Khởi chạy ứng dụng server:
```bash
python app.py
```
Server sẽ chạy tại: `http://localhost:5000`

### Bước 3: Sử dụng Postman để Test
1. Mở Postman, chọn **Import** -> Chọn file `test_collection.json`.
2. Chạy thử từng request trong bộ sưu tập.
3. Xem tab **Tests** trong mỗi request để hiểu cách viết script kiểm tra (ví dụ: `pm.response.to.have.status(200)`).
4. Sử dụng **Collection Runner** để chạy toàn bộ suite cùng lúc.

### Bước 4: Chạy test tự động với Newman
Mở terminal tại thư mục `week8` và chạy lệnh:
```bash
newman run test_collection.json
```
Newman sẽ xuất ra một bảng báo cáo kết quả các bài test ngay trên terminal.

### Bước 5: Đo hiệu năng (Performance)
Trong Postman (phiên bản mới), bạn có thể:
1. Chọn Collection "Week 8 - API Testing Lab".
2. Chọn tab **Run**.
3. Chọn tab **Performance**.
4. Thiết lập số lượng Virtual Users (ví dụ: 20) và thời gian chạy (1 phút).
5. Nhấn **Run** để xem biểu đồ Response Time và Error Rate.

---

## 3. Kỹ năng bổ sung: Viết Test Script
Ví dụ kiểm tra cấu trúc JSON trả về:
```javascript
pm.test("Cấu trúc dữ liệu đúng", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData.name).to.be.a('string');
});
```
