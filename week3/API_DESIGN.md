# Kiến thức cơ bản về Thiết kế API (RESTful)
**Nhất quán (Consistency), Dễ hiểu (Clarity) và Dễ mở rộng (Extensibility).**

## 1. Naming Conventions (Quy tắc đặt tên)

*   **Sử dụng danh từ số nhiều (Plural Nouns):** Luôn sử dụng `/users`, `/products`, `/orders` thay vì `/user`, `/product`, `/order`. Điều này thể hiện đây là một tập hợp (collection) các tài nguyên.
*   **Chữ thường và gạch nối (Lowercase & Hyphens):** Tên endpoint nên viết thường hoàn toàn. Nếu có nhiều từ, hãy dùng dấu gạch nối (ví dụ: `/order-items` thay vì `/orderItems`).
*   **Phân tầng tài nguyên (Resource Hierarchy):** Thể hiện mối quan hệ cha-con qua cấu trúc đường dẫn.
    *   Ví dụ: `/users/1/orders` (Các đơn hàng của người dùng số 1).
*   **Không bao giờ bao gồm động từ trong URI:**
    *   SAI: `/get-users`, `/create-order`
    *   ĐÚNG:
        *   `GET /users` (Lấy danh sách)
        *   `POST /users` (Tạo mới)
        *   `PUT /users/1` (Cập nhật)
        *   `DELETE /users/1` (Xóa)

## 2. API Versioning (Quản lý phiên bản)

*   Luôn bắt đầu API với số phiên bản để đảm bảo tính tương thích ngược khi hệ thống phát triển.
*   Ví dụ: `/api/v1/products`, `/api/v2/products`.

## 3. Best Practices (Quy tắc vàng)

1.  **Tính nhất quán:** Nếu bạn dùng `/api/v1/` cho users, hãy dùng tương tự cho products. Đừng trộn lẫn các kiểu đặt tên.
2.  **Dễ hiểu:** Người dùng API chỉ cần nhìn vào URL và Phương thức HTTP (GET, POST, PUT, DELETE) là hiểu được chức năng.
3.  **Lọc dữ liệu:** Sử dụng `query parameters` cho việc lọc hoặc tìm kiếm.
    *   Ví dụ: `/products?category=electronics` thay vì `/products/electronics`.