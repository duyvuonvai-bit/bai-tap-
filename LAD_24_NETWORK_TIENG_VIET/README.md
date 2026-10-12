# LAD đài phun nước — 24 Network, đúng tên biến tiếng Việt

Dành cho CPU S7-1200 1214C AC/DC/Relay, dựng bằng LAD trên TIA Portal V16. Bản độc lập ngày 12/10/2026, chưa đưa vào đồ án.

## Mở tệp nào?

[Tải trọn bộ ZIP](LAD_24_NETWORK_TIENG_VIET_TRON_BO.zip) — gồm Word, PDF, PNG/SVG từng Network, bảng biến và kiểm thử.

- [Word: hướng dẫn, bảng biến và toàn bộ hình](LAD_24_NETWORK_TEN_BIEN_TIENG_VIET.docx)
- [PDF: hướng dẫn, bảng biến và toàn bộ hình](LAD_24_NETWORK_TEN_BIEN_TIENG_VIET.pdf)
- [PDF chỉ có OB100 và 24 Network, phóng to rõ](HINH_LAD/LAD_24_NETWORK_DUNG_TEN_BIEN.pdf)
- [Toàn bộ rung dạng văn bản](LAD_24_NETWORK_NOI_DUNG.txt)
- [Hướng dẫn đọc ngay trên GitHub](HUONG_DAN_LAD_24_NETWORK.md)
- [Bảng biến và phần thêm/bớt](BANG_BIEN/BANG_BIEN.md)
- [Đối chiếu tài liệu S7-1200 và ảnh demo](DOI_CHIEU_TAI_LIEU_VA_DEMO.md)
- [Kết quả kiểm thử mô hình](KIEM_THU/KET_QUA_KIEM_THU_24.md)

## Yêu cầu đã thực hiện

AUTO hoạt động 06:00–08:00 và 17:00–20:30; mốc cuối ca không bao gồm. Bơm liên tục trong chu trình. Năm bước, mỗi bước đặt TON 10 s; trạng thái van V1→V4 lần lượt 1000, 1100, 1110, 1111, 0101; hết bước 5 về bước 1. Dừng khi hết giờ, STOP, quá tải hoặc thiếu nước. Bổ sung xử lý dừng khẩn, lỗi RTC, bước sai và chống tự khởi động lại sau lỗi/khởi động PLC.

Giữ 14 tên/địa chỉ PLC nhìn thấy trong ảnh. DB giữ 19 trường đang cần, thêm hai Bool `khoi_tao_cho`, `xac_nhan_loi`. Năm `xong_buoc1…5` không cần cho thuật toán mới; chỉ xóa sau kiểm tra tham chiếu HMI/dự án. Dùng năm TON `dem_buoc1…5`, hai bit nhớ cạnh M0.0/M0.1 có sẵn. Các tên cũ `stop`, `rtc_ok` và lệnh/chân Siemens được giữ nguyên.

I0.4 `qua tai` và I0.5 `stop` bằng **1 khi bình thường**. Kiểm tra đấu nối và comment trước thử. Khi có lỗi/STOP: khắc phục → TẮT → thả rồi nhấn RESET mới → AUTO. Khi PLC vào RUN với AUTO đang bật: cần TẮT → AUTO.

Ảnh demo phải đổi `/8` thành `/5`, lịch 18–21 thành hai ca đúng đề, bước 5 sang van 2 và 4. Bản này dùng công tắc AUTO vật lý, chưa tạo dự án HMI.

## Mức kiểm chứng

**34/34 nhóm kiểm thử mô hình Python đạt**, gồm lịch đủ 86.400 giây, chu trình, bảo vệ ở năm bước, trạng thái khởi động và đối chiếu bản 26 trên 50.000 scan ngẫu nhiên. Chạy lại bằng Python 3.10+:

```bash
cd KIEM_THU
python kiem_thu_lad_24.py
```

Đây là thiết kế LAD và bộ hình để dựng chương trình, **chưa Compile bằng TIA V16, chưa chạy PLCSIM hoặc CPU thật**. Không có tệp `.ap16/.zap16` hay XML được xác nhận nhập trực tiếp. CSV là bảng tham khảo để khai báo, không cam kết định dạng import TIA. `doi_chieu_26.py` giữ mô hình cũ để so sánh; tên tiếng Anh trong tệp đó không phải tên tag của LAD mới.

24 Network gọn hơn bản 26 ở biến và điều kiện lặp; chưa có cơ sở gọi là tối ưu nhất về tốc độ/bộ nhớ CPU. Thời gian bước chịu độ trễ vòng quét, cần đo khi thử thực tế.

Các giắc demo 24 V là tín hiệu/lệnh. Khi điều khiển bơm thật, CPU tiêu chuẩn và LAD không thay mạch dừng khẩn, contactor và bảo vệ động cơ. Tài liệu hướng dẫn có phần thử cụ thể.
