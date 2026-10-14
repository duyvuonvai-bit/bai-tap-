# Chạy lại kiểm chứng

Dùng Python 3.12 với các phiên bản trong requirements.txt để tái lập môi trường đã chạy. Mã dùng NumPy 2 trở lên vì có np.trapezoid.

```bash
python -m pip install -r requirements.txt
python tune_and_validate.py
python frequency_check.py
```

Chạy trong thư mục này. Kết quả mới nằm trong ket_qua_chay_lai để không ghi đè dữ liệu gốc của báo cáo. Lệnh thứ nhất chạy 35 cặp PI, 4 kịch bản danh định cho mỗi bộ điều khiển và 8 tổ hợp sai lệch tham số. Lệnh thứ hai dùng hệ số đã chọn để tính ổn định tín hiệu nhỏ rời rạc.

Mô hình là bộ biến đổi trung bình với nguồn pin E(t) đặt trước; không phải mô phỏng SOC/điện hóa, mạch chuyển mạch hoặc firmware. MATLAB được giao là bản triển khai tương ứng không thêm nhiễu, chưa được thực thi bằng MATLAB tại môi trường tạo gói này.
