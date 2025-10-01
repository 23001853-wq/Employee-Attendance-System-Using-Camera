
### 🏷️ Tên nhóm
    Nhóm 28
### 📝 Tên dự án
    Hệ thống điểm danh nhân viên bằng camera
### 👥 Thành viên nhóm
| 👤 Họ và tên 🧑‍🎓  | 🆔 Mã sinh viên 🧾 | 🐙 Tên GitHub 🔗     |
|------------------|---------------------|---------------------|
| [Nguyễn Hữu Duy]      | [23001853]    | [23001853-wq]      |


### 🗒️ Tóm tắt
Dự án xây dựng hệ thống điểm danh nhân viên bằng camera dựa trên công nghệ nhận diện khuôn mặt. Camera sẽ tự động phát hiện và nhận diện nhân viên khi họ đi qua, thay thế việc chấm công bằng thẻ hoặc ký tên. Hệ thống giúp tiết kiệm thời gian, hạn chế gian lận và tăng tính tự động hóa trong quản lý nhân sự.
### 🎯 Bối cảnh
Hiện nay nhiều công ty dùng thẻ từ hoặc vân tay để điểm danh, nhưng còn bất tiện và dễ xảy ra gian lận hộ. Ứng dụng AI để check-in bằng camera giúp nâng cao hiệu quả, tiết kiệm chi phí, đồng thời là ví dụ điển hình cho việc áp dụng AI vào thực tế, gần gũi và có giá trị ứng dụng cao.
### 🚀 Kế hoạch
Thu thập dữ liệu: chụp ảnh khuôn mặt nhân viên (3–5 ảnh/nhân viên).

Tiền xử lý: phát hiện và cắt khuôn mặt bằng OpenCV/Dlib.

Xây dựng mô hình: sử dụng thư viện face_recognition để tạo embeddings và so khớp.

Triển khai camera real-time: nhận diện qua webcam, check-in khi nhận diện thành công.

Ghi log: lưu thông tin nhân viên + thời gian vào file CSV/DB.

Demo: chạy thử nghiệm với nhóm thành viên.
### 📚 Tài liệu tham khảo
Python libraries: OpenCV, face_recognition, numpy, pandas.
Dataset thử nghiệm: Labeled Faces in the Wild (LFW).
Documentation: face_recognition GitHub.
Tutorial: Real-time Face Recognition with OpenCV.