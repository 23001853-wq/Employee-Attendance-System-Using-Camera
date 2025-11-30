
# 🤖 Báo cáo Bài tập nhóm Môn Trí tuệ Nhân tạo
**📋 Thông tin:**

* **📚 Môn học:** MAT3508 - Nhập môn Trí tuệ Nhân tạo  
* **📅 Học kỳ:** Học kỳ 1 - 2025-2026  
* **🏫 Trường:** VNU-HUS (Đại học Quốc gia Hà Nội - Trường Đại học Khoa học Tự nhiên)  
* **📝 Tiêu đề:** Hệ thống điểm danh nhân viên sử dụng nhận diện khuôn mặt  
* **📅 Ngày nộp:** 30/11/2025  
* **📄 Báo cáo PDF:** 📄 [report.pdf](report.pdf)  
* **🖥️ Slide thuyết trình:** 🖥️ [slides.pdf](slides.pdf)  
* **📂 Kho lưu trữ:** 📁 Bao gồm mã nguồn, dữ liệu mẫu và tài liệu hướng dẫn
### 🏷️ Tên nhóm
Nhóm 28
### 👥 Thành viên nhóm
| 👤 Họ và tên 🧑‍🎓  | 🆔 Mã sinh viên 🧾 | 🐙 Tên GitHub 🔗     |
|------------------|---------------------|---------------------|
| [Nguyễn Hữu Duy]      | [23001853]    | [23001853-wq]      |

# Hệ thống Điểm danh bằng Nhận diện Khuôn mặt

Dự án xây dựng hệ thống điểm danh tự động sử dụng camera và thuật toán nhận diện khuôn mặt (OpenCV LBPH), tích hợp với cơ sở dữ liệu SQL Server và giao diện quản lý bằng Streamlit.

---
## 📁 Cấu trúc thư mục repo

```
├── data/              # Dữ liệu mẫu
├── NhanDienKhuonMat/  # Mã nguồn chính (script, model, dataset)
├── report.pdf         # Báo cáo PDF
├── slides.pdf         # Slide trình bày
├── requirements.txt   # Thư viện Python cần thiết
├── README.md          # Hướng dẫn sử dụng
```

## 🚀 Quick Start

Tóm tắt các bước cài đặt và chạy thử nhanh:

```bash
git clone <repo-url>
cd <repo>
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run Attendance.py

# Nếu muốn thao tác thủ công từng bước (tạo dữ liệu, huấn luyện, nhận diện):

```bash
# 1. Tạo dữ liệu khuôn mặt cho từng nhân viên (chạy cho từng người)
python NhanDienKhuonMat/01_face_dataset.py

# 2. Huấn luyện mô hình nhận diện
**Lưu ý:** File `02_face_training` là notebook Jupyter (`.ipynb`).

Bạn có thể mở và chạy bằng Jupyter Notebook hoặc VSCode:
```bash
jupyter notebook NhanDienKhuonMat/02_face_training.ipynb
# hoặc mở trực tiếp bằng VSCode và chạy từng cell
```

```bash
jupyter nbconvert --to script NhanDienKhuonMat/02_face_training.ipynb
python NhanDienKhuonMat/02_face_training.py
```

# 3. Nhận diện và điểm danh (chạy camera)
python NhanDienKhuonMat/03_face_recognition.py

# 4. Nếu thiếu ảnh, có thể tăng cường dữ liệu bằng tool:
python NhanDienKhuonMat/tool_augment_data.py
```

> **Lưu ý:**
> - Nếu dùng giao diện web thì các chức năng thu thập ảnh và huấn luyện đã tích hợp sẵn, không cần chạy 01/02 riêng.




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



## ▶️ Hướng dẫn sử dụng


### 1. Chạy ứng dụng Web quản lý (`Attendance.py`)

Mở terminal trong thư mục dự án và chạy lệnh:
```bash
streamlit run Attendance.py
```
Trình duyệt sẽ tự động mở trang web quản lý. Tại đây bạn có thể:

- Thêm nhân viên: Nhập thông tin, chụp 5 ảnh, và huấn luyện mô hình.
- Xem/Sửa/Xóa nhân viên: Quản lý danh sách nhân viên.
- Xem lịch sử & Thống kê: Theo dõi dữ liệu điểm danh.
- Điểm danh (Demo): Bật/tắt camera để thử nghiệm nhận diện trên web.

> **Ghi chú:** Chức năng thu thập ảnh (trước đây là 01_face_dataset.py) và huấn luyện mô hình (trước đây là 02_face_training.py) đã được tích hợp vào ứng dụng web trong menu "Thêm nhân viên" và không cần chạy riêng nữa.


### 2. Chạy Script điểm danh liên tục (`03_face_recognition.py`)
Script này dùng cho máy chấm công thực tế, chạy camera liên tục.

```bash
python 03_face_recognition.py
```
Camera sẽ mở và tự động nhận diện, ghi log check-in/check-out vào terminal và CSDL.

Nhấn ESC trong cửa sổ camera để dừng script.

Script sẽ tự động check-out cho những ai chưa check-out và dừng khi đến giờ CHECKOUT_TIME .
---

🛠️ Công nghệ sử dụng
Ngôn ngữ: Python

Nhận diện khuôn mặt: OpenCV (Haar Cascade, LBPH)

Giao diện Web: Streamlit

Cơ sở dữ liệu: Microsoft SQL Server

Kết nối CSDL: PyODBC

Xử lý dữ liệu: Pandas, NumPy

Xử lý ảnh: Pillow