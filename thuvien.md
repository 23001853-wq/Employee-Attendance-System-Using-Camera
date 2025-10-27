streamlit as st: Nhập thư viện Streamlit, công cụ chính để tạo giao diện web.

pandas as pd: Dùng để hiển thị dữ liệu (lấy từ SQL) dưới dạng bảng (DataFrame) đẹp mắt.

pyodbc, datetime, os, cv2, numpy, PIL.Image: Các thư viện quen thuộc từ 3 file trước (kết nối CSDL, xử lý thời gian, xử lý file, và xử lý ảnh).

shutil: Một thư viện mới, dùng để xóa toàn bộ thư mục (sử dụng trong chức năng "Xóa nhân viên").

time: Dùng để tạo độ trễ ngắn (time.sleep) giúp giao diện mượt mà hơn.
Nhập thư viện PIL (Python Imaging Library), một thư viện rất mạnh để mở và xử lý nhiều định dạng ảnh khác nhau.
lbph (Local Binary Patterns Histograms) thuật toán xử lý nhận diện ảnh nâng cao
🐍 Ngôn ngữ: Python
Đây là ngôn ngữ lập trình chính, là "bộ não" điều khiển và "chất keo" gắn kết tất cả các thư viện khác lại với nhau. Mọi file code (01_face_dataset.py, 02_face_training.py, 03_face_recognition.py, và file Streamlit) đều được viết bằng Python.

👁️ Nhận diện khuôn mặt: OpenCV
Đây là thư viện thị giác máy tính (Computer Vision), là "đôi mắt" của dự án. Trong OpenCV, bạn đã dùng 2 thuật toán con:

Haar Cascade (haarcascade_...xml):

Tác dụng: Phát hiện khuôn mặt (Face Detection).

Nhiệm vụ: Trả lời câu hỏi: "Trong bức ảnh này, khuôn mặt nằm ở đâu?". Nó là thứ vẽ ra các hình chữ nhật (bounding box) xung quanh các khuôn mặt.

Dùng ở đâu: File 01 (để tìm mặt và cắt) và File 03/Streamlit (để tìm mặt trước khi nhận diện).

LBPH (cv2.face.LBPH...):

Tác dụng: Nhận diện khuôn mặt (Face Recognition).

Nhiệm vụ: Trả lời câu hỏi: "Khuôn mặt này là của ai (ID 1, 2, hay 38)?". Đây là thuật toán so sánh khuôn mặt bạn đưa vào với dữ liệu nó đã học (file trainer.yml).

Dùng ở đâu: File 02 (để học và tạo trainer.yml) và File 03/Streamlit (để dự đoán ID).

🖥️ Giao diện Web: Streamlit
Tác dụng: Xây dựng giao diện web.

Nhiệm vụ: Biến dự án của bạn từ một file chạy trên terminal (cửa sổ đen) thành một trang web tương tác đẹp mắt. Nó tạo ra các menu (st.sidebar), nút bấm (st.button), bảng dữ liệu (st.dataframe), biểu đồ (st.bar_chart), và hiển thị video camera (st.image).

🗄️ Cơ sở dữ liệu: Microsoft SQL Server
Tác dụng: Lưu trữ dữ liệu vĩnh viễn.

Nhiệm vụ: Là cái "kho" chứa toàn bộ thông tin quan trọng. Nếu bạn tắt máy, dữ liệu vẫn còn đó.

Bảng Employees: Lưu ID, Tên, Phòng ban của nhân viên.

Bảng Attendance: Lưu lịch sử chấm công (ngày, giờ vào, giờ ra).

🔌 Kết nối CSDL: PyODBC
Tác dụng: Cầu nối giữa Python và SQL Server.

Nhiệm vụ: Python (code của bạn) không thể "nói chuyện" trực tiếp với SQL Server (cơ sở dữ liệu). PyODBC là "người phiên dịch" cho phép Python gửi các lệnh (như SELECT, INSERT, UPDATE) đến SQL Server và nhận kết quả trả về.

📊 Xử lý dữ liệu: Pandas & NumPy
Hai thư viện này là bộ đôi "xử lý số liệu".

Pandas:

Tác dụng: Xử lý và phân tích dữ liệu dạng bảng.

Nhiệm vụ: Rất quan trọng trong trang web Streamlit. Khi PyODBC lấy dữ liệu từ SQL về, Pandas nhận lấy và nạp vào một cấu trúc gọi là DataFrame (giống như một bảng Excel trong code). Nó giúp bạn lọc, tính toán (WorkHours = TimeOut - TimeIn), và thống kê (groupby) dữ liệu một cách cực kỳ dễ dàng.

NumPy:

Tác dụng: Làm toán ma trận (ảnh).

Nhiệm vụ: Đây là nền tảng của OpenCV. Mọi khung hình (img), mọi ảnh xám (gray) thực chất đều là một mảng NumPy (một ma trận chứa các con số). Lệnh np.array(ids) trong File 02 cũng dùng NumPy để chuyển danh sách ID thành định dạng mà recognizer.train() có thể hiểu.

🖼️ Xử lý ảnh: Pillow (PIL)
Tác dụng: Mở và xử lý file ảnh phụ trợ.

Nhiệm vụ: Trong dự án của bạn, nó được dùng trong file huấn luyện (File 02 và hàm train_model trong Streamlit) với lệnh Image.open(imagePath).convert('L'). Đây là một cách rất đáng tin cậy để mở mọi loại file ảnh (JPG, PNG...) và đảm bảo chúng được chuyển sang ảnh xám ('L') một cách đồng nhất, trước khi chuyển đổi sang NumPy array cho OpenCV.