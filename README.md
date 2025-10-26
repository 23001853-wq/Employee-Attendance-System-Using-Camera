### 🏷️ Tên nhóm
    Nhóm 28
### 📝 Tên dự án
    Hệ thống điểm danh nhân viên bằng camera
### 👥 Thành viên nhóm
| 👤 Họ và tên 🧑‍🎓  | 🆔 Mã sinh viên 🧾 | 🐙 Tên GitHub 🔗     |
|------------------|---------------------|---------------------|
| [Nguyễn Hữu Duy]      | [23001853]    | [23001853-wq]      |

# Hệ thống Điểm danh bằng Nhận diện Khuôn mặt

Dự án xây dựng hệ thống điểm danh tự động sử dụng camera và thuật toán nhận diện khuôn mặt (OpenCV LBPH), tích hợp với cơ sở dữ liệu SQL Server và giao diện quản lý bằng Streamlit.

---

## ✨ Tính năng chính

* **Quản lý nhân viên:** Thêm, xem, sửa, xóa thông tin nhân viên qua giao diện web.
* **Thu thập dữ liệu ảnh:** Chụp 5 ảnh khuôn mặt trực tiếp từ trình duyệt web cho mỗi nhân viên mới.
* **Huấn luyện mô hình:** Tự động huấn luyện mô hình nhận diện LBPH từ dữ liệu ảnh đã thu thập.
* **Điểm danh tự động (Script):** Chạy script Python (`03_face_recognition.py`) để camera hoạt động liên tục, tự động nhận diện và ghi giờ check-in/check-out vào CSDL.
* **Điểm danh (Web - Tùy chọn):** Chức năng bật/tắt camera điểm danh trực tiếp trên giao diện web (dùng cho demo hoặc quản lý).
* **Xem lịch sử:** Xem lịch sử điểm danh chi tiết theo từng nhân viên hoặc theo ngày.
* **Thống kê:** Xem tổng hợp thời gian làm việc của nhân viên và xuất báo cáo Excel.

---

## ⚙️ Cài đặt

### 1. Yêu cầu hệ thống

* Python 3.8+
* SQL Server (và SQL Server Management Studio hoặc công cụ tương tự)
* Driver `ODBC Driver 17 for SQL Server` (hoặc phiên bản tương thích)

### 2. Cài đặt Database

1.  Mở SQL Server Management Studio (SSMS).
2.  Tạo database mới tên `NhanDienKhuonMat`:
    ```sql
    CREATE DATABASE NhanDienKhuonMat;
    ```
3.  Chọn database vừa tạo, chạy script sau để tạo bảng:
    ```sql
    -- Bảng lưu thông tin nhân viên
    CREATE TABLE Employees (
        Id INT PRIMARY KEY IDENTITY(1,1), -- ID tự tăng
        Name NVARCHAR(100) NOT NULL,    -- Tên nhân viên
        Department NVARCHAR(100),       -- Phòng ban
        PhotoPath NVARCHAR(255),        -- Đường dẫn ảnh đại diện (avatar)
        CreatedAt DATETIME DEFAULT GETDATE() -- Thời gian tạo (tùy chọn)
    );

    -- Bảng lưu lịch sử điểm danh
    CREATE TABLE Attendance (
        Id INT PRIMARY KEY IDENTITY(1,1), -- ID tự tăng
        EmpId INT NOT NULL,              -- ID của nhân viên (khóa ngoại)
        Date DATE NOT NULL,              -- Ngày điểm danh
        TimeIn TIME,                     -- Giờ check-in
        TimeOut TIME,                    -- Giờ check-out
        FOREIGN KEY (EmpId) REFERENCES Employees(Id) -- Liên kết với bảng Employees
          ON DELETE CASCADE -- Tùy chọn: Tự động xóa lịch sử nếu nhân viên bị xóa
    );
    ```

### 3. Cài đặt thư viện Python

1.  Tạo môi trường ảo (khuyến nghị):
    ```bash
    python -m venv .venv
    source .venv/bin/activate # Linux/macOS
    .\.venv\Scripts\activate # Windows
    ```
2.  Cài đặt các thư viện cần thiết từ file `requirements.txt`:
    ```bash
    pip install -r requirements.txt

## ▶️ Hướng dẫn sử dụng

### 1. Chạy ứng dụng Web quản lý (`Attendace.py`)

Mở terminal trong thư mục dự án và chạy lệnh:
```bash
streamlit run Attendace.py
Trình duyệt sẽ tự động mở trang web quản lý. Tại đây bạn có thể:

Thêm nhân viên: Nhập thông tin, chụp 5 ảnh, và huấn luyện mô hình.

Xem/Sửa/Xóa nhân viên: Quản lý danh sách nhân viên.

Xem lịch sử & Thống kê: Theo dõi dữ liệu điểm danh.

Điểm danh (Demo): Bật/tắt camera để thử nghiệm nhận diện trên web.

(Ghi chú: Chức năng thu thập ảnh (trước đây là 01_face_dataset.py) và huấn luyện mô hình (trước đây là 02_face_training.py) đã được tích hợp vào ứng dụng web trong menu "Thêm nhân viên" và không cần chạy riêng nữa.)

2. Chạy Script điểm danh liên tục (03_face_recognition.py)
Script này dùng cho máy chấm công thực tế, chạy camera liên tục.

Bash

python 03_face_recognition.py
Camera sẽ mở và tự động nhận diện, ghi log check-in/check-out vào terminal và CSDL.

Nhấn ESC trong cửa sổ camera để dừng script.

Script sẽ tự động check-out cho những ai chưa check-out và dừng khi đến giờ CHECKOUT_TIME (mặc định là 23:00).

🛠️ Công nghệ sử dụng
Ngôn ngữ: Python

Nhận diện khuôn mặt: OpenCV (Haar Cascade, LBPH)

Giao diện Web: Streamlit

Cơ sở dữ liệu: Microsoft SQL Server

Kết nối CSDL: PyODBC

Xử lý dữ liệu: Pandas, NumPy

Xử lý ảnh: Pillow