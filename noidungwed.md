st.session_state: Cực kỳ quan trọng! Đây là "bộ nhớ" của ứng dụng web. Vì mỗi lần bạn nhấn nút, Streamlit sẽ chạy lại toàn bộ script, session_state giúp nó "nhớ" được các thông tin từ bước trước.

photo_count: Nhớ xem đã chụp bao nhiêu ảnh (0-5) cho nhân viên mới.

new_emp_id: Nhớ ID của nhân viên vừa được tạo ở "Bước 1".

run_camera: Biến True/False để Bật/Tắt camera điểm danh (như một công tắc điện).

last_event_time: "Bộ nhớ" cho logic Cooldown (thay vì biến toàn cục như file 03).