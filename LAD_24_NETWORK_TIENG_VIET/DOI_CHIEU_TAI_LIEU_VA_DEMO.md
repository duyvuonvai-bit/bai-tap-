# Đối chiếu LAD 24 Network với tài liệu S7-1200, đề giao và ảnh demo

Ngày rà soát: **12/10/2026**. Đây là phần kiểm tra bổ sung cho bộ LAD riêng, chưa ghép vào đồ án.

## Tài liệu đã mở và kiểm tra

Tệp người dùng gửi lại: **Tai lieu huong dan S7-1200_07_2021.pdf**, 59 trang. Đã mở PDF, trích nội dung và xem trực tiếp các trang liên quan. Số trang bên dưới là số trang PDF, trùng số in ở cuối trang. Tệp có tiêu đề đầu trang “Thainguyen Automation”; không coi đây là tài liệu chuẩn lệnh của Siemens chỉ vì có hình TIA Portal.

SHA-256 của tệp được đối chiếu: `29f931fc4585e53f880832967caf46edba3f08228a7f12141a12c8b539d180a1`.

| Trang | Nội dung nhìn thấy trong tài liệu | Áp dụng cho chương trình đài phun nước |
| --- | --- | --- |
| 1 | Bàn thí nghiệm dùng CPU Siemens S7-1200 1214C, 14 đầu vào số, 10 đầu ra số. | Phù hợp họ CPU và đủ số I/O cho bảng 6 DI, 6 DO của người dùng. Không chứng minh đúng model/firmware của thiết bị đang nối. |
| 6 | Hướng dẫn ghi rõ **“Mở phần mềm TIA Portal V14”**, kèm biểu tượng V14. | Đây là mẫu thao tác trên V14. Bộ LAD đang chuẩn bị nhằm dựng trong **TIA Portal V16**; không gọi PDF này là hướng dẫn V16. |
| 7 | Chọn CPU **1214C AC/DC/RLY**, mã **6ES7 214 1BG40 0XB0**; khai báo PLC tags; mở Main [OB1]. | Cách tổ chức tag và chương trình OB1 phù hợp. Chọn đúng mã và firmware của CPU thực tế khi dựng dự án V16; không sao chép lựa chọn phần cứng chỉ từ hình mẫu. |
| 9–10 | Nạp chương trình, tìm CPU và theo dõi trạng thái chương trình khi Online. | Có thể dùng làm mẫu thao tác kiểm tra sau khi dựng lại LAD. Những trang này không xác nhận bộ 24 Network đã được Compile hoặc chạy trên PLC. |
| 11 | Ví dụ đèn giao thông dùng TON, chân IN/PT/Q/ET và instance riêng; đọc trực tiếp Q của bộ định thời trong tiếp điểm. | Hỗ trợ cách dùng năm TON riêng và đọc `dem_buoc1.Q`…`dem_buoc5.Q`, không bắt buộc sao chép thêm năm Bool `xong_buoc`. Thời gian 20 s/3 s của bài mẫu phải thay bằng 10 s theo đề đài phun. |
| 16 | Bài chuông giảng đường có **RD_LOC_T**, đầu ra kiểu **DTL**, chân **RET_VAL** và **OUT**. | Phù hợp việc dùng `"daiphunnuoc"."gio plc"` kiểu DTL và `"daiphunnuoc"."trangthai rtc"` kiểu Int. Đây là mẫu đọc thời gian, không phải lịch đài phun nước. |
| 17 | So sánh các thành phần **HOUR**, **MINUTE** của thời gian DTL; có khối MOVE trong LAD. | Phù hợp cách tạo ca sáng/ca tối và cập nhật bước. Các mốc 7 giờ, 7 giờ 50, 7 giờ 55 trong mẫu không được dùng thay lịch của đề giao. |
| 27 | Ví dụ chuông dùng nhiều TON với DB instance khác nhau, thời gian PT và tiếp điểm đọc Q. | Củng cố yêu cầu mỗi TON có bộ nhớ riêng. Không dùng chung một instance cho năm bước. |

Chương trình mẫu ở trang 16 đặt điều kiện RUN/STOP trước chân EN của RD_LOC_T. Bản đài phun mới **đọc RTC mỗi vòng quét rồi mới tính `rtc_ok` và lịch chạy**, để giá trị thời gian/trạng thái đọc không bị cũ khi chuyển chế độ hoặc xử lý lỗi. Đây là lựa chọn thiết kế cho bài đài phun, không phải sao chép nguyên rung của bài chuông.

## Những điều PDF không đủ để xác nhận

- Các trang RTC nêu trên **không có bảng giải thích mã RET_VAL 0 và 1**. Không dẫn PDF này làm bằng chứng rằng cả hai mã đều thành công. Bản thiết kế hiện dùng `(trangthai rtc = 0) OR (trangthai rtc = 1)`; khi dựng trên TIA V16, chọn RD_LOC_T và mở **F1** để kiểm tra bảng mã đúng phiên bản lệnh/CPU, đặc biệt trường hợp giờ mùa hè. Tại Việt Nam đặt giờ địa phương UTC+7, tắt DST và kiểm tra đồng hồ CPU đúng thực tế.
- Cách dùng hai bit `"nhocanh auto"`, `"nhocanh reset"` để tính cạnh rồi cập nhật cuối vòng quét là phần thiết kế bổ sung, **không gán cho PDF là hướng dẫn nguyên mẫu này**. Cần kiểm tra trong dự án V16 rằng M0.0/M0.1 không trùng byte clock/system memory, MB0/MW0 hoặc nơi ghi khác.
- PDF không chứng minh hành vi khởi tạo bằng OB100, trạng thái Retain, thứ tự ưu tiên SR hay miền dữ liệu DTL của đúng cấu hình V16 đang dùng. Tra F1 của từng lệnh và Compile dự án thực tế. Với SR dùng chân **R1**, giữ ngữ nghĩa ưu tiên reset trong thiết kế; không đổi sang khối có ưu tiên khác chỉ vì ký hiệu gần giống.
- Kiểu của các toán hạng so sánh HOUR/MINUTE/SECOND, kiểu Int của trạng thái RTC và khai báo DB phải được TIA kiểm tra. Chọn toán hạng từ danh sách tag đúng kiểu, không sao chép chữ hiển thị trong hình rồi coi như đã biên dịch.
- Năm TON và mô hình kiểm thử độc lập không chứng minh thời gian thực đúng tuyệt đối 10.000 s. Thời điểm cập nhật có sai số theo vòng quét; cần theo dõi khi chạy PLCSIM/PLC.

Không thay logic chỉ để giống mọi địa chỉ của PDF: tài liệu chứa nhiều bài thí nghiệm khác nhau, mỗi bài gán I/O khác. Với bài này, hai bảng tag/DB người dùng gửi là căn cứ đặt tên và địa chỉ.

## Đối chiếu đúng yêu cầu công nghệ

| Hạng mục | Theo đề giao, dùng trong bản LAD | Ghi chú |
| --- | --- | --- |
| Lịch sáng | 06:00:00 ≤ thời gian < 08:00:00 | Đúng 08:00 phải dừng. |
| Lịch chiều/tối | 17:00:00 ≤ thời gian < 20:30:00 | Đúng 20:30 phải dừng. |
| Chu trình | 5 bước; mỗi bước 10 s; hết bước 5 lặp về bước 1 khi còn điều kiện chạy | Không đổi thành 8 bước theo ảnh minh họa. |
| Bước 1 | Van 1 mở; van 2, 3, 4 đóng | Chuỗi theo thứ tự van 1–4: `1000`. |
| Bước 2 | Van 1, 2 mở; van 3, 4 đóng | `1100`. |
| Bước 3 | Van 1, 2, 3 mở; van 4 đóng | `1110`. |
| Bước 4 | Cả bốn van mở | `1111`. |
| Bước 5 | Van 2, 4 mở; van 1, 3 đóng | `0101`. |
| Bơm | Chạy liên tục trong chu trình đang được phép hoạt động | Không ngắt bơm giữa hai bước hợp lệ. |
| Dừng | Hết giờ, nhấn STOP, bơm quá tải, mức nước thấp | Dừng khẩn, chốt lỗi RTC/bước sai và quy tắc khởi động lại là phần bổ sung thiết kế. |

## Đối chiếu ảnh demo của người dùng

Ảnh demo là cơ sở bố trí giao diện/đèn/giắc. Những dòng hiển thị chưa khớp đề phải sửa trong cấu hình HMI, không dùng chúng để thay đổi yêu cầu công nghệ.

| Chi tiết trong ảnh demo | Đối chiếu và cách xử lý |
| --- | --- |
| Hiển thị **BƯỚC 5/8** | Đề có 5 bước. HMI cần hiển thị bước hiện tại trên tổng **5**, ví dụ 5/5; khi dừng hiển thị DỪNG hoặc 0/5. |
| Hiển thị lịch **18:00–21:00** | Thay bằng hai ca **06:00–08:00** và **17:00–20:30**. Không sửa LAD theo lịch trên ảnh demo. |
| Ở hình “bước 5”, van 1 và 3 sáng, van 2 và 4 tắt | Đó là tổ hợp `1010`, khác bước 5 của đề. HMI/đèn thực tế ở bước 5 phải cho van **2 và 4** sáng, van **1 và 3** tắt. |
| Đèn BƠM Q0.0; VAN 1…4 Q0.1…Q0.4; BÁO LỖI Q0.5 | Khớp địa chỉ ngõ ra trong bảng người dùng. Giữ nguyên tên biến `"bom nuoc"`, `"van 1"`…`"van 4"`, `"den bao loi"`. Đèn thể hiện lệnh; chưa phải phản hồi cơ khí của bơm/van. |
| Công tắc AUTO/TẮT, công tắc ĐỦ NƯỚC/THIẾU NƯỚC, RESET, DỪNG KHẨN | Có thể đối chiếu với I0.0, I0.1, I0.2, I0.3 theo bảng tag. Mức “khỏe = 1” của các mạch bảo vệ vẫn phải kiểm tra khi đấu dây. |
| Ảnh chưa thể hiện riêng ngõ thử quá tải I0.4 và nút STOP I0.5 | Phải bổ sung tiếp điểm bảo vệ/nút STOP thật hoặc công tắc thử đúng chức năng trong mô hình. **Không gán cố định hai đầu vào bằng 1** để bỏ qua hai điều kiện dừng của đề. |
| Giắc tín hiệu ghi 24 VDC | Dùng cho tín hiệu/lệnh và thiết bị phù hợp điện áp, không nối trực tiếp động cơ 220 VAC vào giắc 24 VDC. Khi nối bơm thật phải qua mạch động lực và bảo vệ phù hợp. |

Việc dùng đèn để mô phỏng giúp thử thứ tự chu trình và điều kiện dừng. Khi chuyển sang thiết bị thật, tín hiệu mức nước/quá tải/dừng khẩn phải lấy từ thiết bị tương ứng; không để chế độ mô phỏng làm mất bảo vệ của bơm thật.

## Thử trên TIA V16 trước khi dùng

1. Tạo/chọn đúng CPU 1214C AC/DC/Rly và firmware; khai báo đúng hai bảng tên biến của bộ LAD. Không bật clock/system memory đè lên M0.0/M0.1.
2. Dựng OB100, OB1 và năm TON có instance riêng; bảo đảm không còn chương trình cũ cùng ghi các Q. Compile cả phần cứng và phần mềm, kiểm tra mọi cảnh báo liên quan.
3. Kiểm tra đồng hồ địa phương và mã RD_LOC_T bằng F1/quan sát Online. Thử ranh giới 06:00, 08:00, 17:00, 20:30.
4. Thử 5 tổ hợp van, 10 s mỗi bước, bơm liên tục, STOP/quá tải/thiếu nước ở từng bước; thử cấp nguồn khi AUTO hoặc RESET đang giữ; thử bước sai -1/6 và phục hồi lỗi.
5. Đối chiếu HMI với đúng `buoc_hientai` và các Q. Thử riêng I0.4/I0.5 chuyển từ 1 xuống 0, không bỏ qua chỉ vì ảnh demo chưa vẽ đủ hai phần này.

Bộ tài liệu đã rà logic và có kiểm thử mô hình độc lập. **Chưa có dự án TIA native trong tệp đã gửi để xác nhận Compile/PLCSIM thành công**; PDF mẫu và hình LAD không thay thế kết quả đó.
