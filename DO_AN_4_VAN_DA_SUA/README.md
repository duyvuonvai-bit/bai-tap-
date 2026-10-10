# Đồ án điều khiển và giám sát đài phun nước 4 van

Bản chỉnh sửa ngày **10/10/2026**, đối chiếu trực tiếp bản đồ án và phiếu giao đề tài được cung cấp. Bản công khai đã ẩn thông tin cá nhân; không kèm hai tài liệu gốc.

Thuyết minh gồm **50 trang**, mục lục đủ **72 đề mục/tiểu mục**, danh mục **9 hình** và **31 bảng**. Phụ lục C đối chiếu từng nhóm nội dung của phiếu giao với vị trí và trạng thái trong báo cáo. Mục lục và danh mục có liên kết nội bộ, số trang đã kiểm tra theo PDF. Trong Word, Ctrl+A → F9 cập nhật trường số trang; khi thêm/xóa đề mục hoặc hình/bảng, cần đồng bộ các danh mục tương ứng.

**Tải trọn bộ:** [DO_AN_4_VAN_AN_DANH_TRON_BO.zip](DO_AN_4_VAN_AN_DANH_TRON_BO.zip). Mở tệp trên GitHub rồi chọn **Download raw file**.

## Nên mở tệp nào?

| Tệp / thư mục | Nội dung |
|---|---|
| [Do_an_4_van_DA_SUA_AN_DANH.pdf](Do_an_4_van_DA_SUA_AN_DANH.pdf) | Bản đọc và in của thuyết minh đã sửa |
| [Do_an_4_van_DA_SUA_AN_DANH.docx](Do_an_4_van_DA_SUA_AN_DANH.docx) | Bản Word có thể chỉnh sửa |
| [BAO_CAO_DANH_GIA_VA_SUA_LOI.md](BAO_CAO_DANH_GIA_VA_SUA_LOI.md) | Các lỗi quan trọng, đối chiếu yêu cầu và phần còn phải kiểm chứng |
| [BAN_VE_NGUYEN_LY_A0.pdf](BAN_VE_NGUYEN_LY_A0.pdf) | 7 tờ A0 nằm ngang: dòng chảy, nguồn, cắt cứng bơm, I/O, cấp coil van, chu trình và giao diện dự kiến |
| [PLC/Fountain_Auto_4Van.scl](PLC/Fountain_Auto_4Van.scl) | Nguồn SCL gồm các khối RTC, trình tự, DB và OB |
| [PLC/HUONG_DAN_TIA_HMI.md](PLC/HUONG_DAN_TIA_HMI.md) | Cách nhập nguồn vào TIA, ánh xạ I/O/DB, cấu hình đồng hồ và HMI |
| [HINH](HINH) | 7 sơ đồ nguyên lý mới và các đồ thị kết quả mô hình; có bản PNG, SVG hoặc PDF để chèn, sửa hoặc in |
| [KIEM_THU](KIEM_THU) | Mô hình Python, ca kiểm tra, kết quả chạy và dữ liệu vết mô phỏng độc lập |

## Yêu cầu đã dùng để sửa

- AUTO đọc RTC; vận hành từ **06:00 đến trước 08:00** và **17:00 đến trước 20:30** hằng ngày.
- Bơm có lệnh ON liên tục trong thời gian chạy chu trình.
- Năm trạng thái van, theo thứ tự YV1–YV4: **1000 → 1100 → 1110 → 1111 → 0101**, mỗi bước đặt 10 s rồi lặp lại.
- Dừng khi hết lịch, nhấn STOP, quá tải bơm hoặc thiếu nước.
- Bố cục thuyết minh theo 3 chương của phiếu giao; bổ sung bản vẽ A0 và nội dung thử nghiệm có phân biệt phần đã làm với phần chưa thực hiện.

Thiết kế bổ sung E-STOP, chốt dừng/lỗi và quy tắc chống tự chạy lại. Sau STOP/lỗi: **TẮT → khắc phục nguyên nhân → nhấn RESET mới → AUTO**. RESET không tự bật bơm. Khi hết lịch bình thường, hệ chờ khung giờ tiếp theo nếu vẫn được cho phép AUTO. Cấu hình cơ sở chỉ có AUTO/TẮT; HMI giám sát chỉ đọc, không điều khiển tay qua vị trí TẮT.

## Sử dụng nguồn PLC

Đọc [hướng dẫn TIA/HMI](PLC/HUONG_DAN_TIA_HMI.md) trước khi nhập nguồn. Tạo project trên đúng CPU/firmware, thêm `.scl` vào `External source files` rồi sinh các khối. Kiểm tra OB1, OB100, timer IEC, DB không lưu giữ trạng thái, múi giờ UTC+7, địa chỉ I/O và offset DB_HMI. Biên dịch trên TIA Portal và thử bằng PLCSIM hoặc tải giả trước khi nạp cho hệ thống có động lực.

Nguồn SCL **chưa được biên dịch bằng TIA Portal**. Kết quả 31/31 ca kiểm tra là của mô hình hành vi Python độc lập; không phải kết quả Siemens PLCSIM hoặc đo trên PLC. Chưa có project HMI EasyBuilder Pro hay kết quả truyền thông thiết bị thật.

## Giới hạn cần giữ khi nộp và triển khai

- Các hình và 7 tờ A0 là **sơ đồ nguyên lý thiết kế**. Chưa chốt đầy đủ thiết bị, định mức, terminal, bảo vệ, cáp và bản vẽ thi công.
- Ảnh giao diện là hình thiết kế, không phải ảnh chụp màn hình HMI đang chạy. Các bit đầu ra chỉ xác nhận **lệnh bơm/lệnh van**, chưa xác nhận cơ cấu hoạt động thực tế.
- Bơm, van, nguồn và các tải phụ cần đối chiếu đúng catalogue/model. Phép tính thủy lực và ngân sách nguồn dựa trên giả thiết được ghi trong thuyết minh.
- Tra cứu trực tiếp nguồn nhà sản xuất bị proxy môi trường chặn; danh mục nguồn là hướng đối chiếu, chưa phải thông số đã xác minh độc lập.
- Đã đối chiếu thêm tài liệu học tập S7-1200 có sẵn trong kho, gồm các ví dụ RTC và timer; tài liệu này không thay kết quả biên dịch trên phiên bản TIA đang dùng.
- Cần hoàn thành TIA/PLCSIM, project HMI, kiểm tra cắt cứng, đo thời gian, dòng điện và thủy lực để có kết quả thực nghiệm. Không đổi các mục “chưa thực hiện” thành “đạt” nếu chưa có bằng chứng.

## Tải từ GitHub

Mở tệp cần lấy trong nhánh chứa bộ hồ sơ này, chọn **Download raw file** (biểu tượng tải xuống). Với Word hoặc PDF, lưu tệp về máy trước khi mở. Có thể dùng **Code → Download ZIP** để tải toàn bộ nhánh; giải nén rồi mở thư mục hồ sơ. Các liên kết trên dùng tệp trong cùng thư mục GitHub, không phụ thuộc liên kết artifact hoặc sandbox của cuộc trò chuyện.

