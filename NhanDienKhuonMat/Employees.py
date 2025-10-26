import pyodbc
import datetime

# ====== CẤU HÌNH KẾT NỐI SQL SERVER ======
server = '.'  # hoặc 'localhost' hoặc '.\\SQLEXPRESS' tùy máy
database = 'NhanDienKhuonMat'
driver = '{ODBC Driver 17 for SQL Server}'

def get_connection():
    return pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )


# ====== CREATE ======
def create_employee(name, department, photo_path, created_at=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO Employees (Name, Department, PhotoPath, CreatedAt)
        VALUES (?, ?, ?, ?)
    """
    if created_at is None:
        created_at = datetime.datetime.now()
    cursor.execute(query, (name, department, photo_path, created_at))
    conn.commit()
    print(f"[SUCCESS] Da them nhan vien: {name}")
    conn.close()


# ====== READ ======
def read_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Department, PhotoPath, CreatedAt FROM Employees;")
    rows = cursor.fetchall()
    print("📋 Danh sách nhân viên:")
    for row in rows:
        print(f"- ID: {row[0]}, Họ tên: {row[1]}, Phòng: {row[2]}, Ảnh: {row[3]}, Tạo lúc: {row[4]}")
    conn.close()


# ====== UPDATE ======
def update_employee(emp_id, name=None, department=None, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []
    if name:
        fields.append("Name = ?")
        values.append(name)
    if department:
        fields.append("Department = ?")
        values.append(department)
    if photo_path:
        fields.append("PhotoPath = ?")
        values.append(photo_path)

    if fields:
        query = f"UPDATE Employees SET {', '.join(fields)} WHERE Id = ?"
        values.append(emp_id)
        cursor.execute(query, tuple(values))
        conn.commit()
        print(f"🛠️ Đã cập nhật nhân viên ID {emp_id}")
    else:
        print("⚠️ Không có thông tin nào để cập nhật!")

    conn.close()


# ====== DELETE ======
def delete_employee(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Employees WHERE Id = ?", (emp_id,))
    conn.commit()
    print(f"🗑️ Đã xóa nhân viên ID {emp_id}")
    conn.close()


# ====== TRUY VẤN GIỜ ĐIỂM DANH ======
def get_timein_by_name_and_date(name: str, date_str: str):
    """
    Trả về TimeIn của nhân viên có 'name' trong ngày 'date_str' (định dạng dd/mm/YYYY)
    """
    date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()

    conn = get_connection()
    cursor = conn.cursor()

    # 1️⃣ Lấy Id của nhân viên
    cursor.execute("SELECT Id FROM Employees WHERE Name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Không tìm thấy nhân viên tên '{name}'")
        conn.close()
        return None
    emp_id = row[0]

    # 2️⃣ Lấy TimeIn từ Attendance
    cursor.execute("""
        SELECT TimeIn FROM Attendance
        WHERE EmpId = ? AND [Date] = ?
    """, (emp_id, date_obj))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"⚠️ Không có bản ghi điểm danh cho {name} ngày {date_str}")
        return None

    return rows[0][0]  # Trả về giờ đầu tiên (TIME)


# ====== TEST ======
if __name__ == "__main__":
    #create_employee("Duy","Phòng AI","User.1.1.jpg")
    read_employees()
    delete_employee(1)
    result = get_timein_by_name_and_date("BIMBIM", "26/10/2025")
    if result:
        print(f"🕒 Nhân viên Duy điểm danh vào: {result}")
    read_employees()