# Quá trình hoàn thiện phần nhận diện khuôn mặt

## 1. Thu thập dữ liệu khuôn mặt
- Chạy file `01_face_dataset.py`.
- Nhập tên thư mục nhân viên (ví dụ: nhanvienduy, nhanvienduc) và user id tương ứng.
- Hệ thống sẽ tự động chụp và lưu ảnh khuôn mặt vào đúng thư mục trong `dataset/`.
- Mỗi nhân viên nên thu thập từ 50–200 ảnh với nhiều góc mặt, ánh sáng khác nhau.

## 2. Huấn luyện mô hình nhận diện
- Chạy file `02_face_training.py`.
- Script sẽ tự động duyệt toàn bộ ảnh trong các thư mục con của `dataset/`.
- Mỗi ảnh phải có tên theo định dạng: `User.<id>.<số thứ tự>.jpg`.
- Mô hình được huấn luyện và lưu vào `trainer/trainer.yml`.

## 3. Nhận diện khuôn mặt và điểm danh
- Chạy file `03_face_recognition.py`.
- Khi camera nhận diện được khuôn mặt, hệ thống sẽ dựa vào id để hiển thị đúng tên nhân viên (cấu hình trong biến `names`).
- Nếu khuôn mặt không khớp, sẽ hiển thị là "unknown".


## HƯỚNG DẪN TẠO VÀ KẾT NỐI DATABASE SQL SERVER

### 1. Tạo Database và Bảng

**Bước 1:** Mở SQL Server Management Studio (SSMS) hoặc công cụ quản lý SQL Server.

**Bước 2:** Tạo database mới tên `NhanDienKhuonMat`:

```sql
CREATE DATABASE NhanDienKhuonMat;
```

**Bước 3:** Chọn database vừa tạo, tạo bảng nhân viên và bảng điểm danh:

```sql
CREATE TABLE Employees (
	Id INT PRIMARY KEY IDENTITY(1,1),
	Name NVARCHAR(100),
	Department NVARCHAR(100),
	Photo NVARCHAR(255)
);

CREATE TABLE Attendance (
	Id INT PRIMARY KEY IDENTITY(1,1),
	EmpId INT,
	Date DATE,
	TimeIn TIME,
	TimeOut TIME,
	FOREIGN KEY (EmpId) REFERENCES Employees(Id)
);
```

### 2. Cấu hình kết nối trong Python

**Bước 1:** Đảm bảo đã cài đặt driver ODBC cho SQL Server (`ODBC Driver 17 for SQL Server`).

**Bước 2:** Cài đặt thư viện `pyodbc`:

```bash
pip install pyodbc
```

**Bước 3:** Cấu hình chuỗi kết nối trong các file Python:

```python
server = '.'  # hoặc '.\\SQLEXPRESS' nếu dùng bản Express
database = 'NhanDienKhuonMat'
driver = '{ODBC Driver 17 for SQL Server}'

def get_connection():
	return pyodbc.connect(
		f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
	)
```

### 3. Kiểm tra hoạt động

1. Chạy các file Python (`Attendace.py`, `03_face_recognition.py`) để kiểm tra kết nối và ghi dữ liệu.
2. Nếu có lỗi kết nối, kiểm tra lại tên server, database, driver ODBC và quyền truy cập.

### 4. Lưu ý

- Đảm bảo SQL Server đang chạy và cho phép kết nối từ Python.
- Nếu dùng tài khoản SQL, thay `Trusted_Connection=yes` bằng `UID=...;PWD=...`.
- Có thể kiểm tra dữ liệu trực tiếp trong SSMS sau khi điểm danh.

