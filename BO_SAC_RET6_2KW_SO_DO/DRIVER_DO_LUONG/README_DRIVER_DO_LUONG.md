# Driver và đo lường — bản sơ bộ

Bản cập nhật ngày 16/10/2026 gồm 5 trang PDF, kèm ảnh PNG/SVG và script tạo hình. Đây là sơ đồ kết nối để rà soát, chưa phải PCB hay thiết kế bộ sạc 2 kW đã thử nghiệm.

## Các thay đổi đã hoàn tất

- D1 dùng đúng tên `PWM_A_TREN_RA`, `PWM_A_DUOI_RA`, `PWM_B_TREN_RA`, `PWM_B_DUOI_RA` như J2 của bo MCU. Driver có vị trí điện trở 0 Ω; bo MCU đã có điện trở nối tiếp 33 Ω. Mỗi IN driver có 10 kΩ kéo xuống.
- D2 dùng `CHO_PHEP_CHAY` từ PB0/J2.7. Hai 2N7002 mắc nối tiếp kéo thấp `NGAT_LAI` khi cả cấp phép và trạng thái bảo vệ hợp lệ đều bằng 1. Đây là logic tổ hợp, **không phải chốt lỗi**. PB1/J2.8 `XOA_LOI` chỉ là chân dự phòng.
- D3 dùng `DONG_L_DA_DO` và `DONG_PIN_DA_DO` đưa về J3.2/J3.3. Hai INA240A1D cùng GND_THU_CAP; mỗi shunt là 1 mΩ, 5 W, bốn đầu Kelvin. Chỉ đo phía thứ cấp.
- D4 dùng `AP_RA_DA_CHIA` đưa về J3.1. Đường từ pin tới bộ chia chứa khối nét đứt **chưa thiết kế** để ngắt khi MCU mất nguồn hoặc bảo vệ power-off đã kiểm chứng. Không có linh kiện thay thế khối này trong BOM sơ bộ.
- D5 thêm ba bộ chia NTC: điện trở cố định 10 kΩ từ 3V3 tới nút đo, NTC 10 kΩ/B3950 từ nút đo xuống mass. Các đầu ra tương ứng J3.4/5/6. NTC phải có gá lắp cách điện phù hợp vị trí đo.

## Những phần chưa hoàn tất

1. Chưa xác minh chân 8 và cấu hình DT của UCC21520DW bằng datasheet đúng mã/revision trong phiên này. Giữ **CHƯA CHỐT** trên hình; không dùng thư viện KiCad thay cho datasheet.
2. Chưa chọn module nguồn cách ly cho ba miền lái `+12V_A/SW_A`, `+12V_B/SW_B`, `+12V_DUOI/DC_AM`. Phải xét điện áp cách ly, điện áp làm việc, CMTI, điện dung ký sinh, công suất cổng và UVLO.
3. Chưa có mạch tạo `BAO_VE_OK_3V3`, bộ so sánh quá dòng/quá áp và chốt giữ lỗi. Không thay bằng mức 1 cố định để coi là đã có bảo vệ. Firmware và trình tự giải phóng FLT1 chưa triển khai.
4. Khối ngắt đo pin khi MCU mất nguồn chưa có sơ đồ chi tiết. Bộ chia thuần trở có thể cấp ngược vào MCU qua ADC khi pin vẫn nối. Cần kiểm tra tương tự đối với INA240 ở trạng thái mất nguồn và mọi đường tín hiệu khác.
5. Các giá trị R_G, diode kẹp cổng và lọc ADC là giá trị khởi đầu, chưa được kiểm nghiệm với MOSFET, dây dẫn và layout thực tế.
6. Chưa lập trình chẩn đoán NTC đứt/chập, ngưỡng nhiệt, hiệu chuẩn đo lường, ngưỡng quá áp/quá dòng hoặc thuật toán CC/CV.

## Điểm cần phân biệt khi ghép với bo MCU

- `GND_THU_CAP` = âm đầu ra/miền điều khiển. Không nối nó với `DC_AM`, `SW_A` hoặc `SW_B`.
- Bo MCU nhận 5 V ổn áp qua J1 và tạo 3V3. Không đưa 12 V nguồn driver vào J1 hoặc J2.1.
- Mỗi ngõ J3 đã có RC 100 Ω/1 nF trên bo MCU. Hai ngõ dòng có thêm RC 100 Ω/2,2 nF tại bo đo. Đây là các vị trí vật lý riêng, tạo bộ lọc nhiều cực.
- Bộ chia 110 kΩ + 110 kΩ / 10 kΩ cho tỷ số 1/23: 58 V tương ứng khoảng 2,522 V; 70 V tương ứng 3,043 V. Trở kháng Thevenin khoảng 9,565 kΩ; ADC phải chọn thời gian lấy mẫu phù hợp. 70 V là mốc tính thang đo, không phải điện áp sạc đã chọn.
- INA240A1D có gain 20 V/V, REF1 nối 3V3 và REF2 nối GND: `V_OUT = V_3V3/2 + 0,020 × I(A)`. Hai shunt riêng biệt đo dòng cuộn cảm và dòng pin; cần hiệu chuẩn.
- Ba kênh nhiệt có khoảng 1,65 V tại 25 °C. NTC nóng hơn làm điện áp giảm. Đứt NTC đưa điện áp về gần 3V3, chập NTC đưa về gần 0 V; chỉ có khả năng chẩn đoán sau khi lập trình và kiểm thử.

Chỉ có sơ đồ bo điều khiển trong thư mục khác được kiểm tra ERC/netlist. Các trang này chưa qua ERC, chưa mô phỏng chuyển mạch và chưa đo thực tế.
