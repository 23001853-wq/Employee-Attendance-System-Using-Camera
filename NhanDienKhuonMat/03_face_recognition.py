import cv2
import numpy as np
import os
import pickle
import datetime
import time
import pyodbc 
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from sklearn.preprocessing import Normalizer

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")
MODEL_SVM_PATH = os.path.join(TRAINER_DIR, 'svm_face_classifier.pkl')
LABEL_MAP_PATH = os.path.join(TRAINER_DIR, 'label_map.pkl')
HAAR_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

# --- CẤU HÌNH SQL ---
DB_SERVER = '.'  
DB_DATABASE = 'NhanDienKhuonMat'
DB_DRIVER = '{ODBC Driver 17 for SQL Server}'

def get_connection():
    try: return pyodbc.connect(f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;')
    except: return None

def load_names_map():
    names = {}
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Name FROM Employees")
            for row in cursor.fetchall(): names[row.Id] = row.Name
        except: pass
        finally: conn.close()
    return names

def load_resources():
    print("[INFO] Đang tải model...")
    face_detector = cv2.CascadeClassifier(HAAR_PATH)
    feature_extractor = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3), pooling='avg')
    
    if not os.path.exists(MODEL_SVM_PATH): return None, None, None, None

    with open(MODEL_SVM_PATH, 'rb') as f: model_svm = pickle.load(f)
    with open(LABEL_MAP_PATH, 'rb') as f: label_map = pickle.load(f)
    
    return face_detector, feature_extractor, model_svm, label_map

def extract_id_from_folder(folder_name):
    s = str(folder_name)
    if s.isdigit(): return int(s)
    if "_" in s:
        try: return int(s.split('_')[-1])
        except: return None
    return None

def main():
    detector, extractor, svm_model, labels = load_resources()
    if detector is None: return

    names_map = load_names_map()
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # QUAN TRỌNG: Bộ chuẩn hóa L2 (phải có để khớp với file train)
    scaler = Normalizer(norm='l2')
    
    # Mức độ an toàn
    CONFIDENCE_THRESHOLD = 0.55
    
    # Biến quản lý điểm danh
    COOLDOWN_SECONDS = 15; MIN_WORK_SECONDS = 30; last_event_time = {}

    print(f"\n[INFO] Sẵn sàng! Sử dụng SVM + L2 Normalization.")
    print(f"[INFO] Ngưỡng tin cậy: {CONFIDENCE_THRESHOLD * 100:.0f}%")

    while True:
        ret, frame = cam.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        img_copy = frame.copy()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_roi = img_copy[y:y+h, x:x+w]
            
            try:
                if face_roi.size == 0: continue
                
                # 1. Preprocess
                face_input = cv2.resize(face_roi, (224, 224))
                face_input = img_to_array(face_input)
                face_input = np.expand_dims(face_input, axis=0)
                face_input = preprocess_input(face_input)
                
                # 2. Extract & Normalize
                raw_vec = extractor.predict(face_input, verbose=0)
                vec = scaler.transform(raw_vec) # Chuẩn hóa vector
                
                # 3. SVM Dự đoán
                preds = svm_model.predict_proba(vec)[0]
                j = np.argmax(preds)
                svm_prob = preds[j]
                
                predicted_id = svm_model.classes_[j]
                folder_name_raw = labels.get(predicted_id, "Unknown")
                
                final_name = "Unknown"
                color = (0, 0, 255) # Đỏ mặc định

                if svm_prob > CONFIDENCE_THRESHOLD and folder_name_raw != "Unknown":
                    # Lấy tên thật từ SQL
                    emp_id = extract_id_from_folder(folder_name_raw)
                    
                    display_name = str(folder_name_raw)
                    if emp_id and emp_id in names_map: display_name = names_map[emp_id]
                    
                    final_name = display_name
                    color = (0, 255, 0) # Xanh    
                    # --- GHI SQL (Chỉ khi nhận diện thành công) ---
                    if emp_id:
                        conn = get_connection()
                        if conn:
                            now = datetime.datetime.now()
                            today = now.date()
                            can_log = True
                            if emp_id in last_event_time:
                                if (now - last_event_time[emp_id]).total_seconds() < COOLDOWN_SECONDS: can_log = False
                            
                            if can_log:
                                cur = conn.cursor()
                                t_str = now.strftime("%H:%M:%S")
                                cur.execute("SELECT Id, TimeIn, TimeOut FROM Attendance WHERE EmpId = ? AND Date = ? ORDER BY Id DESC", emp_id, today)
                                rec = cur.fetchone()
                                
                                if rec is None:
                                    cur.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", emp_id, today, t_str)
                                    conn.commit()
                                    print(f" [SQL] CHECK-IN: {final_name}")
                                    last_event_time[emp_id] = now
                                elif rec.TimeOut is None or str(rec.TimeOut).strip() == "":
                                    t_in = datetime.datetime.strptime(str(rec.TimeIn), "%H:%M:%S").time()
                                    dt_in = datetime.datetime.combine(today, t_in)
                                    if (now - dt_in).total_seconds() > MIN_WORK_SECONDS:
                                        cur.execute("UPDATE Attendance SET TimeOut = ? WHERE Id = ?", t_str, rec.Id)
                                        conn.commit()
                                        print(f" [SQL] CHECK-OUT: {final_name}")
                                        last_event_time[emp_id] = now
                                else:
                                    cur.execute("INSERT INTO Attendance (EmpId, Date, TimeIn) VALUES (?, ?, ?)", emp_id, today, t_str)
                                    conn.commit()
                                    print(f" [SQL] CA MỚI: {final_name}")
                                    last_event_time[emp_id] = now
                            conn.close()
                    # ----------------

                # Hiển thị
                text = f"{final_name} ({svm_prob*100:.0f}%)"
                cv2.putText(frame, text, (x, y-10), font, 0.8, color, 2)

            except Exception as e: pass
            
        cv2.imshow('SVM Face Recognition (L2 Norm)', frame)
        if cv2.waitKey(1) & 0xFF == 27: break
        
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()