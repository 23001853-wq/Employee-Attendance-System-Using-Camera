import cv2
import numpy as np
import os
import datetime
import pyodbc 

# ======  KẾT NỐI SQL SERVER ======
server = '.'  
database = 'NhanDienKhuonMat'
driver = '{ODBC Driver 17 for SQL Server}'
def get_connection():
    return pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )

# ====== NHẬN DIỆN ======
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(os.path.join(os.path.dirname(__file__), 'trainer', 'trainer.yml'))
faceCascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))
font = cv2.FONT_HERSHEY_SIMPLEX

def load_employee_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name FROM Employees ORDER BY Id ASC")
    rows = cursor.fetchall()
    conn.close()
    # Tạo danh sách tên, index là ID
    max_id = max([row[0] for row in rows]) if rows else 0
    names = ['Unknown'] * (max_id + 1)
    for emp_id, name in rows:
        names[emp_id] = name
    return names

names = load_employee_names()

# ====== CAMERA ======
cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)
minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

# =======================================================
# ====== BIẾN QUẢN LÝ (LOGIC GIỐNG FILE STREAMLIT) ======
# =======================================================
COOLDOWN_SECONDS = 15  # (giây) Bỏ qua sau khi ghi sự kiện
MIN_WORK_SECONDS = 30 # (giây) Thời gian tối thiểu để check-out
last_event_time = {}   # {emp_id: datetime_object}

# Giữ lại tính năng tự động check-out lúc 17h
CHECKOUT_TIME = datetime.time(17, 0, 0)
# =======================================================


print("\n Hệ thống nhận diện đang hoạt động...")
print(f"Hệ thống sẽ tự động check-out và tắt lúc {CHECKOUT_TIME}.")

while True:
    ret, img = cam.read()
    if not ret:
        print("[LỖI] Không thể đọc camera.")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(int(minW), int(minH)))

    # Lấy thời gian 1 lần cho chính xác
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    today = current_datetime.date()

    # === Tự động check-out tất cả khi đến 17h ===
    if current_time >= CHECKOUT_TIME:
        print(f"\n[INFO] Đã đến {CHECKOUT_TIME}, tự động check-out cho các nhân viên còn lại...")
        try:
            conn_auto = get_connection()
            cursor_auto = conn_auto.cursor()
            # Cập nhật TimeOut cho tất cả bản ghi hôm nay CÒN TRỐNG TimeOut
            query = "UPDATE Attendance SET TimeOut = ? WHERE Date = ? AND TimeOut IS NULL"
            cursor_auto.execute(query, (current_time.strftime("%H:%M:%S"), today))
            conn_auto.commit()
            conn_auto.close()
            print("[INFO] Check-out hàng loạt hoàn tất.")
        except Exception as e:
            print(f"[LỖI] Lỗi khi auto-checkout: {e}")
        break # Dừng vòng lặp camera

    # === Nhận diện khuôn mặt ===
    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        # Độ tin cậy
        if confidence < 43:
            name = names[id] if id < len(names) else "Unknown"
            cv2.putText(img, f"{name}", (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # =======================================================
            # ====== LOGIC ĐIỂM DANH (GIỐNG FILE STREAMLIT) ======
            # =======================================================
            
            # 1. Kiểm tra Cooldown
            if id in last_event_time:
                seconds_since_last_event = (current_datetime - last_event_time[id]).total_seconds()
                if seconds_since_last_event < COOLDOWN_SECONDS:
                    continue # Đang trong cooldown, bỏ qua, không xử lý

            # 2. Nếu không trong cooldown, kiểm tra DB để quyết định
            try:
                conn = get_connection()
                cursor = conn.cursor()
                time_now_str = current_datetime.strftime("%H:%M:%S")

                # Tìm bản ghi MỚI NHẤT hôm nay của người này
                cursor.execute("SELECT Id, TimeIn, TimeOut FROM Attendance WHERE EmpId = ? AND Date = ? ORDER BY Id DESC", id, today)
                rec = cursor.fetchone()

                if rec is None:
                    # TRƯỜNG HỢP 1: CHƯA CÓ BẢN GHI NÀO HÔM NAY -> CHECK-IN
                    cursor.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", id, today, time_now_str)
                    conn.commit()
                    print(f" CHECK-IN: {name} (ID {id}) lúc {time_now_str}")
                    last_event_time[id] = current_datetime # Cập nhật cooldown

                elif rec.TimeOut is None or str(rec.TimeOut).strip() == "":
                    # TRƯỜNG HỢP 2: ĐÃ CHECK-IN, CHƯA CHECK-OUT -> XỬ LÝ CHECK-OUT
                    
                    # Chuyển TimeIn (từ DB) sang datetime object
                    time_in_obj = datetime.datetime.strptime(str(rec.TimeIn), "%H:%M:%S").time()
                    time_in_datetime = datetime.datetime.combine(today, time_in_obj)
                    
                    duration_seconds = (current_datetime - time_in_datetime).total_seconds()

                    if duration_seconds > MIN_WORK_SECONDS:
                        # Đủ thời gian làm việc -> CHECK-OUT
                        cursor.execute("UPDATE Attendance SET TimeOut = ? WHERE Id = ?", time_now_str, rec.Id)
                        conn.commit()
                        print(f" CHECK-OUT: {name} (ID {id}) lúc {time_now_str}")
                        last_event_time[id] = current_datetime # Cập nhật cooldown
                    else:
                        # Chưa đủ thời gian, chỉ là vẫn đứng trước camera
                        # Không làm gì cả
                        pass 

                else:
                    # TRƯỜNG HỢP 3: ĐÃ CÓ CHECK-IN VÀ CHECK-OUT (ĐÃ HOÀN THÀNH CA) -> CHECK-IN (CA MỚI)
                    cursor.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", id, today, time_now_str)
                    conn.commit()
                    print(f" CHECK-IN (Ca mới): {name} (ID {id}) lúc {time_now_str}")
                    last_event_time[id] = current_datetime # Cập nhật cooldown
                
                conn.close()
            except Exception as e:
                print(f"[LỖI] Lỗi ghi DB: {e}")
            # =======================================================

        else:
            # Xử lý người lạ
            cv2.putText(img, "Unknown", (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow('Camera - Cham Cong Tu Dong', img)
    k = cv2.waitKey(10) & 0xff
    if k == 27:  # ESC để thoát
        break

# ====== DỌN DẸP ======
print(" Đóng camera và kết thúc chương trình.")
cam.release()
cv2.destroyAllWindows()