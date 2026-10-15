# Bảng nối bo điều khiển STM32G474RET6

Ngày kiểm tra: 15/10/2026. Đây là sơ đồ nguyên lý bo điều khiển 3,3 V và bảng giao diện; chưa có PCB và chưa kiểm chứng mạch sạc ở 400 V/2 kW.

## Giắc J2 — driver và bảo vệ

| Chân | Net trên bo điều khiển | Nối sang bo driver | Chân MCU |
|---|---|---|---|
| 1 | 3V3 | VCCI các driver và nguồn logic bảo vệ 3,3 V | Nguồn |
| 2 | GND_THU_CAP | GND_ĐK | GND |
| 3 | PWM_A_TREN_RA | INA driver nhánh A | PA8/42, HRTIM1_CHA1 AF13 |
| 4 | PWM_A_DUOI_RA | INB driver nhánh A | PA9/43, HRTIM1_CHA2 AF13 |
| 5 | PWM_B_TREN_RA | INA driver nhánh B | PA10/44, HRTIM1_CHB1 AF13 |
| 6 | PWM_B_DUOI_RA | INB driver nhánh B | PA11/45, HRTIM1_CHB2 AF13 |
| 7 | CHO_PHEP_CHAY | Gate Q_EN của mạch khóa driver | PB0/24 |
| 8 | XOA_LOI | Dự phòng cho mạch chốt lỗi; hiện chưa sử dụng | PB1/25 |
| 9 | NGAT_LAI | DIS của cả hai driver và nút phản hồi khóa | PA12/46, HRTIM1_FLT1 AF13 |
| 10 | GND_THU_CAP | GND_ĐK | GND |

GND_THU_CAP và GND_ĐK là cùng miền thứ cấp. Tuyệt đối không diễn giải chúng là DC_AM của bus sơ cấp, SW_A hoặc SW_B.

Mỗi PWM có điện trở 33 Ω và kéo xuống 10 kΩ trên bo điều khiển. Bản driver cập nhật dùng 0 Ω dự phòng nối tiếp và thêm 10 kΩ kéo xuống ngay chân IN; tổng nối tiếp danh định là 33 Ω, tải kéo xuống tương đương xấp xỉ 5 kΩ ở trạng thái tĩnh. Điện trở 0 Ω là vị trí để điều chỉnh sau khi đo dạng xung; không tự cộng thêm 47 Ω từ bản cũ. Cần kiểm tra dạng xung tại IN driver sau khi đi dây.

NGAT_LAI mức 1 khóa driver. Kéo lên 10 kΩ trên bo điều khiển làm FLT1 báo khóa khi dây J2.9 đứt. Mạch driver kéo lên 4,7 kΩ và chỉ kéo xuống khi CHO_PHEP_CHAY = 1 và BAO_VE_OK_3V3 = 1. Đây là logic tổ hợp; bản hiện tại chưa có mạch chốt lỗi ngoài. Không gọi NGAT_LAI là bit lỗi đã chốt. XOA_LOI không tự tạo chức năng chốt/xóa lỗi.

Firmware phải cấu hình FLT1 tác động mức cao, đầu ra HRTIM về mức tắt khi fault và CHO_PHEP_CHAY = 0 khi reset. Trình tự giải phóng fault và cấp phép phải được thiết kế để không phát xung bất ngờ khi khởi động. Cần bổ sung và kiểm tra nguồn BAO_VE_OK_3V3, ngưỡng quá dòng/quá áp/nhiệt, độ trễ bảo vệ và cơ chế giữ lỗi trước khi vận hành tầng công suất.

## Giắc J3 — tín hiệu đã điều hòa

| Chân | Net trước RC trên bo MCU | Net sau RC / MCU | Nguồn tín hiệu |
|---|---|---|---|
| 1 | AP_RA_DA_CHIA | ADC_AP_RA — PA0/12, ADC1_IN1 | Bộ chia điện áp đã xử lý bảo vệ |
| 2 | DONG_L_DA_DO | ADC_DONG_L — PA1/13, ADC1_IN2 | INA240 đo dòng cuộn cảm |
| 3 | DONG_PIN_DA_DO | ADC_DONG_PIN — PA2/14, ADC1_IN3 | INA240 đo dòng pin |
| 4 | NHIET_1_DA_DO | ADC_NHIET_1 — PC0/8, ADC1_IN6 | Mạch chia áp NTC 1 |
| 5 | NHIET_2_DA_DO | ADC_NHIET_2 — PC1/9, ADC1_IN7 | Mạch chia áp NTC 2 |
| 6 | NHIET_3_DA_DO | ADC_NHIET_3 — PC2/10, ADC1_IN8 | Mạch chia áp NTC 3 |
| 7 | GND_THU_CAP | GND | GND_ĐK |
| 8 | GND_THU_CAP | GND | GND_ĐK |

Hình đo lường cập nhật dùng thống nhất DONG_L_DA_DO, DONG_PIN_DA_DO và AP_RA_DA_CHIA khi đưa vào J3; đây là tín hiệu trước bộ lọc cuối trên bo MCU, không phải chân MCU trực tiếp. Mỗi chân J3 đi qua RC 100 Ω/1 nF đặt sát MCU. RC này bổ sung cho RC đầu ra của bo đo: dòng có 100 Ω/2,2 nF, điện áp có bộ chia trở kháng khoảng 9,6 kΩ và tụ 10 nF. Chúng tạo bộ lọc nhiều cực; phải tính thời gian xác lập và lựa chọn sampling time ADC theo trở kháng nguồn, không chỉ theo 100 Ω cuối cùng.

Hai shunt là hai linh kiện 1 mΩ, mỗi linh kiện bốn đầu Kelvin; không phải bốn shunt. Một đo dòng cuộn cảm trước nút tụ đầu ra, một đo dòng đi vào pin sau nút tụ. Tại 34,5 A, tổn hao mỗi shunt xấp xỉ 1,19 W. Hai INA240A1 có REF1 nối 3V3, REF2 nối GND: VOUT ≈ V3V3/2 + 0,02 × I. Cần hiệu chuẩn offset và điện trở shunt.

Giắc J3 chỉ nhận mức analog thấp. Không đưa điện áp pin hoặc bus trực tiếp vào. Không để nguồn cảm biến đưa điện áp dương vào ADC khi MCU mất nguồn; bộ chia điện áp pin cần cơ chế ngắt hoặc linh kiện có đặc tính power-off protection đã xác minh. Phần bảo vệ này không nằm trong sơ đồ bo điều khiển tối thiểu.

## Nguồn, nạp chương trình và trạng thái kiểm tra

- J1 nhận 5 V đã ổn áp; AP2112K-3.3 tạo 3V3. Không đưa 12 V vào J1.
- Mạch tối thiểu dùng HSI/PLL nội bộ; chưa gắn thạch anh ngoài.
- J5.1 là 3V3/VTREF, J5.2 SWDIO, J5.3 SWCLK, J5.4 GND, J5.5 NRST, J5.6 GND. Bộ nạp phải cùng mức logic; tránh cấp đồng thời hai nguồn 3V3.
- J6 là UART TTL 3,3 V: PC4 USART1_TX AF7, PC5 USART1_RX AF7. Không nối trực tiếp RS-232/RS-485.
- Chân 7 MCU phải giữ chức năng NRST. BOOT0/PB8 có kéo xuống; kiểm tra option bytes khởi động Flash. Tắt VREFBUF khi cấp VREF+ bằng 3V3_ANALOG.
- `ERC_KIEM_TRA.json`: KiCad kiểm tra 0 vi phạm trên sơ đồ bo điều khiển.
- `KET_QUA_KIEM_TRA_NET.json`: 147 kết nối chân linh kiện vật lý đối chiếu với netlist xuất thực tế, không sai khác. Ba PWR_FLAG là ký hiệu nguồn phục vụ ERC, không phải linh kiện mua.
- Kết quả ERC không chứng minh mạch driver, bảo vệ, layout, phần mềm hoặc tầng công suất đã sẵn sàng chế tạo.

Mở `BO_DIEU_KHIEN_RET6.kicad_pro` cùng thư mục `RET6_LOCAL.kicad_sym` và `sym-lib-table` để giữ đúng thư viện đã đóng gói.
