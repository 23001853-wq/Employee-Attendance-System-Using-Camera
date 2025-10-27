import cv2
import numpy as np
from PIL import Image
import os

# Trỏ đến dataset
path = 'dataset'

# Kiểm tra module face
try:
    # Sử dụng thuật toán LBPH (Local Binary Patterns Histograms) nhận diện khuôn mặt
    recognizer = cv2.face.LBPHFaceRecognizer_create() 
    print("Đã tạo thành công công cụ nhận diện khuôn mặt LBPH.")
except AttributeError:
    print("cv2.face module is not available. Vui lòng cài đặt opencv-contrib-python.")
    exit()

# hàm lấy dữ liệu từ dataset
def getImagesAndLabels(path):
    imagePaths = []
    # Duyệt đệ quy tất cả file trong các thư mục con
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                imagePaths.append(os.path.join(root, file)) #Thêm đường dẫn đầy đủ của ảnh vào danh sách.

    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            PIL_img = Image.open(imagePath).convert('L') # chuyển đổi ảnh sang thang độ xám
        except Exception as e:
            print(f"[WARNING] Không thể mở {imagePath}: {e}")
            continue
        # Chuyển đối tượng ảnh PIL thành mảng NumPy, định dạng mà OpenCV có thể hiểu, uint8 là kiểu dữ liệu (số nguyên 8-bit, 0-255) chuẩn cho ảnh xám.
        img_numpy = np.array(PIL_img, 'uint8')  

        # === Lấy ID từ TÊN FILE ===
        try:
            filename = os.path.basename(imagePath) # Ví dụ: "User.38.1.jpg"
            id_str = filename.split('.')[1]        # Lấy phần "38"
            id = int(id_str)
        except Exception as e:
            print(f"Không thể phân tích cú pháp id từ tệp trên {imagePath}: {e}")
            continue

        
        # === THÊM TRỰC TIẾP ẢNH VÀ ID ===
        faceSamples.append(img_numpy) # Thêm toàn bộ ảnh (đã crop sẵn)
        ids.append(id)                # Thêm ID tương ứng
        # ================================

    return faceSamples, ids
# Huấn luyện lưu mô hình
faces,ids = getImagesAndLabels(path)

if len(faces) == 0:
    print("\n [ERROR] Không thấy khuôn mặt nào để huấn luyện.")
else:
    try:
        # Thuật toán LBPH    
        recognizer.train(faces, np.array(ids)) # ghi nhớ ảnh và id tương ứng

        # tạo thư mục trainer nếu chưa tồn tại  
        os.makedirs('trainer', exist_ok=True) # Đảm bảo thư mục trainer tồn tại
        recognizer.write('trainer/trainer.yml') # lưu kết quả huấn luyện 

        # Thông báo kết quả
        print("\n [INFO] huấn luyện thành công {0} cá nhân.".format(len(np.unique(ids))))
    except cv2.error as e:
         print(f"\n [ERROR] Lỗi trong quá trình đào tạo {e}")
         print("Điều này có thể diễn ra nếu bạn không có khuôn mặt hoặc dữ liệu không hợp lệ.")