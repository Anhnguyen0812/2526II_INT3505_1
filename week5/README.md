# Week 5 - Library API Design Practice

## 1. Muc tieu kien thuc can dat

### 1.1 Thiet ke resource tree phu hop domain
Ban can biet cach mo hinh API theo tai nguyen (resource) thay vi theo action.  
Vi du voi domain thu vien:

- `/books`: danh sach sach
- `/books/{book_id}`: chi tiet mot sach
- `/members`: danh sach thanh vien
- `/members/{member_id}`: thong tin mot thanh vien
- `/members/{member_id}/loans`: danh sach phieu muon cua mot thanh vien
- `/members/{member_id}/loans/{loan_id}`: chi tiet mot phieu muon cua thanh vien do

Y tuong chinh: quan he cha-con duoc the hien ro qua URL, tuong tu vi du `/users/{id}/orders`.

### 1.2 Hieu cac chien luoc pagination
Ban can nam duoc 3 chien luoc pho bien:

1. `offset/limit`
2. `page-based`
3. `cursor`

## 2. So sanh uu/nhuoc diem cac kieu pagination

### 2.1 Offset/Limit
**Dinh nghia:** dung `offset` de bo qua bao nhieu ban ghi dau, va `limit` de lay bao nhieu ban ghi tiep theo.

Vi du:
- `GET /books/search/offset?q=harry&offset=0&limit=5`

**Uu diem:**
- Don gian, de hieu, de trien khai.
- Phu hop cho dataset nho-vua.

**Nhuoc diem:**
- Cham dan khi `offset` lon (DB phai scan va bo qua nhieu dong).
- Co the bi trung/lac ban ghi neu du lieu thay doi lien tuc giua cac lan truy van.

### 2.2 Page-based
**Dinh nghia:** dung `page` va `per_page`.

Vi du:
- `GET /books/search/page?q=harry&page=2&per_page=5`

**Uu diem:**
- Than thien voi UI (trang 1, trang 2, ...).
- De trinh bay tong so trang cho nguoi dung.

**Nhuoc diem:**
- Ban chat van thuong dua tren offset, nen van gap van de hieu nang khi page sau rat lon.
- De sai lech neu du lieu cap nhat lien tuc.

### 2.3 Cursor
**Dinh nghia:** thay vi nhay theo vi tri, ta nhay theo moc du lieu cuoi cung da xem (`cursor`).  
Trong bai nay cursor duoc mo phong bang `book_id` cuoi cung.

Vi du:
- `GET /books/search/cursor?q=harry&cursor=4&limit=3`

**Uu diem:**
- Hieu nang tot hon voi dataset lon.
- On dinh hon khi du lieu thay doi trong luc phan trang (it trung/lac).

**Nhuoc diem:**
- Phuc tap hon cho frontend.
- Khong truyen thong theo kieu "nhay toi trang 10".

## 3. Ky nang can lam duoc

Sau bai nay, ban can lam duoc:

1. Thiet ke data model cho domain cu the (thu vien).
2. Xac dinh va mo hinh quan he giua cac tai nguyen:
   - Author 1-n Book
   - Category 1-n Book
   - Member 1-n Loan
   - Book 1-n Loan
3. Thiet ke endpoint tim kiem ket hop phan trang.
4. Chon chien luoc pagination phu hop theo bai toan:
   - Dashboard nho: offset/page
   - Infinite scroll, feed lon: cursor

## 4. Phan thuc hanh da code trong main.py

File [week5/main.py](main.py) da bao gom:

- Data model bang `@dataclass`:
  - `Author`
  - `Category`
  - `Book`
  - `Member`
  - `Loan`
- Du lieu mau in-memory de test nhanh.
- Endpoint nested resource:
  - `GET /members/<member_id>/loans`
  - `POST /members/<member_id>/loans`
- Endpoint tim kiem + phan trang:
  - `GET /books/search/offset`
  - `GET /books/search/page`
  - `GET /books/search/cursor`

## 5. Huong dan chay

### 5.1 Cai dat
Tu thu muc `week5`:

```bash
pip install flask
```

### 5.2 Chay server

```bash
python main.py
```

Mac dinh server chay tai:
- `http://127.0.0.1:8000`

## 6. Cac request mau de test

### 6.1 Kiem tra health

```bash
curl "http://127.0.0.1:8000/health"
```

### 6.2 Lay danh sach sach

```bash
curl "http://127.0.0.1:8000/books"
```

### 6.3 Tim kiem + offset/limit

```bash
curl "http://127.0.0.1:8000/books/search/offset?q=harry&offset=0&limit=2"
```

### 6.4 Tim kiem + page-based

```bash
curl "http://127.0.0.1:8000/books/search/page?q=harry&page=1&per_page=2"
```

### 6.5 Tim kiem + cursor

Lan 1:

```bash
curl "http://127.0.0.1:8000/books/search/cursor?q=harry&limit=2"
```

Lay `next_cursor` tu response, sau do goi tiep:

```bash
curl "http://127.0.0.1:8000/books/search/cursor?q=harry&cursor=5&limit=2"
```

### 6.6 Xem danh sach loan cua member

```bash
curl "http://127.0.0.1:8000/members/1/loans"
```

### 6.7 Tao loan moi

```bash
curl -X POST "http://127.0.0.1:8000/members/1/loans" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 6, "due_date": "2026-04-10"}'
```

## 7. Goi y trinh bay khi bao cao nhom

1. Ve resource tree tong quan cua he thong.
2. Trinh bay data model + quan he giua cac bang/tai nguyen.
3. Demo 3 kieu pagination bang endpoint da code.
4. Neu ly do chon cursor cho he thong lon (hieu nang + do on dinh).
5. Neu trade-off: cursor kho "jump page" nhung tot cho infinite scroll.

## 8. Tieu chi danh gia ket qua thuc hanh

Ban dat yeu cau neu:

- Thiet ke API dung huong resource-oriented.
- Co endpoint tim kiem va phan trang hoat dong.
- Nhan biet ro uu/nhuoc diem tung pagination strategy.
- Giai thich duoc khi nao dung offset/page, khi nao dung cursor.
