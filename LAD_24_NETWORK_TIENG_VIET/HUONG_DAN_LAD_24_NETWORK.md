# Chương trình LAD đài phun nước — S7-1200, TIA Portal V16

Ngày 12/10/2026. Bản độc lập để dựng và chạy thử; giữ tên trong hai bảng PLC tags và DB đã gửi, chưa tích hợp vào đồ án.

## 1. Phương án được chọn và phần đã tối ưu

Bộ này gồm **24 Network chạy tuần hoàn trong OB1 và một OB100 khởi tạo**, dành cho CPU1214C AC/DC/Relay. Hình LAD dùng trực tiếp tên tag thật, ví dụ `"chon auto"`, `"nhocanh reset"`, `"daiphunnuoc".buoc_hientai`; không dùng tên thay thế tiếng Anh. Những tên sẵn có như `stop`, `rtc_ok`, `xung_reset` được giữ đúng ảnh. Tên lệnh/chân hệ thống `TON`, `RD_LOC_T`, `SR`, `MOVE`, `IN`, `Q`, `PT`, `RET_VAL` phải giữ theo Siemens.

Đây là phương án tối ưu theo mục tiêu hiện tại: ít biến mới, dễ dựng LAD, dễ theo dõi, giữ yêu cầu dừng và chống tự chạy sau lỗi/khởi động. Chưa có số đo thời gian quét và bộ nhớ từ TIA/CPU, nên không gọi là “tối ưu nhất” hoặc cam kết nhanh hơn theo tỷ lệ giảm số Network.

| Phần chỉnh | Lợi ích thực tế |
|---|---|
| Dùng `nhocanh auto`, `nhocanh reset` sẵn có | Thay hai instance R_TRIG bằng phép tính cạnh và hai bit nhớ đã có địa chỉ; cập nhật bộ nhớ ở cuối scan |
| Chỉ một cờ `khoi_tao_cho` | Bỏ cờ sao chép vòng quét đầu; khởi tạo chốt/bước tại OB100 |
| Dùng lại `huy_phep_chay` | Bỏ việc lặp toàn bộ điều kiện ở chốt quyền AUTO và điều kiện chạy |
| Dùng lại `co_van_mo` | Không thêm một biến cho phép ngõ ra; biểu thị có lệnh mở van ở bước hợp lệ |
| Đọc Q của năm TON | Bỏ năm Bool trung gian `xong_buoc1…5` khỏi thuật toán |
| MOVE chuyển bước dùng Q vừa cập nhật của TON | Bỏ so sánh bước và tiếp điểm chạy bị lặp sau TON, với điều kiện timer luôn được gọi mỗi scan |
| Giữ năm TON và hai biến bước | Dễ đối chiếu năm pha; chỉ cập nhật bước hiện tại một lần để không nhảy dồn |

Giảm từ 26 xuống 24 Network có phần do tổ chức lại sơ đồ. Lợi ích chính nằm ở các thay đổi nêu trên, không ở riêng con số 24. Có thể gom thêm nhiều rung thành ít Network hơn, nhưng không làm thuật toán ngắn hơn tương ứng.

## 2. Yêu cầu công nghệ được thực hiện

AUTO dùng giờ địa phương của PLC. Ca sáng: **06:00:00 ≤ giờ < 08:00:00**. Ca chiều tối: **17:00:00 ≤ giờ < 20:30:00**. Trong ca, bơm có lệnh ON liên tục trong cả năm bước.

| Bước | PT | Van 1 | Van 2 | Van 3 | Van 4 | Bơm |
|---|---|---|---|---|---|---|
| 1 | 10 s | Mở | Đóng | Đóng | Đóng | ON |
| 2 | 10 s | Mở | Mở | Đóng | Đóng | ON |
| 3 | 10 s | Mở | Mở | Mở | Đóng | ON |
| 4 | 10 s | Mở | Mở | Mở | Mở | ON |
| 5 | 10 s | Đóng | Mở | Đóng | Mở | ON |

Hết bước 5 trở về bước 1. Bước 0 là dừng; Q0.0–Q0.4 OFF. Dừng khi hết lịch, nhấn STOP, quá tải hoặc thiếu nước. Bổ sung dừng khẩn, lỗi RTC và bước ngoài miền 0–5. Khi có lỗi/STOP, phải khắc phục, gạt TẮT, nhấn RESET mới rồi gạt AUTO. Đây là chính sách khởi động lại được bổ sung; phiếu công nghệ chỉ quy định các điều kiện dừng.

Ngoài giờ, quyền AUTO vẫn được giữ nếu không có lỗi/STOP; ca sau tự chạy lại từ bước 1. Sau khởi động PLC với công tắc đang AUTO, không tự chạy: phải có thao tác TẮT → AUTO. Tắt công tắc bình thường rồi bật lại, nếu không có lỗi/STOP, không cần RESET.

## 3. Khai báo đúng hai bảng của bạn

Giữ nguyên **14 tên và địa chỉ nhìn thấy trong ảnh PLC tags**, kể cả hai bit nhớ M0.0/M0.1. Ảnh ghi bảng có 43 tag nhưng chỉ hiện 14 dòng; không tự xóa 29 tag chưa nhìn thấy.

DB `daiphunnuoc` có 24 trường trong ảnh. Bản mới dùng **19 trường cũ + 2 trường mới = 21 trường**. Hai trường thêm là `khoi_tao_cho : Bool` (start TRUE) và `xac_nhan_loi : Bool` (start FALSE), đều không Retain. Mọi tên trường cũ được giữ đúng, kể cả `gio plc`, `trangthai rtc`, `buoc_hientai`, `buoc_tieptheo`.

Năm trường `xong_buoc1…5` không còn dùng trong thuật toán. Chỉ xóa sau khi kiểm tra tham chiếu toàn dự án và HMI. Nếu HMI đang đọc chúng, có thể giữ tạm và gán từ Q tương ứng, hoặc đổi HMI sang đọc Q của timer; khi giữ tạm, DB có 26 trường thay vì 21.

So với bản 26 Network đã gửi, không cần thêm `vong_quet_dau`, `loi_buoc`, `cho_phep_ngo_ra`. Chức năng bảo vệ vẫn còn: so sánh bước sai trực tiếp trong `loi_hientai`; dùng `co_van_mo` cho điều kiện lệnh; dùng một cờ `khoi_tao_cho` xuyên suốt scan đầu.

Năm TON có năm instance riêng: `dem_buoc1`, `dem_buoc2`, `dem_buoc3`, `dem_buoc4`, `dem_buoc5`. Khi dựng trong OB1, để TIA tạo instance DB tương ứng; không khai báo timer thành Bool trong DB1. Khi chọn multi-instance, phải đặt trong Static của một FB được gọi mỗi scan.

**I0.4 `qua tai` và I0.5 `stop` đều bằng 1 khi bình thường.** Tên giữ nguyên theo ảnh, ghi rõ ý nghĩa trong Comment để không hiểu nhầm thành 1 = đang quá tải/đang nhấn STOP. Bảng đầy đủ nằm trong thư mục BANG_BIEN và phần bảng kèm báo cáo.

## 4. Những thứ tự bắt buộc trong LAD

OB100 RESET `nho_loi`, `nho_stop`, `da_gat_tat`, `cho_phep_auto`; MOVE 0 vào hai biến bước; SET `khoi_tao_cho`. Không đọc các I để bắt cạnh trong OB100. Hai xung được tính lại ở NW07 trước khi dùng; hai bit nhớ đầu vào được cập nhật cuối OB1. Mọi trạng thái điều khiển không Retain.

Tại NW07, dùng tiếp điểm thường đóng của bit nhớ scan trước:

```text
xung_reset = "nut reset" AND NOT "nhocanh reset"
             AND NOT khoi_tao_cho
xung_auto  = "chon auto" AND NOT "nhocanh auto"
             AND NOT khoi_tao_cho
```

Những tên không có tiền tố DB trong khung giải thích này thuộc `"daiphunnuoc"`. Hình LAD và tệp nội dung Network ghi đầy đủ toán hạng. Cuối OB1, NW24 mới gán `"nhocanh auto" := "chon auto"`, `"nhocanh reset" := "nut reset"` và RESET `khoi_tao_cho`. Nếu cập nhật bit nhớ trước NW07, sẽ làm mất cạnh. Không dùng đồng thời một R_TRIG khác cho cùng xung và không ghi đè hai Mbit ở nơi khác.

NW12 tính `huy_phep_chay` sau hai chốt lỗi/STOP. Sau đó dùng lại điều kiện này:

```text
SR cho_phep_auto:
  S  = xung_auto AND da_gat_tat AND NOT huy_phep_chay
  R1 = huy_phep_chay

tu_dong_chay = cho_phep_auto AND trong_gio AND NOT huy_phep_chay
```

SR với chân R1 ưu tiên RESET. `huy_phep_chay` đã chứa TẮT, mất điều kiện đầu vào, RTC lỗi, chốt lỗi, chốt STOP và khởi tạo. Không đưa “ngoài giờ” vào hủy quyền, vì cần tự chạy ca tiếp theo.

NW14 chuẩn bị bước tiếp theo, theo đúng thứ tự: sao chép bước hiện tại; nếu dừng đặt 0; nếu đang chạy từ bước 0 đặt 1. NW15–19 thực hiện đủ năm TON mỗi scan rồi dùng Q vừa cập nhật để cho phép MOVE sang bước kế. IN=FALSE phải reset Q/ET; không đặt timer trong nhánh bỏ qua thực thi. Điều kiện bước/chạy nối vào chân IN của TON; nếu dạng lời gọi có chân EN riêng thì EN phải luôn TRUE, không dùng EN để bỏ qua TON. Chỉ NW20 mới MOVE bước tiếp theo vào bước hiện tại trong vận hành bình thường. Các đầu ra tính sau điểm cập nhật này.

Tại NW21, `co_van_mo = tu_dong_chay AND 1 ≤ buoc_hientai ≤ 5`. Mọi bước hợp lệ trong bảng đề đều có ít nhất một van được lệnh mở. Đây là điều kiện lệnh, không xác nhận cơ khí van đã mở. Mỗi Q được ghi một lần, dùng ảnh tiến trình Q thông thường.

## 5. Dựng và thử trên TIA Portal V16

1. Lưu bản sao dự án. Dùng đúng CPU1214C AC/DC/Relay và cấu hình thực tế của bạn; số hiệu phần cứng phải khớp CPU đang dùng.
2. Khai báo PLC tags/DB theo các bảng tiếng Việt kèm theo. Giữ địa chỉ I/O. Hai bit M0.0/M0.1 không Retain; kiểm tra chúng không bị ghi qua MB0/MW0 hoặc cấu hình Clock/System memory. Nếu MB0 đang dùng chức năng đó, chuyển chức năng sang byte chưa sử dụng.
3. Tạo OB100 và 24 Network OB1 theo thứ tự bộ hình. Chỉ để một bản chương trình điều khiển các Q; không gọi đồng thời bản 36, bản 26 và bản 24.
4. Tạo năm TON instance độc lập với đúng tên `dem_buoc1…5`. Đọc trực tiếp `.Q` của từng instance trong rung chuyển bước ngay sau lời gọi TON. Không dùng kiểu TEMP cho trạng thái timer.
5. CPU đặt múi giờ UTC+7, DST tắt; chỉnh đúng ngày/giờ thực tế. RD_LOC_T trả DTL vào `"daiphunnuoc"."gio plc"`; không lẫn RD_SYS_T theo giờ hệ thống UTC.
6. Compile toàn bộ software, xử lý lỗi kiểu dữ liệu/tên/instance. Kiểm tra mỗi Q và hai Mbit chỉ có đúng các nơi ghi đã thiết kế.
7. Trong mô phỏng, cho I0.1/I0.3/I0.4/I0.5 = TRUE để biểu thị đầu vào bình thường; I0.2 = FALSE. Nếu tất cả đầu vào bằng 0 thì chương trình báo lỗi/dừng là đúng.
8. Tạo Watch table: I0.0–I0.5, M0.0/M0.1, `gio plc`, `trangthai rtc`, `rtc_ok`, `trong_gio`, `loi_hientai`, `nho_loi`, `nho_stop`, `huy_phep_chay`, `cho_phep_auto`, `tu_dong_chay`, hai bước, `khoi_tao_cho`, `xac_nhan_loi`, Q/ET năm TON và Q0.0–Q0.5.

| Ca cần chạy thử | Kết quả mong đợi |
|---|---|
| PLC vào RUN khi AUTO đã bật | Ngõ ra dừng; phải TẮT → AUTO mới có quyền |
| Giữ RESET từ lúc khởi động hoặc trước khi hết lỗi | Không tự xác nhận; phải thả rồi nhấn lại lúc TẮT và điều kiện đã tốt |
| 06:00 / 08:00 / 17:00 / 20:30 | Bắt đầu / dừng / bắt đầu / dừng; kiểm tra cả một giây trước mỗi mốc |
| Chạy ít nhất hai chu trình | Van theo 1000,1100,1110,1111,0101 (thứ tự V1–V4); bơm liên tục |
| STOP, thiếu nước, quá tải, dừng khẩn ở mỗi bước | Q0.0–Q0.4 OFF; bước 0; nhả bảo vệ không tự chạy |
| Hết giờ rồi tới ca sau, giữ AUTO và không lỗi | Dừng ngoài ca, tự bắt đầu lại bước 1 tại ca kế |
| Ghi bước -1, 6 hoặc 100 trong bản thử | Dừng và chốt lỗi, không báo chạy trong khi đứng ở bước sai |
| RTC lỗi khi AUTO, sau đó RTC tốt lại | Dừng/chốt lỗi; cần TẮT → RESET → AUTO |
| STOP đúng lúc TON đủ 10 s | Dừng ưu tiên, không bị xung timer cũ ghi đè bước 0 |

PT=10 s là thời gian đặt. Timer của bước mới bắt đầu khi scan sau đọc bước đã cập nhật, nên thời gian đầu ra chịu độ trễ vòng quét; không tuyên bố 10.000 s tuyệt đối. Không tự giảm PT để bù một chu kỳ quét chưa đo. Dùng trace trong PLCSIM/CPU khi cần đo định lượng.

Để giả lập lỗi RTC/bước, dùng bản thử có kiểm soát; RD_LOC_T hoặc chương trình có thể ghi đè giá trị vừa Modify. Chỉ đánh dấu ca đã thử khi tín hiệu thử thật sự đến network liên quan. Xóa mọi force/nhánh thử sau kiểm tra.

## 6. Khớp chương trình với ảnh bảng demo

Sáu đèn của ảnh khớp địa chỉ Q0.0 bơm, Q0.1–Q0.4 van và Q0.5 báo lỗi. Các công tắc AUTO/TẮT, đủ nước/thiếu nước, RESET, dừng khẩn khớp I0.0–I0.3. Ảnh chưa thể hiện nút STOP riêng và mô phỏng quá tải: cần bổ sung/đấu hai tín hiệu I0.5 và I0.4 theo sơ đồ thực tế, không gán cố định TRUE trong chương trình để bỏ qua bảo vệ.

| Nội dung trên ảnh demo | Cách hiển thị đúng theo đề và bản PLC này |
|---|---|
| BƯỚC 5 / 8 | Dùng `buoc_hientai / 5`; bước 0 hiển thị DỪNG |
| LỊCH CHẠY 18:00–21:00 | Ghi 06:00–08:00 và 17:00–20:30 |
| Bước 5 đang bật van 1 và 3 | Bước 5 đúng phải bật van 2 và 4, tắt van 1 và 3 |
| Bơm/van ON–OFF | Lấy Q0.0–Q0.4; đây là trạng thái lệnh, không phải cảm biến phản hồi |
| ĐỦ NƯỚC | Đọc `du nuoc`; không dùng đèn này thay liên động mức nước |
| KHÔNG LỖI | Xét `nho_loi` và điều kiện liên quan; STOP/ngoài giờ là trạng thái riêng |
| Giờ 18:30:15 | Đọc HOUR, MINUTE, SECOND từ `gio plc`, không nhập chữ cố định |
| CÒN LẠI 03 s | Nếu triển khai HMI: chọn ET của timer bước hiện tại, tính max(0,10 s−ET), làm tròn lên khi hiển thị giây |

Bản điều khiển này dùng công tắc vật lý I0.0 để chọn AUTO/TẮT theo bảng tag bạn cung cấp. Các đối tượng AUTO/TẮT trên HMI trong phương án này là hiển thị trạng thái; chưa có lệnh điều khiển HMI ghi riêng. Không cho HMI ghi trực tiếp I0.0, bước, chốt lỗi hoặc các Q. Tệp cấu hình màn hình HMI chưa được tạo trong bộ PLC này; phần liên kết trên là hướng dẫn để dựng màn hình đúng.

Giắc 24 V của bảng là giao diện tín hiệu/lệnh. Khi nối bơm thật, PLC1214C tiêu chuẩn và LAD này không thay mạch dừng khẩn, contactor và bảo vệ quá tải của động cơ. `co_van_mo` không chứng minh nước đang chảy hoặc van đã mở cơ khí.

## 7. Tài liệu tham khảo và mức kiểm chứng

Đã đối chiếu tài liệu S7-1200 do bạn gửi với cách dùng CPU, LAD, TON, RD_LOC_T và DTL. Số trang và điểm khác biệt phiên bản nằm trong `DOI_CHIEU_TAI_LIEU_VA_DEMO.md`. Các phần chốt lỗi, chống tự khởi động lại, kiểm tra bước sai và tối ưu điều kiện là thiết kế bổ sung cho yêu cầu này, không gán nhầm là ví dụ nguyên văn của tài liệu.

Bộ hình và nội dung Network là chương trình ở mức thiết kế LAD để dựng trong TIA. Chưa có trình biên dịch TIA Portal hoặc PLCSIM trong môi trường này, nên không có tệp `.ap16/.zap16` đã xác nhận chạy. Kiểm thử Python kiểm tra hành vi và phép rút gọn, không thay Compile/PLCSIM. Kết quả chi tiết và cách chạy lại nằm trong KIEM_THU.

Phần tiếp theo của bản Word/PDF có bảng biến đầy đủ, bảng 24 Network, kết quả mô hình và trọn bộ hình OB100 + 24 Network. Khi đọc hình, tên dài xuống dòng chỉ là cách trình bày; chọn đúng một toán hạng trong TIA, ví dụ `"daiphunnuoc".huy_phep_chay`.
