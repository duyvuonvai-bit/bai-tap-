# Bảng biến cho LAD 24 Network

Các tên dưới đây bám đúng hai ảnh PLC tags và DB của người dùng. Các tên đã có như `stop`, `rtc_ok`, `xung_reset` được giữ nguyên. Không dùng tên thay thế tiếng Anh trong logic mới; hai trường thêm là `khoi_tao_cho`, `xac_nhan_loi`, năm instance là `dem_buoc1` đến `dem_buoc5`.

## Phạm vi và cách đọc

- Ảnh PLC tags chỉ hiển thị **14 dòng trong bảng có 43 tag**. Giữ nguyên 14 tên/địa chỉ này; chưa có cơ sở xóa hoặc sửa 29 tag chưa nhìn thấy.
- Ảnh DB `daiphunnuoc` có **24 trường**. Bản mới dùng **19 trường gốc + 2 trường thêm = 21 trường**. Năm `xong_buoc1`…`xong_buoc5` không còn cần trong logic vì đọc trực tiếp Q của từng TON; chỉ xóa khỏi DB sau khi kiểm tra mọi tham chiếu, kể cả HMI. Nếu giữ để tương thích thì DB sẽ có 26 trường; cập nhật chúng từ Q tương ứng nếu HMI vẫn cần hiển thị.
- Tên có khoảng trắng phải chọn đúng từ danh sách tag của TIA; ví dụ `"chon auto"`, `"daiphunnuoc"."gio plc"`. Tên có gạch dưới cũng giữ đúng, ví dụ `"daiphunnuoc".buoc_hientai`.
- `TON`, `RD_LOC_T`, `MOVE`, `SR`, `IN`, `PT`, `Q`, `RET_VAL`, `Bool`, `Int`, `DTL` là tên lệnh, chân hoặc kiểu dữ liệu của Siemens; không đổi chúng thành tên tiếng Việt.
- Các CSV là bảng khai báo để đối chiếu/nhập trong TIA, **không phải tệp dự án native hoặc định dạng nhập tag đã được TIA xác nhận**. DB tối ưu không được tự suy ra địa chỉ byte từ thứ tự các dòng.

## Hai mức tín hiệu cần đọc đúng

`"qua tai"` tại I0.4 phải bằng **1 khi chưa quá tải**, bằng 0 khi bảo vệ tác động/hở mạch. `"stop"` tại I0.5 phải bằng **1 khi chưa nhấn STOP**, bằng 0 khi nhấn/hở mạch. Giữ tên theo ảnh và ghi rõ ý nghĩa trong Comment. Nếu thực tế đấu mức ngược thì phải sửa cách chuẩn hóa đầu vào trước khi chạy.

## Bộ nhớ cạnh và bộ định thời

`"nhocanh auto"` tại M0.0 và `"nhocanh reset"` tại M0.1 lưu trạng thái đầu vào của vòng quét trước. Đầu vòng quét tính hai xung; **cuối vòng quét** mới cập nhật hai Mbit từ đầu vào. Không giữ thêm hai R_TRIG cho cùng chức năng. Đặt hai Mbit không Retain và kiểm tra chúng không trùng MB0/MW0, bit clock/system hoặc nơi ghi khác trong toàn bộ dự án.

Năm TON có năm instance khác nhau: `dem_buoc1`…`dem_buoc5`. Nếu đặt trong OB1, để TIA tạo năm DB instance riêng; không khai báo chúng thành Bool trong DB toàn cục `daiphunnuoc`. Nếu dùng FB, có thể đặt thành multi-instance ở Static của FB. Mỗi TON phải được thực thi mọi vòng quét; bước không hoạt động nhận IN=FALSE để reset bộ định thời.

## Thu gọn so với bản 26 Network trước

- Giữ `khoi_tao_cho` và `xac_nhan_loi` bằng đúng tên tiếng Việt; không dùng tên thay thế bằng tiếng Anh trong LAD.
- Không cần thêm `vong_quet_dau`: dùng trực tiếp `khoi_tao_cho`, chỉ xóa cuối vòng quét đầu.
- Không cần thêm `loi_buoc`: đưa so sánh bước <0 hoặc >5 trực tiếp vào `loi_hientai`.
- Không cần thêm `cho_phep_ngo_ra`: dùng lại `co_van_mo`, ghi rõ đây là điều kiện lệnh và không phải phản hồi van.
- Dùng lại `huy_phep_chay` để tránh lặp chuỗi điều kiện dài. Ngoài giờ chỉ dừng chu trình, không tự xóa quyền AUTO cho ca sau.
- Xóa instance bắt cạnh cũ chỉ sau khi kiểm tra tham chiếu. Tên do TIA tự tạo cho instance không được coi là tên tag của người dùng.

## Khởi tạo

Mọi trạng thái điều khiển trong DB mới đặt Retain=FALSE. `khoi_tao_cho` có giá trị khởi đầu TRUE; các Bool còn lại FALSE; hai bước là 0. DTL khởi đầu chỉ là giá trị hợp lệ để khai báo, không dùng thay thời gian do RD_LOC_T đọc mới. OB100 khởi tạo trạng thái theo sơ đồ; bit `khoi_tao_cho` tiếp tục chặn quyền chạy trong vòng quét OB1 đầu, kể cả khi cấp nguồn với AUTO hoặc RESET đang giữ.

Giá trị khởi đầu không thay thế thao tác kiểm tra chương trình đang nạp: phải Compile/PLCSIM và kiểm tra thời gian thực, I/O, chốt lỗi trước khi nối tải thật.

## PLC tags: giữ đúng 14 tên và địa chỉ nhìn thấy trong ảnh

| Tên biến chính xác | Kiểu | Địa chỉ | Xử lý | Chú thích |
| --- | --- | --- | --- | --- |
| chon auto | Bool | %I0.0 | Giữ nguyên | 1 = chọn AUTO; 0 = TẮT. |
| du nuoc | Bool | %I0.1 | Giữ nguyên | 1 = đủ nước; 0 = thiếu nước hoặc hở mạch. |
| nut reset | Bool | %I0.2 | Giữ nguyên | Nút NO; 1 = đang nhấn RESET. |
| dung khan ok | Bool | %I0.3 | Giữ nguyên | 1 = mạch dừng khẩn bình thường; 0 = tác động hoặc hở mạch. |
| qua tai | Bool | %I0.4 | Giữ nguyên | Tên giữ theo ảnh. Tiếp điểm NC: 1 = CHƯA quá tải; 0 = quá tải hoặc hở mạch. |
| stop | Bool | %I0.5 | Giữ nguyên | Tên giữ theo ảnh. Nút NC: 1 = CHƯA nhấn STOP; 0 = nhấn STOP hoặc hở mạch. |
| bom nuoc | Bool | %Q0.0 | Giữ nguyên | Lệnh điều khiển bơm; không phải phản hồi bơm thật. |
| van 1 | Bool | %Q0.1 | Giữ nguyên | Lệnh mở van 1. |
| van 2 | Bool | %Q0.2 | Giữ nguyên | Lệnh mở van 2. |
| van 3 | Bool | %Q0.3 | Giữ nguyên | Lệnh mở van 3. |
| van 4 | Bool | %Q0.4 | Giữ nguyên | Lệnh mở van 4. |
| den bao loi | Bool | %Q0.5 | Giữ nguyên | Đèn báo lỗi đã chốt. STOP được lưu riêng; không tự coi STOP là lỗi thiết bị. |
| nhocanh auto | Bool | %M0.0 | Giữ, dùng lại | Giá trị chon auto của vòng quét trước; chỉ cập nhật cuối OB1; không Retain. |
| nhocanh reset | Bool | %M0.1 | Giữ, dùng lại | Giá trị nut reset của vòng quét trước; chỉ cập nhật cuối OB1; không Retain. |

## DB daiphunnuoc: 21 trường dùng trong bản 24 Network

| Tên trường chính xác | Kiểu | Giá trị khởi đầu | Retain | Xử lý | Chú thích |
| --- | --- | --- | --- | --- | --- |
| gio plc | DTL | DTL#1970-01-01-00:00:00.0 | FALSE | Giữ nguyên tên | Ngày giờ cục bộ do RD_LOC_T trả về; dùng các thành phần HOUR, MINUTE, SECOND. |
| trangthai rtc | Int | 0 | FALSE | Giữ nguyên tên | Mã RET_VAL của RD_LOC_T; đọc mới trước khi tính rtc_ok. |
| rtc_ok | Bool | FALSE | FALSE | Giữ nguyên tên | Đọc RTC thành công và giờ/phút/giây thuộc miền hợp lệ; không chứng minh đồng hồ đã đặt đúng giờ. |
| ca_sang | Bool | FALSE | FALSE | Giữ nguyên tên | Lịch sáng: từ 06:00:00 đến trước 08:00:00. |
| ca_toi | Bool | FALSE | FALSE | Giữ nguyên tên | Lịch chiều tối: từ 17:00:00 đến trước 20:30:00. |
| trong_gio | Bool | FALSE | FALSE | Giữ nguyên tên | ca_sang OR ca_toi. |
| an_toan | Bool | FALSE | FALSE | Giữ nguyên tên | du nuoc AND dung khan ok AND qua tai AND stop; cả bốn phải bằng 1. |
| loi_hientai | Bool | FALSE | FALSE | Giữ nguyên tên | Thiếu nước, dừng khẩn, quá tải, RTC lỗi khi chọn AUTO, hoặc buoc_hientai ngoài 0..5. |
| nho_loi | Bool | FALSE | FALSE | Giữ nguyên tên | Chốt lỗi; chỉ xóa khi đủ điều kiện xac_nhan_loi. |
| nho_stop | Bool | FALSE | FALSE | Giữ nguyên tên | Chốt yêu cầu STOP; chỉ xóa khi đủ điều kiện xac_nhan_loi. |
| xung_reset | Bool | FALSE | FALSE | Giữ nguyên tên | Cạnh lên nut reset từ bộ nhớ nhocanh reset; chặn trong vòng quét khởi tạo. |
| xung_auto | Bool | FALSE | FALSE | Giữ nguyên tên | Cạnh lên chon auto từ bộ nhớ nhocanh auto; chặn trong vòng quét khởi tạo. |
| da_gat_tat | Bool | FALSE | FALSE | Giữ nguyên tên | Đã quan sát chon auto = 0 sau khởi động; dùng cuộn SET và xóa khi khởi tạo. |
| huy_phep_chay | Bool | FALSE | FALSE | Giữ nguyên tên | TẮT, mất an toàn, RTC lỗi, lỗi/STOP đã chốt hoặc đang khởi tạo. Ngoài giờ không hủy quyền AUTO. |
| cho_phep_auto | Bool | FALSE | FALSE | Giữ nguyên tên | Quyền AUTO đã chốt sau thao tác TẮT rồi AUTO hợp lệ. |
| tu_dong_chay | Bool | FALSE | FALSE | Giữ nguyên tên | Quyền AUTO hợp lệ, trong giờ và không huy_phep_chay. |
| buoc_hientai | Int | 0 | FALSE | Giữ nguyên tên | 0 = dừng; 1..5 = bước hợp lệ; ngoài 0..5 phải chốt lỗi. |
| buoc_tieptheo | Int | 0 | FALSE | Giữ nguyên tên | Bước tính cho cuối vòng quét; chỉ commit một lần sau đủ năm TON. |
| co_van_mo | Bool | FALSE | FALSE | Giữ nguyên tên | Điều kiện lệnh: tu_dong_chay AND buoc_hientai trong 1..5. Không phải xác nhận van thật đã mở. |
| khoi_tao_cho | Bool | TRUE | FALSE | Thêm | OB100 SET; giữ bằng 1 suốt vòng quét OB1 đầu để chặn xung/quyền chạy; RESET sau cập nhật bộ nhớ cạnh cuối OB1. |
| xac_nhan_loi | Bool | FALSE | FALSE | Thêm | xung_reset AND NOT chon auto AND an_toan AND rtc_ok AND NOT loi_hientai. |

## Đối chiếu 24 trường DB gốc và 2 trường bổ sung

| Tên trường chính xác | Nguồn | Thay đổi | Ghi chú |
| --- | --- | --- | --- |
| gio plc | Có trong ảnh DB | Giữ đúng tên | Ngày giờ cục bộ do RD_LOC_T trả về; dùng các thành phần HOUR, MINUTE, SECOND. |
| trangthai rtc | Có trong ảnh DB | Giữ đúng tên | Mã RET_VAL của RD_LOC_T; đọc mới trước khi tính rtc_ok. |
| rtc_ok | Có trong ảnh DB | Giữ đúng tên | Đọc RTC thành công và giờ/phút/giây thuộc miền hợp lệ; không chứng minh đồng hồ đã đặt đúng giờ. |
| ca_sang | Có trong ảnh DB | Giữ đúng tên | Lịch sáng: từ 06:00:00 đến trước 08:00:00. |
| ca_toi | Có trong ảnh DB | Giữ đúng tên | Lịch chiều tối: từ 17:00:00 đến trước 20:30:00. |
| trong_gio | Có trong ảnh DB | Giữ đúng tên | ca_sang OR ca_toi. |
| an_toan | Có trong ảnh DB | Giữ đúng tên | du nuoc AND dung khan ok AND qua tai AND stop; cả bốn phải bằng 1. |
| loi_hientai | Có trong ảnh DB | Giữ đúng tên | Thiếu nước, dừng khẩn, quá tải, RTC lỗi khi chọn AUTO, hoặc buoc_hientai ngoài 0..5. |
| nho_loi | Có trong ảnh DB | Giữ đúng tên | Chốt lỗi; chỉ xóa khi đủ điều kiện xac_nhan_loi. |
| nho_stop | Có trong ảnh DB | Giữ đúng tên | Chốt yêu cầu STOP; chỉ xóa khi đủ điều kiện xac_nhan_loi. |
| xung_reset | Có trong ảnh DB | Giữ đúng tên | Cạnh lên nut reset từ bộ nhớ nhocanh reset; chặn trong vòng quét khởi tạo. |
| xung_auto | Có trong ảnh DB | Giữ đúng tên | Cạnh lên chon auto từ bộ nhớ nhocanh auto; chặn trong vòng quét khởi tạo. |
| da_gat_tat | Có trong ảnh DB | Giữ đúng tên | Đã quan sát chon auto = 0 sau khởi động; dùng cuộn SET và xóa khi khởi tạo. |
| huy_phep_chay | Có trong ảnh DB | Giữ đúng tên | TẮT, mất an toàn, RTC lỗi, lỗi/STOP đã chốt hoặc đang khởi tạo. Ngoài giờ không hủy quyền AUTO. |
| cho_phep_auto | Có trong ảnh DB | Giữ đúng tên | Quyền AUTO đã chốt sau thao tác TẮT rồi AUTO hợp lệ. |
| tu_dong_chay | Có trong ảnh DB | Giữ đúng tên | Quyền AUTO hợp lệ, trong giờ và không huy_phep_chay. |
| buoc_hientai | Có trong ảnh DB | Giữ đúng tên | 0 = dừng; 1..5 = bước hợp lệ; ngoài 0..5 phải chốt lỗi. |
| buoc_tieptheo | Có trong ảnh DB | Giữ đúng tên | Bước tính cho cuối vòng quét; chỉ commit một lần sau đủ năm TON. |
| xong_buoc1 | Có trong ảnh DB | Bỏ khỏi logic 24 Network | Chỉ xóa trường sau khi kiểm tra tham chiếu chéo/HMI; nếu còn nơi dùng thì giữ tạm và cập nhật nơi dùng trước. |
| xong_buoc2 | Có trong ảnh DB | Bỏ khỏi logic 24 Network | Chỉ xóa trường sau khi kiểm tra tham chiếu chéo/HMI; nếu còn nơi dùng thì giữ tạm và cập nhật nơi dùng trước. |
| xong_buoc3 | Có trong ảnh DB | Bỏ khỏi logic 24 Network | Chỉ xóa trường sau khi kiểm tra tham chiếu chéo/HMI; nếu còn nơi dùng thì giữ tạm và cập nhật nơi dùng trước. |
| xong_buoc4 | Có trong ảnh DB | Bỏ khỏi logic 24 Network | Chỉ xóa trường sau khi kiểm tra tham chiếu chéo/HMI; nếu còn nơi dùng thì giữ tạm và cập nhật nơi dùng trước. |
| xong_buoc5 | Có trong ảnh DB | Bỏ khỏi logic 24 Network | Chỉ xóa trường sau khi kiểm tra tham chiếu chéo/HMI; nếu còn nơi dùng thì giữ tạm và cập nhật nơi dùng trước. |
| co_van_mo | Có trong ảnh DB | Giữ đúng tên | Điều kiện lệnh: tu_dong_chay AND buoc_hientai trong 1..5. Không phải xác nhận van thật đã mở. |
| khoi_tao_cho | Chưa có trong ảnh DB | Thêm | OB100 SET; giữ bằng 1 suốt vòng quét OB1 đầu để chặn xung/quyền chạy; RESET sau cập nhật bộ nhớ cạnh cuối OB1. |
| xac_nhan_loi | Chưa có trong ảnh DB | Thêm | xung_reset AND NOT chon auto AND an_toan AND rtc_ok AND NOT loi_hientai. |

## Năm instance TON riêng do TIA tạo

| Tên instance | Lệnh | PT | Yêu cầu | Chú thích |
| --- | --- | --- | --- | --- |
| dem_buoc1 | TON | T#10s | Một instance riêng, gọi mỗi vòng quét | IN = tu_dong_chay AND buoc_hientai = 1; Q cho phép chuyển sang bước 2. |
| dem_buoc2 | TON | T#10s | Một instance riêng, gọi mỗi vòng quét | IN = tu_dong_chay AND buoc_hientai = 2; Q cho phép chuyển sang bước 3. |
| dem_buoc3 | TON | T#10s | Một instance riêng, gọi mỗi vòng quét | IN = tu_dong_chay AND buoc_hientai = 3; Q cho phép chuyển sang bước 4. |
| dem_buoc4 | TON | T#10s | Một instance riêng, gọi mỗi vòng quét | IN = tu_dong_chay AND buoc_hientai = 4; Q cho phép chuyển sang bước 5. |
| dem_buoc5 | TON | T#10s | Một instance riêng, gọi mỗi vòng quét | IN = tu_dong_chay AND buoc_hientai = 5; Q cho phép chuyển sang bước 1. |

