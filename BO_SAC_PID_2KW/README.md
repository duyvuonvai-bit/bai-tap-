# Bộ thiết kế sạc pin 2 kW — môn Thiết kế và tinh chỉnh PID

Hoàn thiện ngày 14/10/2026. Chọn pin LiFePO₄ 16S, 51,2 V–100 Ah; nguồn 220 VAC; điện áp đặt sạc 58,0 V, giới hạn pin giả định 58,4 V; dòng CC 34,483 A. Điều khiển hai vòng PI, có giới hạn dòng/công suất, tăng dòng mềm và chống tích lũy bão hòa.

## Các tệp chính

- [Tải toàn bộ ZIP](BO_SAC_PID_2KW_TRON_BO.zip).
- [Word thuyết minh](THIET_KE_BO_SAC_PID_2KW.docx).
- [PDF thuyết minh](THIET_KE_BO_SAC_PID_2KW.pdf).
- [Mã MATLAB chạy độc lập](THIET_KE_BO_SAC_2KW.m).
- [Đọc thuyết minh trên GitHub](THUYET_MINH_BO_SAC_2KW.md).
- [Bảng 35 phương án PI](BANG_TIM_KIEM_PI.csv).
- [Hướng dẫn chạy lại Python](KIEM_CHUNG_PYTHON/README.md).

## Chạy MATLAB

Tải file .m vào một thư mục được phép ghi, mở trong MATLAB R2018b trở lên, nhấn Run toàn bộ. Không cần Control System Toolbox. Script tạo thư mục ket_qua_MATLAB và xuất bảng CSV, PNG/FIG và MAT. Ba phép thử mặc định: chuyển CC–CV, khởi động CC và bước điện áp CV; có tùy chọn thử bão hòa.

Hệ số dòng có đầu ra tính bằng **volt**, sau đó d=(vdo+ui)/Veq; không nhập trực tiếp các gain này cho bộ PI có đầu ra duty. Hệ số đã chọn: Kpi=0,75398224; Kii=75,39822369; Kpv=0,62831853; Kiv=7853,98163397; Kd=0 ở cả hai vòng. Đơn vị và phép tính đầy đủ trong thuyết minh.

## Kết quả và giới hạn

Bộ 1200/100 Hz được chọn trong 35 cặp theo hàm mục tiêu đã công bố. Trong phép thử không thêm nhiễu, vượt áp giảm từ 0,5141 V xuống 0,1209 V. Tám ca sai lệch L/C/Rb ngoài tập tinh chỉnh đều giữ Vpeak<58,4 V. Mô hình tần số rời rạc danh định cho dự trữ pha vòng dòng khoảng 72,86°, vòng áp khoảng 79,72°.

Đã chạy kiểm chứng bằng Python và kiểm tra cú pháp MATLAB 2018b bằng MISS_HIT. **Chưa thực thi bằng MATLAB/Simulink hoặc phần cứng**; không có file .slx đã xác nhận chạy. Không suy thời gian sạc thật từ phép thử 0,4 giây: E(t) là kích thích của bộ giả lập pin, không phải SOC của pin 100 Ah.

Đây là đồ án điều khiển theo mô hình đã chọn. Kiến trúc PFC/PSFB và thông số linh kiện là tính chọn sơ bộ; chưa có thiết kế driver/từ tính/nhiệt/cách điện, firmware BMS hay bộ quản lý kết thúc sạc hoàn chỉnh. Khi thay pin hoặc mạch thật cần nhận dạng lại đối tượng, điều chỉnh gain và thiết kế bảo vệ độc lập. Các tệp không chứa tên hoặc mã số sinh viên.
