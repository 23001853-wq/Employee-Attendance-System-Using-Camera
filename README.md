# Quá trình hoàn thiện phần nhận diện khuôn mặt

## 1. Thu thập dữ liệu khuôn mặt
- Chạy file `01_face_dataset.py`.
- Nhập tên thư mục nhân viên (ví dụ: nhanvienduy, nhanvienduc) và user id tương ứng.
- Hệ thống sẽ tự động chụp và lưu ảnh khuôn mặt vào đúng thư mục trong `dataset/`.
- Mỗi nhân viên nên thu thập từ 50–200 ảnh với nhiều góc mặt, ánh sáng khác nhau.

## 2. Huấn luyện mô hình nhận diện
- Chạy file `02_face_training.py`.
- Script sẽ tự động duyệt toàn bộ ảnh trong các thư mục con của `dataset/`.
- Mỗi ảnh phải có tên theo định dạng: `User.<id>.<số thứ tự>.jpg`.
- Mô hình được huấn luyện và lưu vào `trainer/trainer.yml`.

## 3. Nhận diện khuôn mặt và điểm danh
- Chạy file `03_face_recognition.py`.
- Khi camera nhận diện được khuôn mặt, hệ thống sẽ dựa vào id để hiển thị đúng tên nhân viên (cấu hình trong biến `names`).
- Nếu khuôn mặt không khớp, sẽ hiển thị là "unknown".

## 4. Lưu ý
- Đảm bảo file `haarcascade_frontalface_default.xml` nằm cùng thư mục với các script.
- Khi thêm nhân viên mới, cần thu thập ảnh và huấn luyện lại mô hình.
- Có thể chỉnh sửa biến `names` trong file nhận diện để hiển thị đúng tên nhân viên theo id.

---

