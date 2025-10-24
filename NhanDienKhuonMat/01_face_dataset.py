
import cv2
import os

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open camera")
    exit()
cam.set(3, 640) # set video width
cam.set(4, 480) # set video height

face_detector = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))


# Nhập tên thư mục nhân viên và user id
employee_folder = input('\nEnter employee folder name (e.g., nhanvienduy, nhanvienduc): ')
face_id = input('Enter user id and press <return>: ')

# Đường dẫn tuyệt đối tới thư mục dataset trong cùng thư mục với script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while(True):

    ret, img = cam.read()
    if not ret:
        print("Error: Could not read frame")
        break
    img = cv2.flip(img, 1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        # Vẽ khung nhận diện khuôn mặt
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
        
        # Tự động chụp ảnh khi phát hiện khuôn mặt

        if count < 200:  # Chỉ chụp khi chưa đủ 200 ảnh
            # Tạo thư mục nếu chưa tồn tại
            save_dir = os.path.join(DATASET_DIR, employee_folder)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Lưu ảnh vào thư mục dataset/<employee_folder>
            filename = os.path.join(save_dir, f"User.{face_id}.{count + 1}.jpg")
            face_img = gray[y:y+h, x:x+w]

            # Kiểm tra và lưu ảnh
            save_success = cv2.imwrite(filename, face_img)

            if save_success:
                count += 1
                # Hiển thị thông báo chụp ảnh thành công
                cv2.putText(img, 'CAPTURED!', (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                print(f"\r[INFO] Captured image {count}/200: {filename}", end='')
        
        # Hiển thị hướng dẫn
        cv2.putText(img, 'Press any key to capture', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    # Hiển thị số ảnh đã chụp
    cv2.putText(img, f'Images Captured: {count}/200', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow('image', img)

    # Hiển thị số ảnh đã chụp
    cv2.putText(img, f'Images Captured: {count}/200', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('image', img)
    
    k = cv2.waitKey(1) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        print("\n[INFO] Exiting by user request (ESC pressed)")
        break
    elif count >= 200: # Take 200 face samples and stop video
        print("\n[INFO] Dataset collection completed")
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()


