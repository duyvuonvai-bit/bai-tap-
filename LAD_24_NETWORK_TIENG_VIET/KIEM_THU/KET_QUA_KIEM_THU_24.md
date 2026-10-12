# Kết quả kiểm thử bản LAD 24 network

**34/34 nhóm ca đạt.**

Kiểm tra bằng mô hình Python độc lập, chưa phải Compile TIA, PLCSIM hoặc thử CPU thật.

Bản24 được so sánh với mô hình bản26 đã lưu nguyên trạng trong doi_chieu_26.py. Tên tiếng Anh trong tệp đối chứng thuộc mô hình cũ; tên tag PLC bản24 dùng đúng bảng người dùng.

Chạy lại: `python kiem_thu_lad_24.py` (Python 3.10+, không cần gói ngoài).

| Nhóm ca | Kết quả |
|---|---|
| Lịch đủ 1.440 phút | Đạt |
| Lịch đủ 86.400 giây, gồm ranh giới ca | Đạt |
| Hai chu trình, bơm liên tục, quét 1 ms | Đạt |
| Hai chu trình, bơm liên tục, quét 10 ms | Đạt |
| Hai chu trình, bơm liên tục, quét 37 ms | Đạt |
| Dừng và phục hồi du nuoc ở cả năm bước | Đạt |
| Dừng và phục hồi dung khan ok ở cả năm bước | Đạt |
| Dừng và phục hồi qua tai ở cả năm bước | Đạt |
| Dừng và phục hồi stop ở cả năm bước | Đạt |
| RESET giữ khi khởi động, AUTO=0 | Đạt |
| RESET giữ khi khởi động, AUTO=1 | Đạt |
| AUTO giữ khi khởi động | Đạt |
| RESET giữ xuyên suốt phục hồi lỗi | Đạt |
| OFF→AUTO không có lỗi | Đạt |
| Tự chạy ca kế tiếp | Đạt |
| Lỗi RTC và phục hồi | Đạt |
| Trạng thái RD_LOC_T 0 | Đạt |
| Trạng thái RD_LOC_T 1 | Đạt |
| Trạng thái RD_LOC_T -32768 | Đạt |
| Trạng thái RD_LOC_T 2 | Đạt |
| Miền RTC gio=24 | Đạt |
| Miền RTC phut=60 | Đạt |
| Miền RTC giay=60 | Đạt |
| Ghi sai bước khi đang ở bước 1 | Đạt |
| Ghi sai bước khi đang ở bước 2 | Đạt |
| Ghi sai bước khi đang ở bước 3 | Đạt |
| Ghi sai bước khi đang ở bước 4 | Đạt |
| Ghi sai bước khi đang ở bước 5 | Đạt |
| STOP trùng lúc TON đủ 10 giây | Đạt |
| So sánh 24 với 26 trên 50.000 scan ngẫu nhiên | Đạt |
| So sánh 4.096 cặp đầu vào startup với bản26 | Đạt |
| So sánh 24/26 khi chạy liên tục 150 giây | Đạt |
| Khởi động lại lúc đang ở bước 5 | Đạt |
| Bốn trạng thái M ban đầu không tạo cạnh giả | Đạt |
