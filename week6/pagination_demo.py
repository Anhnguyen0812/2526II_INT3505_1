import sqlite3
import time

def setup_db():
    # Tạo database in-memory để demo nhanh
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Tạo bảng
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    ''')
    
    # Đánh index cho ID (Primary Key mặc định đã có index, nhưng ghi rõ để hiểu bản chất Cursor)
    cursor.execute('CREATE INDEX idx_users_id ON users(id)')
    
    print("Đang chèn 1.000.000 bản ghi vào database (in-memory)... Vui lòng đợi vài giây...")
    # Chèn dữ liệu theo batch cho nhanh
    batch_size = 100000
    for i in range(10):
        records = [(f"User {j}", f"user{j}@example.com") for j in range(i * batch_size, (i + 1) * batch_size)]
        cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", records)
    conn.commit()
    print("Hoàn tất chèn 1M bản ghi!\n")
    return conn

def test_app_level_pagination(conn, offset, limit=10):
    """
    Chiến lược 1: Fetch All (Lấy tất cả rồi cắt mảng ở App level)
    Rất tệ: Tốn RAM, tốn băng thông mạng và CPU.
    """
    cursor = conn.cursor()
    start = time.perf_counter()
    
    cursor.execute("SELECT * FROM users")  # Lấy toàn bộ dữ liệu
    results = cursor.fetchall()
    page = results[offset : offset+limit]  # Phân trang bằng list slicing ở code
    
    end = time.perf_counter()
    return end - start

def test_offset_pagination(conn, offset, limit=10):
    """
    Chiến lược 2: Offset-based (Sử dụng LIMIT ... OFFSET ...)
    Vấn đề: DB phải duyệt qua 'offset' bản ghi trước khi lấy 'limit' bản ghi.
    Càng vào trang sâu (offset lớn), truy vấn càng chậm.
    """
    cursor = conn.cursor()
    start = time.perf_counter()
    
    cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (limit, offset))
    results = cursor.fetchall()
    
    end = time.perf_counter()
    return end - start

def test_cursor_pagination(conn, last_id, limit=10):
    """
    Chiến lược 3: Cursor-based (Sử dụng WHERE id > cursor LIMIT ...)
    Ưu điểm: Tận dụng Index của cột ID (B-Tree). DB nhảy thẳng đến vị trí last_id và lấy tiếp 'limit' bản ghi.
    Thời gian truy vấn gần như không đổi dù ở trang nào O(1).
    """
    cursor = conn.cursor()
    start = time.perf_counter()
    
    cursor.execute("SELECT * FROM users WHERE id > ? ORDER BY id ASC LIMIT ?", (last_id, limit))
    results = cursor.fetchall()
    
    end = time.perf_counter()
    return end - start

def run_benchmark():
    conn = setup_db()
    
    # Các mốc vị trí trang cần test (từ trang đầu đến trang cuối)
    positions = [0, 10_000, 100_000, 500_000, 900_000, 999_900]
    limit = 10
    
    print("= SO SÁNH THỜI GIAN THỰC THI (Giây) VỚI LIMIT = 10 =")
    print(f"{'Vị trí (Offset/Last ID)':<25} | {'App-Level (s)':<15} | {'Offset (s)':<15} | {'Cursor (s)':<15}")
    print("-" * 80)
    
    for pos in positions:
        time_app = test_app_level_pagination(conn, pos, limit)
        time_offset = test_offset_pagination(conn, pos, limit)
        time_cursor = test_cursor_pagination(conn, pos, limit)
        
        print(f"{pos:<25} | {time_app:<15.6f} | {time_offset:<15.6f} | {time_cursor:<15.6f}")

    print("\nNhận xét:")
    print("- App-Level: Luôn mất nhiều thời gian nhất do phải load 1M bản ghi vào memory trước khi cắt.")
    print("- Offset: Thời gian tăng tuyến tính theo số thứ tự trang. Càng về cuối càng chậm vì DB phải quét qua các bản ghi trước đó.")
    print("- Cursor: Nhanh ổn định (~0.000...s) ở mọi vị trí do nhảy trực tiếp bằng Index B-Tree.")

if __name__ == "__main__":
    run_benchmark()