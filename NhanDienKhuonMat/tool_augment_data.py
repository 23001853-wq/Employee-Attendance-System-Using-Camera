import cv2
import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

# tăng cường mẫu các góc khi thiếu ảnh
# --- CẤU HÌNH ---
INPUT_DIR = input("Nhập đường dẫn thư mục chứa ảnh gốc (VD: dataset/nhanvien_1): ")
TARGET_COUNT = 50 

# --- CẤU HÌNH BỘ SINH DỮ LIỆU ---
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest'
)

def get_user_id_and_max_count(folder_path):
    """
    Quét thư mục để tìm ID và số thứ tự lớn nhất hiện có.
    Mục đích: Để đặt tên file mới nối tiếp (VD: đang có User.1.14.jpg -> sinh tiếp User.1.15.jpg)
    """
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    max_count = 0
    user_id = "1" # Giá trị mặc định nếu không tìm thấy
    
    # Cách 1: Thử tìm ID từ tên thư mục (VD: nhanvien_2 -> 2)
    folder_name = os.path.basename(folder_path.strip('/\\'))
    if "_" in folder_name:
        try:
            user_id = folder_name.split('_')[-1]
        except: pass
    elif folder_name.isdigit():
        user_id = folder_name

    # Cách 2: Quét tên file để tìm ID chính xác và số thứ tự lớn nhất
    # File chuẩn: User.ID.Count.jpg
    for f in files:
        parts = f.split('.')
        # Kiểm tra cấu trúc User.1.14.jpg
        if len(parts) >= 4 and parts[0] == "User":
            try:
                current_id = parts[1]
                current_count = int(parts[2])
                
                # Cập nhật ID theo file tìm thấy
                user_id = current_id 
                
                # Tìm số lớn nhất
                if current_count > max_count:
                    max_count = current_count
            except:
                pass
                
    return user_id, max_count

def augment_data():
    if not os.path.exists(INPUT_DIR):
        print(f"[LỖI] Không tìm thấy thư mục: {INPUT_DIR}")
        return

    print(f"\n[INFO] Đang đọc ảnh từ {INPUT_DIR}...")
    
    # 1. Xác định ID và số thứ tự hiện tại
    user_id, current_max_count = get_user_id_and_max_count(INPUT_DIR)
    print(f" -> User ID xác định: {user_id}")
    print(f" -> Đang dừng ở số thứ tự: {current_max_count}")

    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Chỉ lấy những file chưa qua xử lý (nếu muốn) hoặc lấy tất cả làm mẫu
    if len(image_files) == 0:
        print("[LỖI] Thư mục rỗng!")
        return

    current_total = len(image_files)
    needed = TARGET_COUNT - current_total
    
    if needed <= 0:
        print(f"[INFO] Đã có {current_total} ảnh. Đủ rồi, không cần sinh thêm.")
        return

    print(f" -> Cần sinh thêm {needed} ảnh nữa...")

    generated_count = 0
    next_count = current_max_count + 1 # Bắt đầu đếm từ số tiếp theo
    
    # Vòng lặp sinh ảnh
    for filename in image_files:
        img_path = os.path.join(INPUT_DIR, filename)
        try:
            # Load ảnh và ép size 224x224 luôn
            img = load_img(img_path, target_size=(224, 224))
            x = img_to_array(img)
            x = x.reshape((1,) + x.shape)
        except Exception as e:
            print(f"    Lỗi đọc ảnh {filename}: {e}")
            continue

        i = 0
        # Quan trọng: KHÔNG dùng save_to_dir, mà lấy dữ liệu về tự lưu
        for batch in datagen.flow(x, batch_size=1):
            i += 1
            
            # Lấy dữ liệu ảnh sinh ra (đang ở hệ màu RGB của Keras)
            aug_img = batch[0].astype('uint8')
            
            # Chuyển màu từ RGB sang BGR (để OpenCV lưu đúng màu)
            aug_img = cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR)
            
            # Tự đặt tên file CHUẨN: User.ID.Count.jpg
            new_filename = f"User.{user_id}.{next_count}.jpg"
            save_path = os.path.join(INPUT_DIR, new_filename)
            
            # Lưu ảnh thủ công
            cv2.imwrite(save_path, aug_img)
            print(f"    -> Đã tạo: {new_filename}")
            
            generated_count += 1
            next_count += 1
            
            if generated_count >= needed:
                break
            
            # Mỗi ảnh gốc sinh tối đa 10 biến thể để đảm bảo đa dạng
            if i >= 10: 
                break
        
        if generated_count >= needed:
            break

    print(f"\n[SUCCESS] Hoàn tất! Tổng số ảnh hiện tại: {len(os.listdir(INPUT_DIR))}")

if __name__ == "__main__":
    augment_data()