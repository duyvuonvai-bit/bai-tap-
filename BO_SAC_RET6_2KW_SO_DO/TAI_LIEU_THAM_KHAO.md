# Hướng dẫn và tài liệu tham khảo: bộ sạc Full Bridge PWM 2 kW dùng STM32G474RET6

Cập nhật: 16/10/2026. Phương án đang nghiên cứu: bus DC khoảng 400 V sau PFC; tầng DC–DC cách ly; đầu ra 58 V, giới hạn dòng khoảng 34,5 A. Các giá trị này là mục tiêu thiết kế, chưa phải kết quả thử mạch.

## 1. Nên bắt đầu từ những nguồn nào?

| Mục đích | Nguồn nên đọc | Tình trạng kiểm tra |
|---|---|---|
| Tạo xung bằng STM32G474RET6 | Ví dụ HRTIM_Basic_MultiplePWM của ST | Đã tải và đọc README |
| Dead-time và dừng xung khi quá dòng | Ví dụ HRTIM_CBC_Deadtime của ST | Đã tải README và mã C |
| Đồng bộ ADC với PWM, ngắt bốn ngõ ra | Ví dụ HRTIM_Buck_Boost của ST | Đã tải và đọc README |
| Tổ chức vòng kín nguồn số | Buck_VoltageMode_SW của ST | Đã tải README và mã C |
| Ví dụ Full Bridge PWM cùng họ MCU | STM32G474_HSFB_Current_Mode_Test | Đã đọc README; chưa chạy phần cứng |
| Thiết kế công suất bộ sạc 2 kW | TI PMP8740 | Có liên kết hãng; chưa truy cập được nội dung trong phiên |
| Cách tính một tầng PSFB | TI SLUA560 và tài liệu UCC28950 | Có liên kết hãng; chưa truy cập được nội dung trong phiên |

Không nguồn nào trong các ví dụ STM32 đã đọc chứng minh rằng bộ mạch đang thiết kế đã đạt 2 kW. Mạch, firmware và hệ số bộ điều khiển vẫn cần thiết kế theo tải thực tế.

## 2. Mã mẫu chính thức ST: dùng được để học trên bo RET6 tự thiết kế

Các liên kết dưới đây cố định tại commit `140db648b016ba49b05ca790b5b66e3477807839` của kho chính thức ST. Có thể chuyển project sang bo RET6 tự thiết kế; không bắt buộc mua NUCLEO. Cần cấu hình lại chân, clock, ADC, mức tích cực của tín hiệu lỗi và trạng thái khởi động.

### 2.1. Tạo nhiều xung HRTIM

[ST — HRTIM_Basic_MultiplePWM](https://github.com/STMicroelectronics/STM32CubeG4/tree/140db648b016ba49b05ca790b5b66e3477807839/Projects/NUCLEO-G474RE/Examples/HRTIM/HRTIM_Basic_MultiplePWM)

README xác nhận STM32G474RET6 và các cặp TA1/TA2 ở PA8/PA9, TD1/TD2 ở PB14/PB15. Dùng mẫu để học khởi tạo HRTIM, đặt chu kỳ, compare và xuất xung ra chân.

**Điểm phải đổi:** mẫu gốc tạo hai tần số 100 kHz và 133 kHz. Không đưa nguyên bốn xung này vào cầu H. Hai nhánh cầu của bộ sạc phải có lịch phát xung đồng bộ, dead-time và cân bằng volt–giây trên biến áp. Bo điều khiển đang vẽ dùng cặp A/B; mẫu này dùng A/D, nên phải đổi cả chân và timer tương ứng.

### 2.2. Dead-time và giới hạn dòng từng chu kỳ

[ST — HRTIM_CBC_Deadtime](https://github.com/STMicroelectronics/STM32CubeG4/tree/140db648b016ba49b05ca790b5b66e3477807839/Projects/NUCLEO-G474RE/Examples_LL/HRTIM/HRTIM_CBC_Deadtime)

Mẫu phát xung bù TD1/TD2 ở PB14/PB15. Sự kiện quá dòng EEV5/EEV8 nhận qua PB8/PB9; mẫu minh họa tắt đầu ra khi quá dòng mà không tự kích nhánh bù. Các tên cấu hình cần tìm trong mã là `TIMER_PWM_FREQ` và `DEADTIME_IN_NS`.

Dùng để học cơ chế HRTIM; không lấy một giá trị dead-time của mẫu làm giá trị cuối cho MOSFET, driver và biến áp khác. Giới hạn dòng từng chu kỳ cũng không thay thế bảo vệ lỗi nghiêm trọng có khóa giữ và trình tự khởi động lại.

### 2.3. Lấy mẫu ADC đồng bộ và ngắt bốn PWM

[ST — HRTIM_Buck_Boost](https://github.com/STMicroelectronics/STM32CubeG4/tree/140db648b016ba49b05ca790b5b66e3477807839/Projects/B-G474E-DPOW1/Examples_MIX/HRTIM/HRTIM_Buck_Boost)

README mô tả TC1/TC2/TD1/TD2; ADC được kích vào giữa thời gian ON; FAULT2 ở PA15, mức thấp, tắt bốn PWM. Đây là phần nên học khi thiết kế đo dòng và ngắt xung của bộ sạc.

**Điểm phải đổi:** phần công suất là buck–boost không đảo, không có biến áp Full Bridge. Mức tích cực và chân FAULT của mẫu khác bo RET6 hiện tại. Không sao chép nguyên BOM, cách phát xung hay pinout của mẫu.

### 2.4. Điều khiển vòng kín và kiểm tra đáp ứng tần số

[ST — Buck_VoltageMode_SW](https://github.com/STMicroelectronics/STM32CubeG4/tree/140db648b016ba49b05ca790b5b66e3477807839/Projects/B-G474E-DPOW1/Applications/Digital_Power/Buck_VoltageMode_SW)

README xác nhận STM32G474RET6, nguồn vào 12 VDC, đầu ra buck 3,3 V; thuật toán chạy trên CPU, có file `SW_3p3z_controller.h`, project STM32CubeIDE và `.ioc`. README dẫn **AN5496** cho cách sử dụng và đo đạc. Mẫu HRTIM ở mục 2.1 dẫn **AN4539 — HRTIM cookbook**.

Học cách tổ chức đọc ADC, tính bộ bù và cập nhật PWM; không sử dụng nguyên hệ số bộ bù 3p3z cho bộ sạc 58 V. Chế độ sạc CC/CV, giới hạn dòng, chống tích phân bão hòa và chuyển vòng điều khiển cần triển khai riêng.

## 3. Ví dụ cộng đồng gần yêu cầu Full Bridge PWM

[STM32G474_HSFB_Current_Mode_Test](https://github.com/derlucae98/STM32G474_HSFB_Current_Mode_Test/tree/53bdfc406f564f079c4fcbb0cf97ffbbfdb02468)

README mô tả những bước đầu điều khiển số **hard-switched Full Bridge DC–DC** bằng NUCLEO-G474RE. Tác giả trình bày thử bộ bù 2p2z bằng nối DAC–ADC, chưa gắn tầng công suất, rồi so sánh đáp ứng tần số với mô phỏng. Đây là ví dụ sát cấu trúc của thầy và cùng dòng MCU, phù hợp để học cách thử bộ điều khiển trước khi nối công suất.

Giới hạn: đã đọc README, chưa biên dịch/chạy phần cứng; không có căn cứ để coi repo này là bộ sạc 2 kW hoàn thiện.

Một repo có tên [STM32G474RE-Full-Bridge-Phase-Shift-Complementary-PWM](https://github.com/ahmedfotoh/STM32G474RE-Full-Bridge-Phase-Shift-Complementary-PWM) cũng tồn tại tại commit `c29e4c1905af85a4d6e28e266604441b4230d223`, nhưng chỉ thấy tệp nén `.rar`, không có README. Chưa kiểm tra firmware trong tệp nén; chỉ cung cấp như đầu mối tìm hiểu, không dùng nó để xác nhận dạng xung đúng.

## 4. Tài liệu công suất của hãng cần đọc khi chốt thiết kế

Trong phiên này, truy cập trực tiếp các PDF/trang TI và ST bên dưới bị proxy trả 403. Chúng là liên kết tài liệu hãng để mở bằng trình duyệt; nội dung PDF chưa được kiểm tra trong môi trường này.

- [TI PMP8740 — thiết kế tham chiếu bộ sạc 2 kW](https://www.ti.com/tool/PMP8740). Tìm sơ đồ, BOM, báo cáo thử và phần tính toán. Phải đọc đúng dải đầu vào/đầu ra của bản thiết kế; không mặc định trùng 58 V/34,5 A của đồ án.
- [TI SLUA560 — UCC28950 600-W, Phase-Shifted, Full-Bridge Application Note](https://www.ti.com/lit/an/slua560/slua560.pdf). Dùng làm đầu mối học cách tính PSFB. Mẫu 600 W không thể nâng lên 2 kW chỉ bằng thay MOSFET hoặc tăng dòng đặt.
- [TI TIDM-02000 — điều khiển số PSFB](https://www.ti.com/tool/TIDM-02000). Tham khảo cấu trúc điều khiển; nền tảng C2000 khác STM32, mã không nạp trực tiếp vào G474.
- [TI UCC28950 datasheet](https://www.ti.com/lit/ds/symlink/ucc28950.pdf). Đọc khi tìm hiểu PSFB, ZVS và chỉnh lưu đồng bộ. Nếu STM32 đảm nhiệm điều chế thì không mặc định cần mua thêm UCC28950.
- [TI UCC21520 datasheet](https://www.ti.com/lit/ds/symlink/ucc21520.pdf). Nguồn cần đối chiếu trước khi chốt chân driver, DIS, DT, nguồn nổi và layout. **Chân 8 và công thức/giới hạn điện trở DT chưa xác minh được bằng PDF hãng trong phiên; không chốt PCB driver từ dữ liệu thư viện đơn lẻ.**
- [ST STM32G474RE datasheet](https://www.st.com/resource/en/datasheet/stm32g474re.pdf). Đối chiếu chân, nguồn, reset/boot và đặc tính điện MCU.
- [ST AN4539 — HRTIM cookbook](https://www.st.com/resource/en/application_note/an4539-hrtim-cookbook-stmicroelectronics.pdf). Số hiệu tài liệu được xác nhận từ README mẫu ST đã đọc; PDF chưa đọc được.
- [ST B-G474E-DPOW1 — trang bo nguồn số và tài liệu](https://www.st.com/en/evaluation-tools/b-g474e-dpow1.html). Tìm AN5496 trong mục tài liệu. Đây là nền tảng học buck/buck–boost, không phải mẫu mạch Full Bridge 2 kW.

## 5. Full Bridge PWM và PSFB khác nhau ở đâu?

| Nội dung | Full Bridge điều chỉnh độ rộng xung | Phase-shifted Full Bridge — PSFB |
|---|---|---|
| Đại lượng điều khiển chính | Độ rộng khoảng áp dương/âm lên sơ cấp | Độ lệch pha giữa hai nhánh cầu |
| Phát xung | Cần thiết kế lịch đóng cắt đúng; vẫn phải có dead-time | Hai nhánh thường gần 50% duty, có dead-time |
| Tổn hao chuyển mạch | Có thể là hard switching | Có thể đạt ZVS trong miền tải thích hợp |
| Điều kiện để chọn | Phù hợp yêu cầu PWM và mô hình của thầy | Cần tính thêm điều kiện ZVS, dòng tuần hoàn, mất duty hiệu dụng |

Sơ đồ cầu H bốn khóa và biến áp chưa xác định được phương pháp điều chế. Không thể đạt ZVS chỉ bằng đổi sang chương trình lệch pha. Với đồ án này nên giữ PWM theo yêu cầu của thầy, rồi đánh giá PSFB như một phương án cải thiện hiệu suất ở 2 kW nếu được lựa chọn kiến trúc.

## 6. Video và cách học theo thứ tự

Chưa có video cụ thể được mở/xem để xác minh. Các liên kết sau là **trang tìm kiếm video**, không phải video đã kiểm tra:

- [Tìm video ST về STM32G4 HRTIM và nguồn số](https://www.youtube.com/results?search_query=STMicroelectronics+STM32G4+HRTIM+digital+power)
- [Tìm video TI về thiết kế PSFB](https://www.youtube.com/results?search_query=Texas+Instruments+phase+shifted+full+bridge+design)
- [Tìm video TI PMP8740 2 kW battery charger](https://www.youtube.com/results?search_query=TI+PMP8740+2kW+battery+charger)

Thứ tự thực hành: (1) SWD, clock và ADC của bo RET6; (2) bốn xung đồng bộ, dead-time, trạng thái khởi động và ngắt lỗi khi chưa nối công suất; (3) driver và nguồn nổi; (4) mô phỏng vòng dòng/vòng áp CC/CV; (5) thử tầng DC–DC bằng nguồn DC điện áp thấp giới hạn dòng và tải thử; (6) hoàn thiện biến áp, lọc, bảo vệ, cách điện, tản nhiệt và PCB trước khi đánh giá ở 400 V/2 kW.

Đây là trình tự kiểm chứng các phần của thiết kế. Bộ tài liệu hiện tại không cung cấp một mạch điện lưới 2 kW đã nghiệm thu để hàn xong là cấp điện.
