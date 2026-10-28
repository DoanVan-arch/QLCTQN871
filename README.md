# Hệ thống Quản lý Chính trị Quân nhân - Đoàn 871

Website quản lý chính trị quân nhân xây dựng bằng **Python Flask**, dùng cho công tác quản lý hồ sơ học viên, quân số khung và hồ sơ lưu trữ của đơn vị.

## 1. Tính năng chính

### Đăng nhập & phân quyền tài khoản
- **Admin**: Toàn quyền — quản lý tài khoản (thêm/sửa/xóa/khóa), thêm/sửa/xóa dữ liệu nhân sự.
- **Mod**: Chỉ được thêm/sửa/xóa dữ liệu nhân sự, **không** được quản lý tài khoản.
- **Viewer**: Chỉ xem dữ liệu, tìm kiếm, thống kê — không có quyền chỉnh sửa.

### 5 mục quản lý
1. Quản lý học viên trong nước
2. Quản lý học viên ngoài nước
3. Quản lý quân số khung
4. Quản lý hồ sơ lưu
5. Thống kê (tìm kiếm, lọc, sắp xếp toàn bộ dữ liệu)

### Các trường dữ liệu quản lý
Họ và tên, tôn giáo, dân tộc, giới tính, ngày sinh, ngày nhập ngũ, cấp bậc, TG nhận cấp bậc, chức vụ, TG nhận chức vụ, TG vào Đoàn, chi đoàn, đã học lớp cảm tình Đảng (có/không), TG vào Đảng (dự bị), chi bộ, TG chính thức, đơn vị trước khi nhập học, nơi ở, trú quán, quê quán, tên trường theo học, chuyên ngành, bậc học, TG nhập học, TG tiếp nhận, TG tốt nghiệp, khen thưởng, kỷ luật, số CCCD, CMSQ, SĐT, người báo tin.

### Dashboard (trang chủ)
Hiển thị nhanh: tổng số hồ sơ theo từng danh mục, số đảng viên, đảng viên chính thức, đảng viên dự bị, đoàn viên, biểu đồ phân bố theo cấp bậc/giới tính, và danh sách cảnh báo thăng quân hàm / chuyển Đảng chính thức.

### Trang Thống kê
Thống kê chi tiết theo danh mục, cấp bậc, giới tính, tôn giáo, dân tộc, bậc học; kèm bảng tìm kiếm/lọc/sắp xếp nâng cao trên toàn bộ nhân sự (tất cả các mục), có thể lọc theo trạng thái "sắp đến hạn / quá hạn" thăng quân hàm hoặc chuyển Đảng chính thức.

### Dự báo thăng quân hàm & chuyển Đảng chính thức
Thời hạn xét thăng quân hàm áp dụng:

| Từ cấp bậc | Lên cấp bậc | Số năm |
|---|---|---|
| Thiếu úy | Trung úy | 2 năm |
| Trung úy | Thượng úy | 3 năm |
| Thượng úy | Đại úy | 3 năm |
| Đại úy | Thiếu tá | 4 năm |
| Thiếu tá | Trung tá | 4 năm |
| Trung tá | Thượng tá | 4 năm |
| Thượng tá | Đại tá | 4 năm |

Hệ thống tự tính thời điểm dự kiến thăng quân hàm tiếp theo = *TG nhận cấp bậc* + số năm quy định, và cảnh báo (🟠 sắp đến hạn trong năm / 🔴 quá hạn) ngay trên Dashboard và trang Thống kê.

Tương tự, Đảng viên dự bị sẽ được dự báo thời điểm chuyển chính thức = *TG vào Đảng* + 1 năm, kèm cảnh báo trước khi đến hạn.

## 2. Công nghệ sử dụng
- Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- SQLite (CSDL cục bộ, file tại `instance/qlctqn871.db`)
- Bootstrap 5 + Bootstrap Icons + Chart.js (giao diện & biểu đồ)

## 3. Cài đặt & chạy ứng dụng

```powershell
cd D:\Codes\QLCTQN871
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe run.py
```

Truy cập: http://127.0.0.1:5000

Lần chạy đầu tiên, hệ thống tự động tạo CSDL và tài khoản quản trị mặc định:

- **Tài khoản:** `admin`
- **Mật khẩu:** `admin123`

> ⚠️ Hãy đổi mật khẩu tài khoản admin ngay sau khi đăng nhập lần đầu (vào mục **Tài khoản** → sửa tài khoản `admin`).

## 4. Cấu trúc thư mục

```
QLCTQN871/
├── app/
│   ├── auth/          # Đăng nhập / đăng xuất
│   ├── users/         # Quản lý tài khoản (chỉ admin)
│   ├── personnel/     # CRUD 4 danh mục nhân sự + tìm kiếm/sắp xếp
│   ├── main/          # Dashboard
│   ├── stats/         # Trang Thống kê
│   ├── utils/         # Hằng số & logic dự báo thăng quân hàm/Đảng
│   ├── templates/
│   ├── static/
│   ├── models.py      # User, Personnel
│   ├── forms.py
│   └── decorators.py  # Phân quyền (roles_required, edit_required, admin_required)
├── instance/          # CSDL SQLite (tự sinh, không commit)
├── config.py
├── run.py
└── requirements.txt
```

## 5. Ghi chú
- Thống kê Đảng viên/Đoàn viên trên Dashboard được tính trên nhân sự **đang quản lý thực tế** (không tính mục "Hồ sơ lưu").
- Mọi thao tác thêm/sửa/xóa đều ghi nhận người tạo/người cập nhật cuối (`created_by`, `updated_by`).
