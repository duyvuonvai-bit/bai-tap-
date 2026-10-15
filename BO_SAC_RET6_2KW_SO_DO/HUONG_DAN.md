# Bộ sạc Full Bridge 2 kW — bo STM32G474RET6 tự thiết kế

Bản tiếp tục ngày 16/10/2026. Tài liệu dành cho đồ án và phát triển nguyên mẫu. Đã có sơ đồ nguyên lý bo điều khiển, bảng chân, BOM và bản vẽ hệ thống; chưa có PCB/Gerber, firmware hoàn chỉnh hay thử nghiệm bộ sạc 400 V/2 kW.

## 1. Phương án đang dùng

| Đại lượng | Thông số mục tiêu / giả thiết |
|---|---|
| Công suất ra lớn nhất | 2.000 W |
| Đầu vào toàn bộ sạc | 220 VAC; qua chỉnh lưu và PFC để tạo bus khoảng 400 VDC |
| Đầu vào tầng Full Bridge | Bus DC; chỉnh lưu 220 VAC đơn thuần không tạo bus ổn áp 400 V |
| Pin của phương án đồ án | LiFePO₄ 16S, 51,2 V danh định, 100 Ah; cần BMS phù hợp |
| Điện áp CV đang chọn | 58,0 V; phải phù hợp thông số cell/BMS thực tế, không mặc định dùng cho mọi pin 16S |
| Dòng CC giới hạn đang chọn | 2.000 / 58 ≈ 34,48 A |
| Điều khiển | STM32G474RET6, LQFP64; HRTIM, ADC, ngắt lỗi phần cứng |
| Cấu trúc công suất | Cầu H 4 MOSFET → biến áp cao tần → cầu diode → LC → pin |

Giới hạn dòng 34,48 A nghĩa là công suất nhỏ hơn 2 kW khi điện áp pin dưới 58 V. Muốn giữ 2 kW khi điện áp pin thay đổi phải dùng chế độ công suất không đổi (CP) và tăng giới hạn dòng ở điện áp thấp; đó không còn là giai đoạn CC với dòng 34,48 A cố định. Bản này không yêu cầu chế độ CP.

Tỷ số Ns/Np ≈ 0,20, L ≈ 100 µH và C ≈ 1.000 µF được giữ làm giá trị khởi đầu từ mô hình trước. Chúng chưa xác định lõi, số vòng, khe hở, dòng bão hòa, tổn hao hay dòng ripple của linh kiện thật. Không mua biến áp hoặc cuộn cảm chỉ theo ba con số này.

## 2. Cấu trúc và cách điều khiển đúng

Q1/Q2 là hai khóa cùng nhánh A; Q3/Q4 cùng nhánh B. Q1 + Q4 đặt điện áp dương lên sơ cấp; Q2 + Q3 đặt điện áp âm. Các khoảng điện áp bằng 0 và đường dòng hồi tiếp phụ thuộc cách điều chế và dòng trong mạch. Không được bật đồng thời hai khóa cùng nhánh; phải có dead-time và trạng thái tắt khi lỗi.

Với mô hình lý tưởng ở chế độ dòng liên tục: **Vra ≈ (Ns/Np) × Vbus × Dhiệu_dụng**. Tại 400 V, Ns/Np = 0,20 và Vra = 58 V, Dhiệu_dụng ≈ 0,725. Đây là tổng tỷ lệ thời gian có xung điện áp chỉnh lưu trong chu kỳ, không phải lệnh đặt duty 72,5% cho từng transistor. Với cách định nghĩa một chu kỳ gồm hai xung đối xứng, mỗi xung chiếm khoảng 0,3625 chu kỳ, trước khi tính sụt áp và dead-time.

**Full Bridge PWM thông thường:** điều chỉnh độ rộng hai xung dương/âm đối xứng. Cần cân bằng volt–giây để tránh lệch từ thông và bão hòa biến áp. Đây là phương án nền để bám yêu cầu PWM của đề.

**PSFB:** hai nhánh thường hoạt động gần duty 50%; thay đổi độ lệch pha giữa hai nhánh để điều chỉnh năng lượng. ZVS phụ thuộc điện cảm, điện dung khóa, tải và thời gian chuyển mạch. PSFB là phương án cần nghiên cứu khi tối ưu tổn hao 2 kW; không thể chỉ đổi tên hoặc lấy mã PSFB nạp vào phần cứng chưa tính chọn.

Vòng dòng điều khiển dòng cuộn cảm; vòng áp tạo giới hạn dòng khi tới mức CV. Phải có giới hạn duty, khởi động mềm, chống tích lũy tích phân và xử lý lỗi. Hai shunt giúp phân biệt dòng cuộn cảm với dòng thực vào pin; dòng tụ làm hai giá trị khác nhau trong quá độ. Hệ số PI của bài ổn định nhiệt độ không dùng cho bộ sạc này. Hệ số mô phỏng sạc trước đây cũng cần hiệu chỉnh theo mạch và chu kỳ lấy mẫu thật.

## 3. Thay NUCLEO bằng bo RET6 tối thiểu

Giữ STM32G474RET6 nhưng bỏ ST-LINK tích hợp, USB, HMI và các mạch không phục vụ điều khiển nguồn. Dùng ST-LINK rời qua SWD; ban đầu dùng HSI/PLL, điện trở/tụ 0805. Đây là cách giảm linh kiện; chưa có báo giá đủ để khẳng định tự làm một bo luôn rẻ hơn bo thương mại sau chi phí PCB, bộ nạp và dụng cụ hàn.

LQFP64 bước chân 0,5 mm cần PCB đúng footprint, flux và kiểm tra cầu thiếc. Không dùng breadboard cho bo công suất. Sơ đồ KiCad hiện có là thiết kế bo điều khiển, chưa có bố trí PCB để đặt gia công.

| Chức năng | Chân MCU / chân vật lý |
|---|---|
| PWM nhánh A trên/dưới | PA8/42 và PA9/43; HRTIM A1/A2, AF13 |
| PWM nhánh B trên/dưới | PA10/44 và PA11/45; HRTIM B1/B2, AF13 |
| NGAT_LAI, tác động mức cao | PA12/46; HRTIM FLT1, AF13 |
| CHO_PHEP_CHAY | PB0/24, kéo xuống khi reset |
| XOA_LOI dự phòng | PB1/25; chưa có mạch chốt lỗi ngoài để xóa |
| Đo áp / dòng L / dòng pin | PA0/12, PA1/13, PA2/14; ADC1_IN1/2/3 |
| NTC 1/2/3 | PC0/8, PC1/9, PC2/10; ADC1_IN6/7/8 |
| Nạp SWD | PA13/49, PA14/50, NRST/7; 3V3 là VTREF |

J1 nhận **5 V đã ổn áp**, qua AP2112K-3.3 tạo 3,3 V. Không cấp 12 V trực tiếp vào J1. Các chân VDD, VDDA, VREF+, VBAT, reset và boot đã thể hiện trong sơ đồ đầy đủ. RET6 này không có chân VCAP để lắp theo sơ đồ MCU khác. Tắt VREFBUF khi cấp VREF+ theo phương án đang vẽ.

Xem `DIEU_KHIEN/BANG_NOI_LIEN_BO.md` để nối từng chân J2/J3. Nhãn giống nhau trên cùng miền nguồn là cùng một net. GND_THU_CAP là âm đầu ra và mass MCU; **khác DC_AM, SW_A, SW_B** phía sơ cấp.

## 4. Driver, đo lường và các phần còn cần thiết kế

Hai UCC21520DW được dự kiến lái hai nhánh cầu, mỗi IC một khóa trên và một khóa dưới. Logic driver ở miền MCU; nguồn đầu ra driver tham chiếu trực tiếp source của MOSFET tương ứng. Cần ba miền nguồn lái cách ly phù hợp: khóa trên A, khóa trên B và nguồn chung cho hai khóa dưới. Một module DC/DC ghi “cách ly” bất kỳ chưa đủ căn cứ sử dụng ở điện áp làm việc và dv/dt của bộ sạc này.

NGAT_LAI được kéo lên để khóa driver mặc định. Hai transistor cấp phép nối tiếp chỉ kéo thấp khi MCU cho chạy và mạch bảo vệ báo hợp lệ. Đây là logic tổ hợp, **không phải mạch nhớ lỗi**. BAO_VE_OK_3V3 phải đến từ mạch bảo vệ đã thiết kế, không nối cố định lên 3,3 V để thay bảo vệ. XOA_LOI đang là chân dự phòng.

Hai INA240A1D + hai shunt 1 mΩ bốn đầu Kelvin đo dòng. Với REF1 = 3V3, REF2 = GND: Vđo ≈ V3V3/2 + 0,020 × I. Tại 3,3 V và 34,48 A, Vđo ≈ 2,340 V; mỗi shunt tiêu tán khoảng 1,19 W. Công suất danh định 5 W vẫn phải kiểm tra với footprint, đồng PCB và nhiệt thực tế.

Bộ chia 110 kΩ + 110 kΩ / 10 kΩ tạo tỷ lệ 1/23; 58 V tương ứng 2,522 V, 70 V tương ứng 3,043 V. Phải cấu hình ADC theo trở kháng nguồn và các RC nối tiếp. **Đường đo áp cần cơ chế ngắt/bảo vệ khi MCU mất nguồn nhưng pin vẫn nối.** Bản vẽ đánh dấu phần này chưa thiết kế; không nối thẳng bộ chia vào MCU rồi coi là đã hoàn tất.

Các đầu việc còn lại để có mạch lắp ráp hoàn chỉnh: chốt loại PWM và tần số; chọn MOSFET/diode từ tổn hao; tính biến áp/cuộn cảm/tụ; xác minh driver và dead-time; thiết kế bảo vệ nhanh và giữ lỗi; ngắt đo khi mất nguồn; quản lý nối pin, dòng nạp ban đầu và đảo cực; PFC/nguồn phụ; tản nhiệt; khoảng cách cách điện và layout; firmware CC/CV và thử nghiệm. Các bản vẽ có chữ TBD là thiết kế sơ bộ, chưa phải chỉ dẫn cấp điện 400 V.

## 5. Mua gì trước

`DANH_SACH_MUA_BO_DIEU_KHIEN.csv` gộp số lượng từ BOM bo điều khiển và có liên kết tìm kiếm Shopee theo mã. Liên kết tìm kiếm không xác minh hàng thật, tồn kho hay giá. Mua đúng STM32G474RET6 LQFP64 và AP2112K-3.3 SOT-23-5; không thay sang VET6 hoặc IC ổn áp khác chỉ vì tên gần giống.

Có thể chuẩn bị trước linh kiện bo điều khiển, bộ nạp SWD phù hợp mức 3,3 V, tụ/trở và đầu cắm. Bộ nạp rời không nằm trong mạch. **BOM này không phải BOM đầy đủ của bộ sạc 2 kW.** Các khóa công suất, từ tính, nguồn driver cách ly, cầu diode và tản nhiệt chưa chốt mã để đặt mua hàng loạt.

## 6. Học và kiểm tra theo thứ tự

1. Đọc sơ đồ tổng thể và sơ đồ bo điều khiển; kiểm tra nguồn, cực linh kiện và chập chân trước cấp nguồn thấp áp có giới hạn dòng.
2. Nạp thử qua SWD, kiểm tra reset, boot và ADC bằng tín hiệu thấp áp. Chưa nối pin hoặc bus công suất.
3. Dựa vào ví dụ ST để tạo bốn PWM đồng bộ. Đo dead-time, tần số và cân bằng xung bằng dao động ký; thử tín hiệu lỗi phải tắt toàn bộ PWM.
4. Kiểm tra driver, từng điện áp Gate–Source, trạng thái reset/mất dây/mất nguồn. Chỉ thử tầng công suất thấp áp sau khi mạch bảo vệ và nguồn driver đã được hoàn thiện.
5. Đối chiếu mô phỏng với mạch thấp áp có giới hạn dòng và tải thử; kiểm tra cực tính đo, quá dòng và khởi động mềm trước khi đóng vòng điều khiển.
6. Hoàn thành thiết kế cách điện, layout, nhiệt và các thử nghiệm bảo vệ rồi mới lập kế hoạch thử công suất cao tại phòng thí nghiệm có thiết bị phù hợp.

Không được kẹp mass dao động ký nối đất tùy ý vào SW_A/SW_B hoặc sơ cấp; cần phương pháp đo và đầu dò phù hợp. Đây là các nút chuyển mạch điện áp cao, khác mass MCU.

## 7. Tài liệu tham khảo và mức độ kiểm tra

Đọc `TAI_LIEU_THAM_KHAO.md`: ưu tiên ví dụ ST về HRTIM/dead-time/ADC, sau đó ví dụ cộng đồng Full Bridge trên G474, rồi tài liệu thiết kế công suất TI. Có cả liên kết tìm video, được ghi rõ là tìm kiếm nếu chưa xác minh video cụ thể. Mã mẫu buck hoặc C2000 không nạp nguyên vào mạch Full Bridge STM32.

Kiểm tra đã thực hiện: đối chiếu chân MCU với dữ liệu chân ST; KiCad ERC không có vi phạm; đối chiếu 147 kết nối chân vật lý với netlist xuất thực tế, không sai khác. Đây là kiểm tra tệp/sơ đồ, **không phải đo mạch thật**, kiểm chứng an toàn cách điện hay xác nhận hiệu suất 2 kW.

Các hình tổng thể, công suất, chân MCU, sơ đồ KiCad điều khiển và bản vẽ driver/đo lường được ghép sau phần hướng dẫn trong PDF tổng hợp. Tệp nguồn có thể chỉnh sửa, cùng BOM và tài liệu tham khảo nằm trong gói ZIP.
