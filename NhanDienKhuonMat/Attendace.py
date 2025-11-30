import streamlit as st
import pandas as pd
import pyodbc
import datetime
import os
import cv2
import numpy as np
import pickle
import time
import base64
from PIL import Image
import shutil

# --- THƯ VIỆN DEEP LEARNING ---
# Chỉ import khi cần thiết để tiết kiệm tài nguyên nếu không dùng chức năng AI
try:
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
    from tensorflow.keras.preprocessing.image import img_to_array, ImageDataGenerator, load_img
    from sklearn.preprocessing import Normalizer
except ImportError:
    st.error("Thiếu thư viện Deep Learning. Vui lòng cài đặt: tensorflow, scikit-learn")

# ==============================
#  CẤU HÌNH HỆ THỐNG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")
MODEL_SVM_PATH = os.path.join(TRAINER_DIR, 'svm_face_classifier.pkl')
LABEL_MAP_PATH = os.path.join(TRAINER_DIR, 'label_map.pkl')
HAAR_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

# SQL Server Config
DB_SERVER = '.'
DB_DATABASE = 'NhanDienKhuonMat'
DB_DRIVER = '{ODBC Driver 17 for SQL Server}'

# ==============================
#  1. CÁC HÀM KẾT NỐI & DATABASE
# ==============================
def get_connection():
    try:
        return pyodbc.connect(
            f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;'
        )
    except Exception as e:
        st.error(f"Lỗi kết nối SQL Server: {e}")
        return None

def get_employees():
    conn = get_connection()
    if conn:
        query = "SELECT Id, Name, Department, CreatedAt FROM Employees"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_attendance():
    conn = get_connection()
    if conn:
        query = "SELECT * FROM Attendance"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# ==============================
#  2. CÁC HÀM LOAD MODEL AI
# ==============================
@st.cache_resource
def load_ai_resources():
    """Load model một lần duy nhất và cache lại để tăng tốc"""
    face_detector = cv2.CascadeClassifier(HAAR_PATH)
    
    try:
        feature_extractor = MobileNetV2(weights="imagenet", include_top=False, 
                                        input_shape=(224, 224, 3), pooling='avg')
    except Exception as e:
        st.error(f"Lỗi load MobileNetV2: {e}")
        return None, None, None, None
    
    if not os.path.exists(MODEL_SVM_PATH) or not os.path.exists(LABEL_MAP_PATH):
        return face_detector, feature_extractor, None, None

    with open(MODEL_SVM_PATH, 'rb') as f: model_svm = pickle.load(f)
    with open(LABEL_MAP_PATH, 'rb') as f: label_map = pickle.load(f)
        
    return face_detector, feature_extractor, model_svm, label_map

def extract_id_from_folder(folder_name):
    s = str(folder_name)
    if s.isdigit(): return int(s)
    if "_" in s:
        try: return int(s.split('_')[-1])
        except: pass
    return None

# ==============================
#  3. HÀM XỬ LÝ ẢNH & AUGMENTATION
# ==============================
def save_cropped_face(image_bytes, user_id, count):
    try:
        # Đọc ảnh từ buffer của Streamlit
        image_bytes_data = image_bytes.getvalue()
        img_numpy = cv2.imdecode(np.frombuffer(image_bytes_data, np.uint8), cv2.IMREAD_COLOR)
        if img_numpy is None: return None

        # Chuyển xám để tìm mặt
        gray = cv2.cvtColor(img_numpy, cv2.COLOR_BGR2GRAY)
        face_detector = cv2.CascadeClassifier(HAAR_PATH)
        faces = face_detector.detectMultiScale(gray, 1.2, 5)

        if len(faces) == 0:
            st.warning("⚠️ Không tìm thấy khuôn mặt. Hãy thử lại!")
            return None

        # Lấy khuôn mặt lớn nhất
        faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
        (x, y, w, h) = faces[0]

        # Cắt và resize về 224x224
        face_img = img_numpy[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (224, 224))

        # Tạo thư mục
        folder_path = os.path.join(DATASET_DIR, f"nhanvien_{user_id}")
        os.makedirs(folder_path, exist_ok=True)

        # Lưu file
        filename = os.path.join(folder_path, f"User.{user_id}.{count}.jpg")
        cv2.imwrite(filename, face_img)
        return filename
    except Exception as e:
        st.error(f"Lỗi xử lý ảnh: {e}")
        return None

def augment_data_for_user(user_id):
    """Tự động sinh 50 ảnh từ các ảnh gốc"""
    folder_path = os.path.join(DATASET_DIR, f"nhanvien_{user_id}")
    if not os.path.exists(folder_path): return 0
    
    datagen = ImageDataGenerator(
        rotation_range=20, width_shift_range=0.1, height_shift_range=0.1,
        shear_range=0.1, zoom_range=0.1, horizontal_flip=True,
        brightness_range=[0.8, 1.2], fill_mode='nearest'
    )
    
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('jpg')]
    if not image_files: return 0
    
    TARGET_COUNT = 50
    needed = TARGET_COUNT - len(image_files)
    if needed <= 0: return 0
    
    generated = 0
    next_count = len(image_files) + 1
    
    for filename in image_files:
        img_path = os.path.join(folder_path, filename)
        try:
            img = load_img(img_path, target_size=(224, 224))
            x = img_to_array(img)
            x = x.reshape((1,) + x.shape)
            
            i = 0
            for batch in datagen.flow(x, batch_size=1):
                aug_img = cv2.cvtColor(batch[0].astype('uint8'), cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(folder_path, f"User.{user_id}.{next_count}.jpg"), aug_img)
                
                generated += 1
                next_count += 1
                i += 1
                if generated >= needed: break
                if i >= 10: break 
            if generated >= needed: break
        except: continue
    
    return generated

# ==============================
#  4. GIAO DIỆN CHÍNH (STREAMLIT UI)
# ==============================
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{ background-image: url("data:image/png;base64,{encoded_string}"); background-size: cover; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.7); z-index: -1; }}
        </style>
        """, unsafe_allow_html=True)


st.set_page_config(page_title="Hệ thống điểm danh AI", layout="wide", page_icon="📸")
if os.path.exists('photos/anh3.jpg'):
    add_bg_from_local('photos/anh3.jpg')

st.title("🚀 HỆ THỐNG ĐIỂM DANH NHÂN VIÊN")

if os.path.exists('photos/anh.jpg'):
    st.sidebar.image('photos/anh.jpg')
st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Chọn chức năng", 
    ["Điểm danh bằng Camera", "Xem nhân viên", "Thêm nhân viên", "Xem lịch sử", "Thống kê", "Huấn luyện Mô hình"])

# Init Session State
if 'photo_count' not in st.session_state: st.session_state.photo_count = 0
if 'new_emp_id' not in st.session_state: st.session_state.new_emp_id = None
if 'run_camera' not in st.session_state: st.session_state.run_camera = False
if 'last_event_time' not in st.session_state: st.session_state.last_event_time = {}

# ---------------------------------------------------------
#  CHỨC NĂNG 1: ĐIỂM DANH (QUAN TRỌNG NHẤT)
# ---------------------------------------------------------
if menu == "Điểm danh bằng Camera":
    st.header("📸 Điểm danh Real-time")
    face_detector, feature_extractor, model_svm, label_map = load_ai_resources()
    
    if model_svm is None:
        st.error("⚠️ Chưa có Model. Vui lòng vào menu 'Huấn luyện Mô hình' trước!")
    else:
        scaler = Normalizer(norm='l2')
        db_names = {}
        df = get_employees()
        if not df.empty:
            for _, row in df.iterrows(): db_names[row['Id']] = row['Name']

        col1, col2 = st.columns([1, 3])
        with col1:
            start = st.button("▶️ BẮT ĐẦU", type="primary")
            stop = st.button("⏹️ DỪNG")
            thresh = st.slider("Ngưỡng tin cậy", 40, 90, 65) / 100.0
        with col2:
            st.write("Màn hình Camera:")
            FRAME_WINDOW = st.empty() # Dùng st.empty() để placeholder ảnh

        if start: st.session_state.run_camera = True
        if stop: st.session_state.run_camera = False

        if st.session_state.run_camera:
            cam = cv2.VideoCapture(0)
            cam.set(3, 640); cam.set(4, 480)
            # Giảm FPS nếu cần
            cam.set(cv2.CAP_PROP_FPS, 30) 
            COOLDOWN = 15; MIN_WORK = 30
            
            while st.session_state.run_camera:
                ret, frame = cam.read()
                if not ret: break
                
                frame = cv2.flip(frame, 1)
                disp = frame.copy()
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Tối ưu tham số detectMultiScale
                faces = face_detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(disp, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    roi = frame[y:y+h, x:x+w]
                    if roi.size == 0: continue
                    
                    try:
                        # Xử lý nhận diện (MobileNet + SVM)
                        inp = cv2.resize(roi, (224, 224))
                        inp = img_to_array(inp)
                        inp = np.expand_dims(inp, axis=0)
                        inp = preprocess_input(inp)
                        
                        vec = feature_extractor.predict(inp, verbose=0)
                        vec = scaler.transform(vec)
                        
                        preds = model_svm.predict_proba(vec)[0]
                        j = np.argmax(preds)
                        score = preds[j]
                        pid = model_svm.classes_[j]
                        
                        fname = label_map.get(pid, "Unknown")
                        final_name = "Unknown"; color = (0, 0, 255)
                        
                        if score > thresh and fname != "Unknown":
                            eid = extract_id_from_folder(fname)
                            if eid in db_names: final_name = db_names[eid]
                            else: final_name = str(fname)
                            color = (0, 255, 0)
                            
                            # Ghi SQL Server
                            if eid:
                                conn = get_connection()
                                if conn:
                                    cur = conn.cursor()
                                    now = datetime.datetime.now()
                                    
                                    # Check Cooldown
                                    can_log = True
                                    if eid in st.session_state.last_event_time:
                                        delta = (now - st.session_state.last_event_time[eid]).total_seconds()
                                        if delta < COOLDOWN: can_log = False
                                    
                                    if can_log:
                                        t_str = now.strftime("%H:%M:%S")
                                        cur.execute("SELECT Id, TimeIn, TimeOut FROM Attendance WHERE EmpId=? AND Date=? ORDER BY Id DESC", eid, now.date())
                                        rec = cur.fetchone()
                                        msg = ""
                                        
                                        if not rec:
                                            cur.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", eid, now.date(), t_str)
                                            msg = f"Check-in: {final_name}"
                                        elif not rec.TimeOut:
                                            t_in = datetime.datetime.strptime(str(rec.TimeIn), "%H:%M:%S").time()
                                            dt_in = datetime.datetime.combine(now.date(), t_in)
                                            if (now - dt_in).total_seconds() > MIN_WORK:
                                                cur.execute("UPDATE Attendance SET TimeOut=? WHERE Id=?", t_str, rec.Id)
                                                msg = f"Check-out: {final_name}"
                                        else:
                                            cur.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", eid, now.date(), t_str)
                                            msg = f"Ca mới: {final_name}"
                                            
                                        if msg:
                                            conn.commit()
                                            st.toast(f"✅ {msg}", icon="🎉")
                                            st.session_state.last_event_time[eid] = now
                                    conn.close()

                        cv2.putText(disp, f"{final_name} ({score:.0%})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    except: pass
                
                # Giảm kích thước ảnh trước khi gửi lên UI để tăng FPS
                display_img = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
                # Resize nhỏ hơn nếu vẫn lag, ví dụ (320, 240) hoặc giữ nguyên nếu ổn
                # display_img = cv2.resize(display_img, (320, 240))
                
                # Cập nhật ảnh vào placeholder đã tạo
                FRAME_WINDOW.image(display_img)
                
                # Thêm một độ trễ nhỏ nếu cần giảm tải CPU
                # time.sleep(0.03) 

            cam.release()

# ---------------------------------------------------------
#  CHỨC NĂNG: HUẤN LUYỆN (TÍCH HỢP AUGMENTATION + TRAIN)
# ---------------------------------------------------------
elif menu == "Huấn luyện Mô hình":
    st.header(" Huấn luyện bộ não AI")
    st.info("Quy trình: Tăng cường dữ liệu -> Trích xuất đặc trưng -> Huấn luyện SVM.")
    
    if st.button("BẮT ĐẦU HUẤN LUYỆN", type="primary"):
        from sklearn.svm import SVC
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Augmentation
            status.text("Đang tăng cường dữ liệu...")
            if os.path.exists(DATASET_DIR):
                subfolders = [f for f in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, f))]
                for i, folder in enumerate(subfolders):
                    uid = extract_id_from_folder(folder)
                    if uid: augment_data_for_user(uid)
                    bar.progress((i + 1) / (len(subfolders) * 2))
            
            # 2. Training
            status.text("Đang train model...")
            feature_extractor = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3), pooling='avg')
            X, y, label_map = [], [], {}
            
            dirs = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
            for idx, folder in enumerate(dirs):
                folder_path = os.path.join(DATASET_DIR, folder)
                files = [f for f in os.listdir(folder_path) if f.endswith('jpg')]
                
                for fname in files:
                    try:
                        uid = int(fname.split('.')[1])
                        img = cv2.imread(os.path.join(folder_path, fname))
                        if img is None: continue
                        img = cv2.resize(img, (224, 224))
                        x_arr = img_to_array(img)
                        x_arr = np.expand_dims(x_arr, axis=0)
                        x_arr = preprocess_input(x_arr)
                        
                        vec = feature_extractor.predict(x_arr, verbose=0)
                        X.append(vec[0])
                        y.append(uid)
                        if uid not in label_map: label_map[uid] = folder
                    except: pass
                
                bar.progress(0.5 + (idx + 1) / (len(dirs) * 2))

            if len(X) > 0:
                scaler = Normalizer(norm='l2')
                X = scaler.transform(np.array(X))
                model = SVC(kernel='rbf', C=10.0, gamma='scale', probability=True)
                model.fit(X, np.array(y))
                
                os.makedirs(TRAINER_DIR, exist_ok=True)
                with open(MODEL_SVM_PATH, 'wb') as f: pickle.dump(model, f)
                with open(LABEL_MAP_PATH, 'wb') as f: pickle.dump(label_map, f)
                
                st.success(f"✅ Huấn luyện xong! Đã học {len(X)} khuôn mặt.")
            else:
                st.error("Không có dữ liệu để train.")
                
        except Exception as e:
            st.error(f"Lỗi: {e}")

# ---------------------------------------------------------
#  CHỨC NĂNG: THÊM NHÂN VIÊN
# ---------------------------------------------------------
elif menu == "Thêm nhân viên":
    st.header(" Thêm nhân viên mới")
    
    with st.form("add_emp"):
        name = st.text_input("Họ tên")
        dept = st.text_input("Phòng ban")
        sub = st.form_submit_button("Tạo hồ sơ")
        
        if sub and name:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Employees (Name, Department) OUTPUT INSERTED.Id VALUES (?, ?)", (name, dept))
            nid = cur.fetchone()[0]
            conn.commit(); conn.close()
            st.session_state.new_emp_id = nid
            st.session_state.photo_count = 0
            st.success(f"Đã tạo nhân viên ID: {nid}")
            st.rerun()

    if st.session_state.new_emp_id:
        eid = st.session_state.new_emp_id
        st.info(f"📸 Đang chụp ảnh cho ID {eid}. Đã chụp: {st.session_state.photo_count}/5")
        
        img_buffer = st.camera_input("Chụp ảnh", key=f"cam_{st.session_state.photo_count}")
        
        if img_buffer:
            path = save_cropped_face(img_buffer, eid, st.session_state.photo_count + 1)
            if path:
                st.session_state.photo_count += 1
                st.toast(f"Đã lưu ảnh {st.session_state.photo_count}", icon="💾")
                time.sleep(1)
                st.rerun()
        
        if st.session_state.photo_count >= 5:
            st.success("✅ Đã chụp đủ 5 ảnh! Hãy sang menu 'Huấn luyện Mô hình'.")
            if st.button("Hoàn tất"):
                st.session_state.new_emp_id = None
                st.session_state.photo_count = 0
                st.rerun()

# ---------------------------------------------------------
#  CÁC CHỨC NĂNG QUẢN LÝ (XEM, LỊCH SỬ, THỐNG KÊ)
# ---------------------------------------------------------
elif menu == "Xem nhân viên":
    st.header("📋 Danh sách nhân viên")
    df = get_employees()
    st.dataframe(df, use_container_width=True)

elif menu == "Xem lịch sử":
    st.header(" Lịch sử ra vào")
    df_att = get_attendance()
    df_emp = get_employees()
    if not df_att.empty and not df_emp.empty:
        df = pd.merge(df_att, df_emp, left_on="EmpId", right_on="Id")
        st.dataframe(df[["Name", "Date", "TimeIn", "TimeOut"]], use_container_width=True)

elif menu == "Thống kê":
    st.header(" Thống kê công làm")
    df_att = get_attendance()
    df_emp = get_employees()
    if not df_att.empty:
        df = df_att.merge(df_emp[['Id', 'Name']], left_on='EmpId', right_on='Id', how='left')
        time_diff = (pd.to_datetime(df["TimeOut"].astype(str), errors='coerce') - pd.to_datetime(df["TimeIn"].astype(str), errors='coerce')).dt.total_seconds()
        df["Hours"] = time_diff / 3600
        df = df.fillna(0)
        sum_df = df.groupby("Name")["Hours"].sum().reset_index().sort_values("Hours", ascending=False)
        st.bar_chart(sum_df.set_index("Name"))
        st.dataframe(sum_df)