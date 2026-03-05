# Phân tích mã lỗi HTTP

Mã trạng thái phản hồi HTTP cho biết liệu một yêu cầu HTTP cụ thể đã được hoàn thành thành công hay chưa. Các phản hồi được nhóm thành năm lớp.

---

## 1. 2xx: Thành công (Success)

- **200 OK**: Yêu cầu đã thành công.
- **201 Created**: Yêu cầu đã thành công và kết quả là một tài nguyên mới đã được tạo ra. Thường dùng cho các yêu cầu `POST`.

---

## 2. 4xx: Lỗi phía Client (Client Error)

Đây là nhóm mã lỗi do phía người dùng hoặc ứng dụng client gây ra (sai URL, thiếu quyền truy cập...).

| Mã lỗi | Tên lỗi | Ý nghĩa & Phân tích | Tình huống thực tế |
| :--- | :--- | :--- | :--- |
| **400** | Bad Request | Yêu cầu không hợp lệ do cú pháp không chính xác. | Gửi JSON thiếu dấu ngoặc hoặc sai kiểu dữ liệu. |
| **401** | Unauthorized | Yêu cầu thiếu thông tin xác thực hoặc xác thực sai. | Quên gửi mang `Authorization` token hoặc token hết hạn. |
| **403** | Forbidden | Client không có quyền truy cập vào tài nguyên này. | Cố gắng xóa bài viết của một người dùng khác. |
| **404** | **Not Found** | Không tìm thấy tài nguyên được yêu cầu. | Nhập sai URL hoặc tìm kiếm ID không tồn tại. |
| **429** | **Too Many Requests** | Người dùng đã gửi quá nhiều yêu cầu trong một khoảng thời gian nhất định. | Khi vượt quá "Rate Limit" của API (như Spotify/GitHub). |

---

## 3. 5xx: Lỗi phía Server (Server Error)

Đây là nhóm mã lỗi do máy chủ API gặp sự cố (lỗi logic code, sập database...).

| Mã lỗi | Tên lỗi | Ý nghĩa & Phân tích | Tình huống thực tế |
| :--- | :--- | :--- | :--- |
| **500** | **Internal Server Error** | Một lỗi không xác định xảy ra trên Server. | Code bị lỗi "Null Pointer" hoặc logic xử lý bị treo. |
| **502** | Bad Gateway | Server nhận được phản hồi không hợp lệ từ server cấp trên. | Proxy server không kết nối được tới ứng dụng chính. |
| **503** | Service Unavailable | Server chưa sẵn sàng để xử lý yêu cầu (bảo trì/quá tải). | Hệ thống đang được cập nhật hoặc có quá nhiều User truy cập cùng lúc. |
| **504** | Gateway Timeout | Server không nhận được phản hồi kịp thời từ phía sau. | Database xử lý quá chậm khiến request bị treo quá lâu. |

---

## Cách xử lý lỗi trong lập trình

1. **Client-side**: Luôn kiểm tra status code trước khi xử lý dữ liệu. Sử dụng khối `try...catch` để bắt lỗi mạng.
2. **Server-side**: Trả về thông báo lỗi chi tiết trong body (ví dụ: `{"error": "User not found"}`) kèm theo mã HTTP phù hợp.
3. **Retry logic**: Đối với lỗi **429** hoặc **503**, có thể thiết kế cơ chế thử lại (Retry) sau một khoảng thời gian chờ.
