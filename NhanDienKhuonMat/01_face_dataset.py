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
employee_folder = input('\nEnter employee folder name (Nhập tên : (employee_1,employee_2)): ')
face_id = input('Enter user id and press <return>: ')

# Đường dẫn tuyệt đối tới thư mục dataset trong cùng thư mục với script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

print("\n [INFO] Camera đã sẵn sàng. Nhấn phím bất kỳ để bắt đầu chụp ảnh!")
# Hiển thị camera và chờ nhấn phím
while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Could not read frame")
        break
    img = cv2.flip(img, 1)
    cv2.putText(img, 'Nhan phim bat ky de bat dau chup', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xff
    if k != 255:  # Đã nhấn phím bất kỳ
        break
    if k == 27:
        print("\n[INFO] Exiting by user request (ESC pressed)")
        cam.release()
        cv2.destroyAllWindows()
        exit()

# Bắt đầu quá trình chụp ảnh
print("\n [INFO] Bắt đầu chụp ảnh khuôn mặt... Hãy di chuyển đầu nhẹ nhàng.")
count = 0
while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Could not read frame")
        break
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Chỉ lưu khi count < 5
        if count < 5:
            save_dir = os.path.join(DATASET_DIR, employee_folder)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            filename = os.path.join(save_dir, f"User.{face_id}.{count + 1}.jpg")
            face_img = gray[y:y + h, x:x + w]
            
            save_success = cv2.imwrite(filename, face_img)
            if save_success:
                count += 1
                cv2.putText(img, 'CAPTURED!', (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(f"\r[INFO] Captured image {count}/5: {filename}", end='')
        
        cv2.putText(img, 'Dang chup...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.putText(img, f'Images Captured: {count}/5', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow('image', img)
    
    # === THAY ĐỔI QUAN TRỌNG ===
    # Tăng thời gian chờ lên 200ms (hoặc 100ms)
    # Điều này làm chậm vòng lặp lại, cho phép bạn di chuyển đầu một chút
    # giữa các lần chụp. Dataset của bạn sẽ tốt hơn.
    k = cv2.waitKey(1000) & 0xff
    
    if k == 27:
        print("\n[INFO] Exiting by user request (ESC pressed)")
        break
    elif count >= 5:
        print("\n[INFO] Dataset collection completed")
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()