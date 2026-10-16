# Bảng linh kiện và công dụng — cấu hình 20S / 84 V

Đã xác nhận: dùng bo STM32G474RET6 hàn sẵn của người dùng, không mua chip/bo MCU khác. Theo hình đề xuất, 20 cell được hiểu là 20S Li-ion 4,2 V/cell, điện áp cuối sạc 84 V. Dòng CC thiết kế tối đa 23,81 A để đạt 2 kW tại 84 V; dòng cài đặt thực tế phải không vượt mức của cell và BMS. Theo quyền tự chọn thông số người dùng đã cho: đặt mục tiêu pin50 Ah, BMS dòng sạc liên tục≥30 A; đây chưa phải thông số đã xác minh của pin thật.

Các giá trị trong cột “Thông số” là đầu vào thiết kế và tiêu chí tính chọn, chưa thay thế mã linh kiện/footprint đã được đối chiếu datasheet. Chưa có BOM đặt hàng hoàn chỉnh.

| Khối / linh kiện | Số lượng dự kiến | Công dụng | Thông số / trạng thái |
|---|---:|---|---|
| Bo STM32G474RET6 đã có | 1 | Tạo bốn PWM PSFB đồng bộ, xử lý ADC, CC/CV, trạng thái lỗi | Không mua lại; đã có link nhưng trang bị403, cần ảnh/pinout để biết đầu cắm và chân bị chiếm dụng |
| Cầu chì AC | 1 | Ngắt dòng sự cố từ lưới | Phải phối hợp dòng khởi động, I²t và khả năng cắt; chưa chốt chỉ theo dòng định mức |
| MOV và cầu chì/giải pháp bảo vệ MOV | 1 bộ | Hạn chế xung quá áp đầu vào | Theo lưới và tiêu chí thử surge, chưa chốt mã |
| Cuộn chống nhiễu, tụ X/Y | 1 bộ | Lọc nhiễu dẫn; đưa dòng nhiễu về đường phù hợp | Tụ đúng cấp an toàn; giá trị và bố trí cần thử EMI |
| Điện trở hạn dòng nạp tụ + relay bypass | 1 bộ | Hạn chế dòng nạp C_BUS khi đóng điện | Ví dụ R=47 Ω có thể nhận năng lượng cỡ 75 J khi nạp 940 µF lên400 V; phải chọn theo xung, không chọn chỉ theo W liên tục |
| Cầu chỉnh lưu đầu vào | 1 | Đổi AC thành DC chỉnh lưu cho PFC | Dòng đầu vào khoảng 10 A ở220 VAC; chọn theo dòng RMS/đỉnh, nhiệt, surge |
| IC điều khiển PFC và mạch phụ | 1 bộ | Giữ bus DC và tạo dạng dòng vào gần sin | Chưa chốt IC và sơ đồ chân; không thể chỉ vẽ một MOSFET rồi coi có PFC |
| MOSFET PFC | Theo cấu trúc đã chọn | Đóng cắt cuộn cảm boost | Nhóm650 V là điểm khởi đầu; phải tính tổn hao, Qg/Coss, nhiệt |
| Diode boost PFC | 1 chức năng tương đương | Truyền năng lượng L_PFC vào bus, chặn dòng ngược | Thường xét SiC650 V; mã/dòng chưa chốt |
| L_PFC | 1 | Tích và truyền năng lượng PFC | Khảo sát560 µH tại65 kHz; Isat nóng mục tiêu≥22 A, còn tính lõi/dây/nhiệt |
| C_BUS điện phân | 2 dự kiến | Đệm năng lượng nhấp nhô100 Hz | Khảo sát2×470 µF/450 V; phải kiểm dòng ripple, nhiệt, tuổi thọ, hold-up |
| Tụ film sát cầu H | Theo layout | Khép vòng dòng chuyển mạch cao tần, giảm ký sinh bus | 4,7 µF/630 V trên ảnh là giá trị có thể khảo sát; không thay cho tụ đệm100 Hz |
| MOSFET cầu H Q1–Q4 | 4 | Tạo điện áp xoay chiều cao tần trên sơ cấp T1 | Nhóm650 V; chưa chốt mã từ tổn hao/Coss/body-diode và yêu cầu PSFB |
| Driver hai kênh cách ly | 2 | Khuếch đại xung và cách ly bốn cổng MOSFET | UCC21520 là ứng viên; pinout, DIS, DT, nguồn và package cần xác minh |
| Nguồn lái nổi/cách ly | 3 miền | Cấp nguồn đúng source cho hai khóa trên và hai khóa dưới | +V_A/SW_A, +V_B/SW_B, +V_L/DC_AM; chưa chọn module |
| Điện trở cổng, kéo G–S, kẹp cổng | 4 bộ | Điều chỉnh tốc độ chuyển mạch, giữ tắt, hạn chế VGS | Rg phải đo hiệu chỉnh; không chốt10/22 Ω từ ảnh như giá trị tối ưu |
| T1 biến áp cao tần | 1 | Truyền2 kW và cách ly sơ–thứ cấp | Tỷ số25:8 được kiểm tra như một ứng viên; chưa xác định lõi, vòng/dây, Lm, Llk hoặc cách điện |
| D1–D4 chỉnh lưu thứ cấp | 4 diode tương đương | Chỉnh lưu điện áp thứ cấp thành xung một chiều | Điện áp thứ cấp lý tưởng tới134,4 V khi bus420 V, n=0,32; phải có dự phòng ringing, chọn loại cao tần và tản nhiệt |
| L_OUT | 1 | Giảm gợn dòng sạc | Đề xuất khảo sát100 µH thay33 µH, dòng liên tục≥24 A, Isat nóng mục tiêu≥35 A; còn thiết kế từ tính |
| C_OUT | 1 cụm | Lọc gợn đầu ra, chịu dòng tụ trong quá độ | 220+220+680=1.120 µF/160 V trên ảnh là ứng viên; kiểm ESR/ripple, đáp ứng và năng lượng khi nối pin |
| Shunt đo dòng L | 1 | Phản hồi nhanh vòng dòng, phân biệt dòng L với dòng pin | Chọn R cùng gain/offset mạch đo; 0,5 mΩ trong ảnh chỉ tạo11,9 mV ở23,81 A |
| Shunt đo dòng pin | 1 | Đo dòng thực đi vào pin phục vụ CC/CV/kết thúc sạc | Tách vị trí với shunt L bởi nút tụ đầu ra; có thể nghiên cứu gộp nếu đổi thuật toán |
| Khuếch đại đo dòng phía cao | 2 nếu dùng2 shunt | Đưa điện áp shunt về ADC | INA241 là ứng viên; chưa chốt hậu tố/gain/REF. Không dùng INA240 ở common-mode84 V vì vượt dải80 V |
| Bộ chia áp chính xác + bảo vệ ADC | 1 bộ | Đo84 V, cung cấp tín hiệu OVP | 390k/10k cho tỷ lệ1/40,84 V→2,10 V; cần ngắt/chặn cấp ngược khi MCU mất nguồn |
| NTC và điện trở chia áp | 3 bộ | Đo nhiệt MOSFET/tản nhiệt, biến áp/cuộn cảm | Chọn thống nhất NTC10k/B3950 và Rtrên10k để25°C≈1,65 V; không lẫn NTC100k trong ảnh |
| Bảo vệ nhanh sơ cấp + OVP/OTP + chốt lỗi | 1 hệ | Khóa driver độc lập khi sự cố, kiểm soát khởi động lại | Đo dòng đầu ra không thay bảo vệ shoot-through/quá dòng sơ cấp; ngưỡng phải có phân tích sai số |
| Khối nối pin, cầu chì DC, chống dòng ngược | 1 bộ | Xử lý cắm/rút pin, đảo cực và nạp tụ đầu ra | Tụ1.120 µF tích khoảng3,95 J ở84 V; BMS không mặc nhiên thay chức năng này |
| Nguồn phụ cách ly | 1 hệ | Cấp logic, driver, quạt và bảo vệ | Chưa chốt flyback/module và các đầu ra riêng; một mass12 V chung không đủ lái high-side |
| CAN/RS485 nếu BMS yêu cầu | Theo đúng BMS | Trao đổi trạng thái/giới hạn sạc | Chọn đúng giao thức; một transceiver phù hợp mỗi đầu, không ghép nối tiếp hai transceiver như hình |
| Tản nhiệt, quạt, cách điện, vỏ, đầu nối | 1 bộ | Tản tổn hao và bảo đảm lắp ráp/cách điện | Tính theo công suất tổn hao, nhiệt môi trường và điện áp làm việc, chưa chốt mã |

## Điều kiện để biến bảng này thành BOM đặt hàng và PCB

- Đã nhận link Shopee của bo nhưng truy cập bị403; cần ảnh/pinout đúng biến thể để chốt đầu cắm, nguồn và PWM/ADC/FAULT. Không suy ra vị trí chân header từ số chân IC LQFP64.
- Chọn mục tiêu50 Ah/BMS sạc≥30 A theo yêu cầu tự ước lượng; khi dùng pin thật phải kiểm thông số cell/BMS. Không tự gán50 Ah cho20 viên pin bất kỳ.
- Cần chọn mã thực tế và datasheet cho linh kiện công suất/từ tính/driver/nguồn. Các chân và giá trị sai trong ảnh phải được vẽ lại thành netlist CAD có thể kiểm tra.
- Sau đó mới chốt footprint, bố trí cách điện, bề rộng đồng/busbar, kiểm ERC/DRC, xuất Gerber/drill/BOM và bản vẽ lắp linh kiện. ERC/DRC không thay thử nghiệm cách điện, nhiệt và chức năng bảo vệ.
