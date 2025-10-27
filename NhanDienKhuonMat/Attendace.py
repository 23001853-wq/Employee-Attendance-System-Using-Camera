import streamlit as st
import pandas as pd
import pyodbc
import datetime
import os
import cv2
import numpy as np
from PIL import Image
import shutil # Thư viện để xóa thư mục
import time   # Thư viện để tạo độ trễ
import base64 # ui
# ==============================
#  CẤU HÌNH KẾT NỐI SQL SERVER
# ==============================
server = '.'
database = 'NhanDienKhuonMat'
driver = '{ODBC Driver 17 for SQL Server}'

def get_connection():
    return pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )

# ==============================
#  CÁC HÀM LẤY DỮ LIỆU
# ==============================
def get_employees():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Employees", conn)
    conn.close()
    return df

def get_attendance():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Attendance", conn)
    conn.close()
    return df

# ==============================
#  CÁC HÀM HỖ TRỢ (TỪ FILE 01 VÀ 02)
# ==============================
DATASET_DIR = "dataset"
TRAINER_DIR = "trainer"
TRAINER_FILE = os.path.join(TRAINER_DIR, 'trainer.yml')
FACE_DETECTOR = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))

def save_cropped_face(image_bytes, folder_name, user_id, count):
    """
    Xử lý ảnh từ st.camera_input, tìm mặt, crop, chuyển xám và lưu.
    Folder_name bây giờ có dạng 'nhanvien_{ID}'.
    Đã bỏ lưu ảnh khi lỗi.
    """
    try:
        # Đọc ảnh bằng cv2.imdecode
        image_bytes_data = image_bytes.getvalue()
        img_numpy_cv = cv2.imdecode(np.frombuffer(image_bytes_data, np.uint8), cv2.IMREAD_COLOR)

        if img_numpy_cv is None:
            st.error("Lỗi : Không thể giải mã dữ liệu ảnh từ camera.")
            return None

        gray = cv2.cvtColor(img_numpy_cv, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray) # Cân bằng sáng

        # Tăng minSize lên (80, 80)
        faces = FACE_DETECTOR.detectMultiScale(
            gray_eq,
            scaleFactor=1.2,
            minNeighbors=4,
            minSize=(80, 80) # <<< TĂNG KÍCH THƯỚC TỐI THIỂU
        )

        if len(faces) == 0:
            st.warning("Không tìm thấy khuôn mặt trong ảnh. Vui lòng thử lại.")           
            return None # Trả về None nếu thất bại

        # Chỉ lấy khuôn mặt đầu tiên
        (x, y, w, h) = faces[0]

        # In ra kích thước để kiểm tra
        print(f"Detected face box: x={x}, y={y}, w={w}, h={h}")

        # Kiểm tra kích thước hợp lệ trước khi crop
        if w < 30 or h < 30: # Nếu vẫn quá nhỏ -> coi như lỗi
             st.warning(f"Khuôn mặt tìm thấy quá nhỏ (w={w}, h={h}). Vui lòng thử lại.")
             return None

        face_img = gray[y:y + h, x:x + w] # Lưu ảnh gốc (chưa cân bằng)

        save_dir = os.path.join(DATASET_DIR, folder_name) # folder_name = f"nhanvien_{user_id}"
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f"User.{user_id}.{count}.jpg")
        cv2.imwrite(filename, face_img)

        return filename

    except Exception as e:
        st.error(f"Lỗi khi xử lý ảnh: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

def train_model():
    """
    Huấn luyện mô hình từ thư mục 'dataset' và lưu ra file .yml
    """
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        def getImagesAndLabels(path):
            imagePaths = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        imagePaths.append(os.path.join(root, file))

            faceSamples = []
            ids = []

            for imagePath in imagePaths:
                try:
                    PIL_img = Image.open(imagePath).convert('L')
                    img_numpy = np.array(PIL_img, 'uint8')
                    filename = os.path.basename(imagePath)
                    id_str = filename.split('.')[1]
                    id = int(id_str)
                    faceSamples.append(img_numpy)
                    ids.append(id)
                except Exception as e:
                    st.warning(f"Bỏ qua ảnh lỗi: {imagePath} ({e})")

            return faceSamples, ids

        st.info("Đang huấn luyện mô hình... Vui lòng chờ.")
        faces, ids = getImagesAndLabels(DATASET_DIR)

        if len(faces) == 0:
            st.error("Không có ảnh nào để huấn luyện. Vui lòng thêm ảnh.")
            return

        recognizer.train(faces, np.array(ids))
        os.makedirs(TRAINER_DIR, exist_ok=True)
        recognizer.write(TRAINER_FILE)

        st.success(f"Huấn luyện thành công! ({len(np.unique(ids))} người).")

    except Exception as e:
        st.error(f"Lỗi khi huấn luyện: {e}")


# ==============================
#  UI STREAMLIT
st.set_page_config(page_title="Hệ thống điểm danh", layout="wide")
st.title(" HỆ THỐNG ĐIỂM DANH NHÂN VIÊN")
# ================================
# Khởi tạo session_state (Bộ nhớ wed)
if 'photo_count' not in st.session_state:
    st.session_state.photo_count = 0
if 'new_emp_id' not in st.session_state:
    st.session_state.new_emp_id = None
if 'run_camera' not in st.session_state:
    st.session_state.run_camera = False
if 'last_event_time' not in st.session_state:
    st.session_state.last_event_time = {}

menu = st.sidebar.selectbox(
    "Chọn chức năng",
    ["Xem nhân viên", "Thêm nhân viên", "Xem lịch sử điểm danh", "Thống kê tổng hợp", "Điểm danh bằng camera"]
)

# -------------------------------
#  XEM DANH SÁCH NHÂN VIÊN (SỬA/XÓA)
# -------------------------------
if menu == "Xem nhân viên":
    st.header(" Danh sách nhân viên")
    df_emp = get_employees()
    if df_emp.empty:
        st.warning("Chưa có nhân viên nào trong hệ thống.")
    else:
        st.dataframe(df_emp, use_container_width=True)

    if not df_emp.empty:
        st.subheader("Quản lý nhân viên")

        selected_name = st.selectbox(
            "Chọn nhân viên để quản lý",
            df_emp["Name"],
            index=None,
            placeholder="Chọn một nhân viên..."
        )

        if selected_name:
            emp_details = df_emp[df_emp["Name"] == selected_name].to_dict('records')[0]
            emp_id = int(emp_details["Id"])

            # === CHỨC NĂNG SỬA ===
            with st.expander("✏️ Sửa thông tin nhân viên"):
                with st.form("edit_form"):
                    st.write(f"Đang sửa cho: **{emp_details['Name']}** (ID: {emp_id})")
                    new_name = st.text_input("Họ tên", value=emp_details['Name'])
                    new_dept = st.text_input("Phòng ban", value=emp_details['Department'])

                    submitted_edit = st.form_submit_button("Cập nhật thông tin")

                    if submitted_edit:
                        if not new_name or not new_dept:
                            st.error("Tên và Phòng ban không được để trống.")
                        else:
                            try:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("UPDATE Employees SET Name = ?, Department = ? WHERE Id = ?", (new_name, new_dept, emp_id))
                                conn.commit()
                                conn.close()
                                st.success(f"Đã cập nhật thông tin cho {new_name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi khi cập nhật: {e}")

            # === CHỨC NĂNG XÓA ===
            with st.expander("🗑️ Xóa nhân viên"):
                st.warning(f"**CẢNH BÁO:** Bạn có chắc chắn muốn xóa **{emp_details['Name']}**? Toàn bộ lịch sử điểm danh và ảnh huấn luyện của người này sẽ bị xóa vĩnh viễn.")

                confirm_check = st.checkbox("Tôi xác nhận muốn xóa")

                if st.button("XÓA VĨNH VIỄN", disabled=not confirm_check, type="primary"):
                    try:
                        # 1. Xóa ảnh avatar (nếu có)
                        if emp_details['PhotoPath'] and os.path.exists(emp_details['PhotoPath']):
                            os.remove(emp_details['PhotoPath'])

                        # 2. XÓA THƯ MỤC THEO ID
                        folder_name_to_delete = f"nhanvien_{emp_id}"
                        dir_to_delete = os.path.join(DATASET_DIR, folder_name_to_delete)

                        if os.path.exists(dir_to_delete):
                            shutil.rmtree(dir_to_delete)
                            st.info(f"Đã xóa thư mục ảnh: {dir_to_delete}")
                        else:
                            st.warning(f"Không tìm thấy thư mục ảnh {dir_to_delete}. Bỏ qua bước xóa ảnh.")

                        # 3. Xóa dữ liệu CSDL
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM Attendance WHERE EmpId = ?", (emp_id,))
                        cursor.execute("DELETE FROM Employees WHERE Id = ?", (emp_id,))
                        conn.commit()
                        conn.close()

                        st.success(f"Đã xóa vĩnh viễn {emp_details['Name']} (ID: {emp_id}) khỏi CSDL.")
                        st.warning("Mô hình đã cũ. Vui lòng huấn luyện lại (ở menu 'Thêm nhân viên').")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi xóa: {e}")

            # === LỊCH SỬ ĐIỂM DANH ===
            st.subheader(f"Lịch sử điểm danh của {selected_name}")
            df_att = get_attendance()
            df_att = df_att[df_att["EmpId"] == emp_id]
            if not df_att.empty:
                df_att = df_att.copy()
                df_att["WorkHours"] = (
                    pd.to_datetime(df_att["TimeOut"].astype(str), errors='coerce') - pd.to_datetime(df_att["TimeIn"].astype(str), errors='coerce')
                ).dt.total_seconds() / 3600
                st.dataframe(df_att, use_container_width=True)
            else:
                st.info("Nhân viên này chưa có lịch sử điểm danh.")

# -------------------------------
#  THÊM NHÂN VIÊN (SỬA LẠI THEO ID)
# -------------------------------
elif menu == "Thêm nhân viên":
    st.header(" Bước 1: Thêm thông tin nhân viên")

    with st.form("form_add_emp"):
        name = st.text_input(" Họ tên nhân viên")
        department = st.text_input(" Phòng ban")
        photo = st.file_uploader(" Ảnh đại diện (ảnh avatar, không dùng huấn luyện)", type=["jpg", "png", "jpeg"])
        submitted = st.form_submit_button("Lưu nhân viên")

        if submitted:
            if not name or not department:
                st.error(" Vui lòng nhập đầy đủ Tên và Phòng ban.")
            else:
                photo_path = None
                if photo:
                    os.makedirs("photos", exist_ok=True)
                    safe_name = name.replace(' ', '_')
                    photo_path = f"photos/{safe_name}.jpg"
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Employees (Name, Department, PhotoPath)
                        OUTPUT INSERTED.Id
                        VALUES (?, ?, ?)
                    """, (name, department, photo_path))

                    new_id = cursor.fetchone()[0]
                    conn.commit()
                    conn.close()

                    st.success(f" Đã thêm nhân viên: {name} (ID: {new_id})")

                    st.session_state.new_emp_id = new_id
                    st.session_state.photo_count = 0

                except Exception as e:
                    st.error(f"Lỗi khi thêm nhân viên vào DB: {e}")

    # === BƯỚC 2: CHỤP ẢNH (SỬA LẠI THEO ID) ===
    if st.session_state.new_emp_id:
        emp_id_for_photo = st.session_state.new_emp_id
        folder_name_for_photo = f"nhanvien_{emp_id_for_photo}"

        st.header(f" Bước 2: Chụp ảnh huấn luyện cho ID: {emp_id_for_photo} (Thư mục: {folder_name_for_photo})")
        st.info(f"Đã chụp: {st.session_state.photo_count} / 5 ảnh.")

        st.markdown("**Hướng dẫn:**")
        st.markdown("1. Đảm bảo đủ sáng, khuôn mặt rõ ràng.")
        st.markdown("2. **Thay đổi góc mặt (nhìn thẳng, hơi nghiêng trái/phải) *trước khi* nhấn nút chụp.**")
        st.markdown("3. Nhấn nút 'Take photo' bên dưới.")

        img_file_buffer = st.camera_input("Chụp ảnh huấn luyện")

        if img_file_buffer is not None and st.session_state.photo_count < 5:
            saved_file_path = save_cropped_face(
                image_bytes=img_file_buffer,
                folder_name=folder_name_for_photo, # Dùng tên thư mục mới
                user_id=emp_id_for_photo,
                count=st.session_state.photo_count + 1
            )

            if saved_file_path:
                st.session_state.photo_count += 1
                st.success(f"Đã lưu ảnh {st.session_state.photo_count}/5: {saved_file_path}")
                time.sleep(1) # Thêm độ trễ(s)
                st.rerun()

    # === BƯỚC 3: HUẤN LUYỆN ===
    if st.session_state.photo_count >= 5:
        st.header(" Bước 3: Hoàn tất huấn luyện")
        st.success("Đã chụp đủ 5 ảnh!")
        if st.button("Bắt đầu huấn luyện"):
            train_model()
            st.session_state.new_emp_id = None
            st.session_state.photo_count = 0

    # Cho phép huấn luyện lại bất cứ lúc nào
    st.divider()
    st.header("Huấn luyện lại mô hình (Tùy chọn)")
    st.warning("Nếu bạn vừa XÓA nhân viên, bạn nên chạy lại huấn luyện.")
    if st.button("Huấn luyện lại tất cả ảnh trong 'dataset'"):
        train_model()

# -------------------------------
#  XEM LỊCH SỬ ĐIỂM DANH
# -------------------------------
elif menu == "Xem lịch sử điểm danh":
    st.header(" Lịch sử điểm danh")
    df_att = get_attendance()
    if df_att.empty:
        st.warning("Chưa có dữ liệu điểm danh.")
    else:
        df_emp = get_employees()
        df = df_att.merge(df_emp[['Id', 'Name']], left_on='EmpId', right_on='Id', how='left')
        df = df.copy()

        df["WorkHours"] = (
            pd.to_datetime(df["TimeOut"].astype(str), errors='coerce') - pd.to_datetime(df["TimeIn"].astype(str), errors='coerce')
        ).dt.total_seconds() / 3600

        df = df.fillna(0) # Hiển thị 0 thay vì NaN
        df = df[["Name", "Date", "TimeIn", "TimeOut", "WorkHours"]]

        date_filter = st.date_input("Chọn ngày", datetime.date.today())
        df_filtered = df[pd.to_datetime(df["Date"]).dt.date == date_filter]

        if df_filtered.empty:
            st.info(f"Không có điểm danh nào trong ngày {date_filter}.")
        else:
            st.dataframe(df_filtered, use_container_width=True)

# -------------------------------
#  THỐNG KÊ TỔNG HỢP
# -------------------------------
elif menu == "Thống kê tổng hợp":
    st.header(" Thống kê tổng thời gian làm việc")
    df_att = get_attendance()
    df_emp = get_employees()

    if df_att.empty:
        st.warning("Chưa có dữ liệu điểm danh để thống kê.")
    else:
        df = df_att.merge(df_emp[['Id', 'Name']], left_on='EmpId', right_on='Id', how='left')

        time_diff_seconds = (
            pd.to_datetime(df["TimeOut"].astype(str), errors='coerce') - 
            pd.to_datetime(df["TimeIn"].astype(str), errors='coerce')
        ).dt.total_seconds()

        df["WorkHours"] = time_diff_seconds / 3600
        
        df["WorkMinutes"] = time_diff_seconds / 60

        df = df.fillna(0) 

        summary = df.groupby("Name").agg(
            WorkHours=('WorkHours', 'sum'),      
            WorkMinutes=('WorkMinutes', 'sum') 
        ).reset_index()

        summary['Tổng Giờ'] = (summary['WorkMinutes'] // 60).astype(int)
        summary['Tổng Phút'] = (summary['WorkMinutes'] % 60).astype(int)
        summary['Tổng thời gian'] = summary['Tổng Giờ'].astype(str) + " giờ " + summary['Tổng Phút'].astype(str) + " phút"
        
        summary = summary.sort_values(by="WorkHours", ascending=False)
        
        st.bar_chart(summary.set_index("Name")['WorkHours'])
        
        st.dataframe(
            summary[['Name', 'Tổng thời gian', 'WorkHours']],
            use_container_width=True,
            column_config={"WorkHours": "Tổng giờ (dạng số)"} 
        )
        
        st.download_button(
            label="⬇️ Tải báo cáo Excel",
            # Xuất file có cả cột "Tổng thời gian"
            data=summary[['Name', 'Tổng thời gian', 'WorkHours', 'WorkMinutes']].to_csv(index=False).encode("utf-8"),
            file_name=f"ThongKe_{datetime.date.today()}.csv",
            mime="text/csv"
        )

# -------------------------------
#  ĐIỂM DANH BẰNG CAMERA (LOGIC FILE 03 - WEB)
# -------------------------------

def load_employee_names_dict():
    """
    Trả về một danh sách 'names' mà index của list
    khớp với 'Id' trong database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name FROM Employees ORDER BY Id ASC")
    rows = cursor.fetchall()
    conn.close()

    max_id = 0
    if rows:
        max_id = max([row[0] for row in rows])

    names = ['Unknown'] * (max_id + 1)

    for emp_id, name in rows:
        # Đảm bảo emp_id nằm trong khoảng index hợp lệ
        if 0 <= emp_id < len(names):
             names[emp_id] = name
        else:
            st.warning(f"Employee ID {emp_id} không hợp lệ cho danh sách names (độ dài {len(names)}).")

    return names

def opencv_attendance_streamlit():
    st.header("Điểm danh bằng nhận diện khuôn mặt (OpenCV)")

    COOLDOWN_SECONDS = 15 # thời gian check in ca mới 
    MIN_WORK_SECONDS = 30 # thời gian làm việc tối thiểu để check out
    NGUONG_TIN_CAY = 43 # Ngưỡng tin cậy (thấp hơn là tốt hơn

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Bắt đầu điểm danh"):
            st.session_state.run_camera = True
    with col2:
        if st.button("Dừng điểm danh"):
            st.session_state.run_camera = False

    FRAME_WINDOW = st.image([])

    if st.session_state.run_camera:
        try:
            # Kiểm tra file trainer có tồn tại không
            if not os.path.exists(TRAINER_FILE):
                 st.error(f"Lỗi: Không tìm thấy file huấn luyện '{TRAINER_FILE}'. Bạn đã huấn luyện mô hình chưa?")
                 st.session_state.run_camera = False
                 return

            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(TRAINER_FILE)
            faceCascade = FACE_DETECTOR
            font = cv2.FONT_HERSHEY_SIMPLEX
            names = load_employee_names_dict()
            cam = cv2.VideoCapture(0)
            if not cam.isOpened(): # Kiểm tra camera có mở được không
                 st.error("Lỗi: Không thể mở camera.")
                 st.session_state.run_camera = False
                 return
            cam.set(3, 640)
            cam.set(4, 480)
            minW = 0.1 * cam.get(3)
            minH = 0.1 * cam.get(4)
        except Exception as e:
            st.error(f"Lỗi khởi động camera hoặc mô hình: {e}. Bạn đã huấn luyện mô hình chưa?")
            st.session_state.run_camera = False
            return

        st.info("Nhấn nút 'Dừng điểm danh' để kết thúc.")

        while st.session_state.run_camera:
            ret, img = cam.read()
            if not ret:
                st.error("Không thể đọc camera.")
                st.session_state.run_camera = False
                break

            img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(int(minW), int(minH)))

            current_time = datetime.datetime.now()
            today = current_time.date()

            for (x, y, w, h) in faces:
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

                # Kiểm tra id có hợp lệ không trước khi lấy tên
                name = "Unknown"
                if id < len(names):
                     name = names[id]
                else:
                     st.warning(f"ID {id} trả về từ recognizer nằm ngoài khoảng của danh sách names (độ dài {len(names)}).")


                if confidence < NGUONG_TIN_CAY and name != "Unknown": # Chỉ xử lý nếu đủ tin cậy VÀ tên không phải Unknown
                    # Đủ tin cậy
                    cv2.putText(img_display, f"{name}", (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                    cv2.rectangle(img_display, (x, y), (x + w, y + h), (0, 255, 0), 2) # Xanh lá

                    # Logic điểm danh
                    if id in st.session_state.last_event_time:
                        seconds_since_last_event = (current_time - st.session_state.last_event_time[id]).total_seconds()
                        if seconds_since_last_event < COOLDOWN_SECONDS:
                            continue

                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        time_now_str = current_time.strftime("%H:%M:%S")
                        cursor.execute("SELECT Id, TimeIn, TimeOut FROM Attendance WHERE EmpId = ? AND Date = ? ORDER BY Id DESC", id, today)
                        rec = cursor.fetchone()

                        if rec is None:
                            # 1. Check-in
                            cursor.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", id, today, time_now_str)
                            conn.commit()
                            st.success(f"Check-in: {name} lúc {time_now_str}")
                            st.session_state.last_event_time[id] = current_time
                        elif rec.TimeOut is None or str(rec.TimeOut).strip() == "":
                            # 2. Check-out
                            time_in_str = str(rec.TimeIn)
                            # Thêm try-except để bắt lỗi format time
                            try:
                                time_in_obj = datetime.datetime.strptime(time_in_str, "%H:%M:%S").time()
                                time_in_datetime = datetime.datetime.combine(today, time_in_obj)
                                duration_seconds = (current_time - time_in_datetime).total_seconds()
                                if duration_seconds > MIN_WORK_SECONDS:
                                    cursor.execute("UPDATE Attendance SET TimeOut = ? WHERE Id = ?", time_now_str, rec.Id)
                                    conn.commit()
                                    st.success(f"Check-out: {name} lúc {time_now_str}")
                                    st.session_state.last_event_time[id] = current_time
                            except ValueError:
                                st.error(f"Lỗi format thời gian TimeIn từ DB: '{time_in_str}'")

                        else:
                            # 3. Check-in (ca mới)
                            cursor.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", id, today, time_now_str)
                            conn.commit()
                            st.success(f"Check-in (new): {name} lúc {time_now_str}")
                            st.session_state.last_event_time[id] = current_time
                        conn.close()
                    except Exception as e:
                        st.error(f"Lỗi ghi DB: {e}")
                else:
                    # Không đủ tin cậy hoặc id không hợp lệ
                    cv2.putText(img_display, "Unknown", (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                    cv2.rectangle(img_display, (x, y), (x + w, y + h), (255, 0, 0), 2) 

            # Hiển thị ảnh lên web
            FRAME_WINDOW.image(img_display)

        # Dọn dẹp khi vòng lặp dừng
        cam.release()
        # cv2.destroyAllWindows() # Không cần dòng này trong Streamlit
        if 'run_camera' in st.session_state:
            if st.session_state.run_camera == False:
                 st.success("Đã dừng camera!")

# === XỬ LÝ CHỌN MENU ===
if menu == "Điểm danh bằng camera":
    opencv_attendance_streamlit()