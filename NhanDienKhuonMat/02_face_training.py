import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'dataset'

# Kiểm tra module face
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("LBPH Face Recognizer created successfully.")
except AttributeError:
    print("cv2.face module is not available. Vui lòng cài đặt opencv-contrib-python.")
    exit()

# === BỎ DÒNG NÀY ĐI ===
# detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = []
    # Duyệt đệ quy tất cả file trong các thư mục con
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                imagePaths.append(os.path.join(root, file))

    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        except Exception as e:
            print(f"[WARNING] Could not open {imagePath}: {e}")
            continue
        
        img_numpy = np.array(PIL_img, 'uint8')

        # === Lấy ID từ TÊN FILE ===
        try:
            filename = os.path.basename(imagePath) # Ví dụ: "User.38.1.jpg"
            id_str = filename.split('.')[1]        # Lấy phần "38"
            id = int(id_str)
        except Exception as e:
            print(f"[WARNING] Could not parse id from filename {imagePath}: {e}")
            continue
        
        # === BỎ PHẦN detectMultiScale VÀ VÒNG LẶP for faces ===
        # faces = detector.detectMultiScale(img_numpy)
        # for (x, y, w, h) in faces:
        #     faceSamples.append(img_numpy[y:y + h, x:x + w])
        #     ids.append(id)
        # =======================================================
        
        # === THÊM TRỰC TIẾP ẢNH VÀ ID ===
        faceSamples.append(img_numpy) # Thêm toàn bộ ảnh (đã crop sẵn)
        ids.append(id)                # Thêm ID tương ứng
        # ================================

    return faceSamples, ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)

if len(faces) == 0:
    print("\n [ERROR] No faces found to train. Please check your 'dataset' folder or subfolders.")
else:
    try:
        recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        os.makedirs('trainer', exist_ok=True) # Đảm bảo thư mục trainer tồn tại
        recognizer.write('trainer/trainer.yml')

        # Print the number of individuals trained and end program
        print("\n [INFO] {0} individuals trained. Exiting Program".format(len(np.unique(ids))))
    except cv2.error as e:
         print(f"\n [ERROR] OpenCV error during training: {e}")
         print("This might happen if dataset contains images without faces or invalid data.")