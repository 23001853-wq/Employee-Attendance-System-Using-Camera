import cv2
import os
import time

# Khởi tạo camera
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Camera không mở được")
    exit()

# Thiết lập độ phân giải
cam.set(3, 640)
cam.set(4, 480)

# Load model phát hiện khuôn mặt (Haar Cascade)
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Nhập thông tin người dùng
employee_folder = input('\n Nhập tên thư mục (nhanvien_1,..nhanvien_n): ')
face_id = input('Nhập ID User (Ví dụ: 1): ')

# Tạo đường dẫn lưu ảnh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

# Tạo thư mục nếu chưa có
save_dir = os.path.join(DATASET_DIR, employee_folder)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

print("\n Nhấn phím bất kỳ để bắt đầu chụp ảnh!")

# Vòng lặp chờ người dùng sẵn sàng
while True:
    ret, img = cam.read()
    if not ret: break
    img = cv2.flip(img, 1)
    
    cv2.putText(img, 'Nhan phim bat ky de bat dau chup', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    cv2.imshow('image', img)
    
    k = cv2.waitKey(1) & 0xff
    if k != 255: # Đã nhấn phím
        break
    if k == 27: # ESC
        cam.release()
        cv2.destroyAllWindows()
        exit()

# --- BẮT ĐẦU QUÁ TRÌNH CHỤP ẢNH ---
print("\n[INFO] Bắt đầu chụp 50 ảnh. Hãy xoay mặt nhiều góc độ!")
count = 0
total_images = 50
# Thời gian chụp
capture_duration = 60 
start_time = time.time()

while count < total_images:
    ret, img = cam.read()
    if not ret: break
    img = cv2.flip(img, 1) # Lật ảnh gương
    
    # 1. Chuyển sang xám chỉ để PHÁT HIỆN mặt (cho nhanh)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Vẽ khung chữ nhật lên màn hình để dễ nhìn
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # 2. Cắt khuôn mặt từ ảnh gốc MÀU (img)
        face_img = img[y:y + h, x:x + w]
        
        # Kiểm tra an toàn
        if face_img.size == 0:
            continue

        try:
            # 3. Resize về chuẩn 224x224
            face_img = cv2.resize(face_img, (224, 224))
            
            # 4. Lưu ảnh
            filename = os.path.join(save_dir, f"User.{face_id}.{count + 1}.jpg")
            cv2.imwrite(filename, face_img)
            
            count += 1
            print(f"Đã lưu: {count}/{total_images}")
            
            # --- THÊM ĐOẠN NÀY: NGHỈ 0.5 GIÂY SAU MỖI LẦN CHỤP ---
            # Giúp bạn có thời gian đổi tư thế mặt
            time.sleep(0.5) 
            # -----------------------------------------------------
            
        except Exception as e:
            print(f"Lỗi khi xử lý ảnh: {e}")

        # Chỉ lấy 1 khuôn mặt trong khung hình để tránh lỗi
        if count >= total_images:
            break

    # Hiển thị thông tin lên màn hình
    elapsed = time.time() - start_time
    remain = max(0, int(capture_duration - elapsed))
    cv2.putText(img, f'Da chup: {count}/{total_images}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    
    cv2.imshow('image', img)

    # Thoát nếu hết giờ hoặc nhấn ESC
    k = cv2.waitKey(1) & 0xff
    if k == 27 or elapsed >= capture_duration:
        break

print("\n[INFO] Hoàn thành quá trình thu thập dữ liệu.")
cam.release()
cv2.destroyAllWindows()