import cv2 # thư viện opencv cho phép làm m thứ liên quan đến video,ảnh
import os # Operating System. Thư viện này cho phép ta sư lý đường dẫn tạo lưu file

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Camera không mở được") # camera không mở được thì lỗi thoát chương trình 
    exit()
# chiều rộng dài độ phân giải
cam.set(3, 640)
cam.set(4, 480) 
# phát hiện khuôn mặt nhìn thẳng từ file xml 
face_detector = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))

# Nhập tên thư mục nhân viên và user id
employee_folder = input('\n Enter employee folder name (Nhập tên : (nhanvien_1,nhanvien_2))...: ')
face_id = input('nhập id user: ')

# Đường dẫn tuyệt đối tới thư mục dataset trong cùng thư mục với script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

print("\n Nhấn phím bất kỳ để bắt đầu chụp ảnh!")
# Hiển thị camera và đợi nhấn phím
while True:
    ret, img = cam.read() 
    if not ret:
        print("Error: Không thể đọc khung hình")
        break
    img = cv2.flip(img, 1)
    cv2.putText(img, 'Nhan phim bat ky de bat dau chup', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xff
    if k != 255:  # Đã nhấn phím bất kỳ
        break
    if k == 27:
        print("\n ESC (out camera)")
        cam.release()
        cv2.destroyAllWindows()
        exit()

# Bắt đầu quá trình chụp ảnh
print("\n Bắt đầu chụp ảnh khuôn mặt... Hãy di chuyển đầu nhẹ nhàng.")
count = 0
while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Không thể đọc khung hình")
        break
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5) # thuật toán quét ảnh nhiều kích cỡ khấc nhau

    for (x, y, w, h) in faces: # chạy qua từng khuôn mặt trong hình 
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2) 
        
        # Chỉ lưu khi count < 5 
        if count < 5:
            save_dir = os.path.join(DATASET_DIR, employee_folder)
            if not os.path.exists(save_dir): # kiểm tra xem tồn tại thư mục chưa nếu chưa tạo nó
                os.makedirs(save_dir) 
            
            filename = os.path.join(save_dir, f"User.{face_id}.{count + 1}.jpg")
            face_img = gray[y:y + h, x:x + w] # cắt khuôn mặt ra khởi ảnh xám 
            
            save_success = cv2.imwrite(filename, face_img) # lưu ảnh xám 
            if save_success:
                count += 1
                cv2.putText(img, 'CAPTURED!', (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(f"\r Captured image {count}/5: {filename}", end='')
        
        cv2.putText(img, 'Dang chup...', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.putText(img, f'Images Captured: {count}/5', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow('image', img)
   
    # thời gian chụp khung hình ms giúp mình có thể di chuyển đầu chụp ảnh tốt hơn (ms)
    k = cv2.waitKey(1000) & 0xff
    
    if k == 27:
        print("\n ESC (thoát camera)")
        break
    elif count >= 5:
        print("\n Thu thập tập dữ liệu đã hoàn tất")
        break

# Đóng cửa sổ khi chụp xong
print("\n Thoát khỏi chương trình và dọn dẹp ")
cam.release()
cv2.destroyAllWindows()