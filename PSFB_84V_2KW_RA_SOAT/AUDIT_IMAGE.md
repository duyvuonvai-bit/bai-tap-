# Đánh giá độc lập ảnh sơ đồ bộ sạc PSFB 2 kW

Ngày: 16/10/2026. Phạm vi: hai ảnh sơ đồ khối và một ảnh sơ đồ nguyên lý người dùng vừa gửi. Đây là rà soát từ ảnh; chưa có netlist, PCB, mô phỏng chuyển mạch hoặc đo thực tế của bản này.

## Kết luận

**Sơ đồ cấu trúc đúng hướng:** điện lưới → lọc/chỉnh lưu → Boost PFC → cầu H PSFB → biến áp cách ly → chỉnh lưu cao tần → LC → pin; STM32 nhận phản hồi và điều khiển cầu H qua driver cách ly. Cần thêm đường bảo vệ phần cứng tới chân khóa driver, nguồn phụ, phần tử đóng/ngắt pin và vị trí đo rõ ràng.

**Ảnh sơ đồ nguyên lý chưa đủ để hàn mạch theo.** Có mâu thuẫn về tên chân, tên mạng, nguồn nổi của driver, ngưỡng bảo vệ và cấu trúc CAN. Một số đường dây nhỏ không đọc chắc; không được suy ra kết nối đúng từ hình đẹp hoặc từ việc các khối đã đủ tên.

Ảnh mới ghi **Li-ion 20S, tối đa 84 V**. Đây là bộ thông số khác phương án LiFePO₄ 16S/58 V trước. Các bảng linh kiện và điều khiển trước không tự động áp dụng được. Với 2 kW, dòng tại 84 V là 23,81 A. Nếu chọn CC = 23,81 A thì công suất ở 60 V chỉ khoảng 1,43 kW; muốn 2 kW cả ở 60 V phải có giới hạn dòng đến 33,33 A và chiến lược giới hạn công suất phù hợp. Dòng sạc còn phải phù hợp dung lượng và loại cell/BMS thực tế.

## Các phát hiện theo khối

| Khối trong ảnh | Phát hiện và mức chắc chắn | Cách sửa/điều kiện cần chốt |
|---|---|---|
| 1. Boost PFC | Ảnh không thể hiện rõ cặp phần tử bắt buộc: MOSFET từ nút chuyển mạch xuống DC_BUS− và diode Boost từ nút đó tới DC_BUS+. Đường L_PFC trông nối thẳng sang tụ/bus; không được coi đây là mạch Boost hoàn chỉnh. Dây nhỏ chưa đủ rõ để khẳng định mọi điểm nối. | Vẽ lại đầy đủ: cầu diode → L_PFC → nút SW_PFC; từ SW_PFC qua diode tới bus+, và qua MOSFET xuống bus−. Thêm điều khiển PFC, đo dòng, đo bus, tụ bus, bảo vệ và hạn dòng nạp. |
| 1. AC/EMI | Có ký hiệu X/Y/PE nhưng chưa có mã cấp an toàn, thông số lọc, cách nối đất và dòng định mức. | PE chỉ nối vỏ/đất bảo vệ theo thiết kế. Không dùng tụ gốm thường thay tụ X/Y. Không lấy cùng một ký hiệu GND cho PE và tất cả các miền điện. |
| 2. Cầu H | Chọn cấu trúc bốn khóa, biến áp và chỉnh lưu cầu là phù hợp. Tuy nhiên hình không xác định dạng PWM, tần số, dead-time hay giới hạn lệch pha. | Với PSFB, hai khóa mỗi nhánh bổ sung gần 50%, có dead-time; thay công suất bằng lệch pha giữa hai nhánh. Không dùng bốn PWM độc lập tùy ý. |
| 2. Tụ bus | Những tụ 4,7 µF/630 V sát cầu H có thể là tụ film cao tần. Chúng không tự thay thế tụ dự trữ năng lượng của PFC. | Tách rõ C_BUS_FILM và C_PFC_BULK; tính ripple 100 Hz, ripple chuyển mạch, thời gian giữ điện nếu yêu cầu. |
| 2. Biến áp/LC | Tỷ số khoảng Np:Ns = 25:8, L_OUT khoảng 33 µH và các tụ 160 V chỉ là thông số sơ bộ. Không thể kết luận đủ 2 kW chỉ từ ba con số này. | Chốt fs, bus min/max, dòng tối đa, vật liệu/lõi/Ae, số vòng tuyệt đối, tiết diện dây, cách điện, điện cảm rò và tổn hao. Tính Isat, DCR của L và ESR/dòng ripple của tụ. |
| 2. Đường pin | Chỉ thấy pin/BMS nối đầu ra; chưa có xử lý đảo cực, dòng ngược, dòng nạp tụ khi nối pin, cầu chì DC và đóng/ngắt pin. | Bổ sung các phần tử này theo phương án khởi động/nối pin. BMS không thay chức năng bảo vệ của bộ sạc. |
| 3. Nguồn phụ | Hình chưa có mã điều khiển, cuộn dây, hồi tiếp và linh kiện đủ xác định; không thể triển khai nguồn AC/DC hoặc DC/DC từ ảnh này. | Dùng nguồn phụ cách ly có thông số đã biết hoặc thiết kế nguồn phụ riêng hoàn chỉnh. Tách nguồn logic thứ cấp khỏi các miền nguồn lái công suất. |
| 4. Driver U10 | Ngõ trên trong khối U10 nhánh A được ghi **GATE_Q3**, trong khi U11 cũng ghi GATE_Q3. Đây là mâu thuẫn tên mạng đọc được rõ. | U10.OUTA phải đi Gate Q1; U10.OUTB đi Gate Q2. U11.OUTA đi Gate Q3; U11.OUTB đi Gate Q4. Mỗi Gate chỉ có một driver điều khiển. |
| 4–5. Nguồn driver | Ảnh chưa thể hiện đáng tin cậy nguồn nổi riêng và điểm hồi dòng của từng kênh. Một số dây quanh OUTA/VDDA cũng khó phân biệt. | VDDA/VSSA là nguồn kênh trên; VSSA_A = Source Q1 = SW_A, VSSA_B = Source Q3 = SW_B. VSSB của các kênh dưới = DC_BUS−. Tụ decoupling mắc giữa VDDx–VSSx tương ứng. Không nối VSSA nổi về GND logic. OUTx chỉ tới Gate qua mạng cổng; không nối OUTx trực tiếp nguồn 12 V. |
| 4–5. UCC21520 | Không thể chốt chân vật lý hoặc DT từ hình này. KiCad địa phương có symbol UCC21520DW nhưng chưa có đối chiếu datasheet hãng thành công trong lần này. | Trước PCB phải kiểm tra đúng package/revision, mọi chân VCCI/NC, cấu hình DT/UVLO. Không tự nối chân 8 hoặc chọn điện trở DT từ suy đoán. |
| 4–5. FAULT/DIS | DIS của driver là tín hiệu **đầu vào khóa**, không phải đầu ra báo trạng thái. Tên FAULT_A/B có thể dùng cho lệnh khóa, nhưng chưa thấy đầy đủ logic, cực tính và trạng thái khi mất nguồn. | Thiết kế mặc định khóa khi reset/mất nguồn/mất dây; lỗi phần cứng phải trực tiếp khóa driver. Chốt lỗi và thao tác xóa lỗi phải có mạch/firmware cụ thể. |
| 4–5. Định danh linh kiện | Có vị trí mã linh kiện/giá trị không nhất quán, ví dụ vùng mang nhãn dạng R26 nhưng giá trị 100 nF; các tham chiếu C/R trùng giữa các khối. | Vẽ bằng EDA với symbol đúng, annotate lại toàn bộ, mỗi linh kiện vật lý có một mã duy nhất trong một bo; kiểm tra netlist/BOM. |
| 6. STM32 | Ký hiệu trong ảnh không phải một pinout RET6 đủ tin cậy: số pin nhỏ bên PA8… không khớp pin vật lý; vùng dưới có dòng ghép PA2 với PC14-OSC32_IN. | Dùng symbol STM32G474RET6/LQFP64 đã kiểm tra từ dữ liệu ST. Không hàn theo số chân trên ảnh tổng hợp này. Xem bảng pin đã kiểm chứng bên dưới. |
| 6. Nguồn MCU | Chưa thể hiện đầy đủ, rõ ràng mọi VDD/VSS, VDDA/VSSA/VREF+, VBAT, BOOT và NRST. | Decoupling sát từng chân nguồn; nguồn ADC phù hợp; bảo đảm ADC không bị cấp ngược khi MCU tắt. Không thêm VCAP/VDDUSB vì RET6 này không có các chân đó. |
| 7.1. Đo áp | Với R trên = 390 kΩ, R dưới = 10 kΩ, **V_SENSE = V_OUT/40**. 84 V → 2,10 V; 100 V → 2,50 V. Thang đo có thể dùng nhưng không tận dụng hết ADC 3,3 V. | Có thể giữ tỷ số nếu chủ ý, nhưng tính sai số điện trở, điện áp làm việc mỗi điện trở, RC và thời gian lấy mẫu ADC. Bổ sung bảo vệ/đường ngắt khi MCU mất nguồn mà pin vẫn nối. |
| 7.3. OVP | Nếu comparator dùng VREF = 2,70 V đúng như chữ trong ảnh, với bộ chia 1/40 thì ngưỡng là **108 V**. Quá cao cho pin giới hạn 84 V. | Chọn ngưỡng OVP riêng dựa giới hạn pin, dung sai cảm biến và bộ điều khiển. Ví dụ số học: 86 V cần 2,150 V với tỷ số 1/40; đây chưa phải ngưỡng được phê duyệt cho cell thực tế. |
| 7.2. Đo dòng | Ảnh đổi sang INA241A1 và shunt 0,5 mΩ; đây không phải INA240A1/1 mΩ trong bản cũ. Chỉ thấy một kênh đo, nhưng MCU/bảo vệ sử dụng cả I_L_SENSE và I_BAT_SENSE. | Chốt đo một dòng hay hai dòng. Nếu đo cả hai thì cần hai shunt/sensor ở hai vị trí: trước điểm tụ đầu ra và nhánh tới pin. Nếu chỉ dùng một kênh, sửa toàn bộ tên, thuật toán và bảo vệ tương ứng. |
| 7.2–7.3. Gain dòng/OCP | Symbol KiCad địa phương mô tả **INA241A1 gain 10 V/V**; chưa kiểm chứng datasheet hãng trong lần này. Khi đúng gain này, 0,5 mΩ tạo độ nhạy 5 mV/A: 23,81 A chỉ làm tăng 0,119 V trên điện áp tham chiếu. 2,70 V không tự tạo ngưỡng OCP hợp lý. | Công thức phải dùng `I_trip = (V_threshold − V_reference)/(G × R_shunt)`. Nếu reference = 0 thì 2,70 V tương đương 540 A; nếu reference = 1,65 V thì 210 A. Phải chỉ rõ chân REF, nguồn, khoảng output và ngưỡng trước thiết kế. |
| 7.2. Chọn sensor | INA240 có giới hạn common-mode 80 V, không phù hợp đo high-side tại đầu ra danh định 84 V; không giữ lại mã này chỉ vì đã có trong giỏ hàng cũ. | Chọn sensor có common-mode đủ cả điện áp sạc và quá độ. INA241 là ứng viên cần kiểm tra đúng mã và datasheet; kiểm tra cả nguồn cấp, output/ADC, trạng thái mất nguồn. |
| 7.3. Bảo vệ nhanh | RC đầu vào/đầu ra và comparator chưa có tính thời gian đáp ứng; chưa thấy kênh bảo vệ dòng sơ cấp đủ nhanh hoặc cách truyền lỗi qua ranh giới cách ly. | Tách điều khiển CC/CV khỏi bảo vệ ngắn mạch từng chu kỳ/khóa lỗi. Không chỉ lấy tín hiệu dòng đã lọc chậm rồi trông chờ chương trình ADC. |
| 7.4. NTC | Hình ghi kéo lên 10 kΩ và NTC 100 kΩ: tại 25 °C điện áp khoảng 3,0 V, không phải 1,65 V. Đây không tự là lỗi nhưng khác bộ 10 kΩ/10 kΩ trước; chưa có B/hàm R(T). | Chọn đúng một loại NTC và tính bảng ADC/nhiệt tương ứng. Tính cả đứt/chập cảm biến. Với MCU ở thứ cấp, cảm biến gắn vào phần điện lưới phải có cách điện phù hợp. |
| 7.3. OTP | Ảnh vẽ ba tín hiệu NTC quanh một comparator nhưng không xác định mạch OR hay ngưỡng riêng; không thể nối chập ba nút đo để suy ra nhiệt cao nhất. | Dùng so sánh riêng từng kênh và tổng hợp lỗi, hoặc xử lý đo nhiệt bằng MCU kết hợp bảo vệ độc lập tại vị trí quan trọng. Số comparator phải phù hợp package thực. |
| 8. CAN/BMS | ISO1050 và ADM3053 là các phương án transceiver CAN cách ly; SN65HVD230 cũng là transceiver. Chuỗi CAN → ISO1050/ADM3053 → SN65HVD230 → MCU trong ảnh không phải cách ghép tiêu chuẩn. | Dùng **một** transceiver CAN cách ly nối TXD/RXD logic về MCU, với nguồn đúng mỗi phía; hoặc isolator logic + một transceiver riêng. Không ghép nối tầng hai transceiver như hình. |
| 8. CAN termination | Cách vẽ hai điện trở 60 Ω chưa đủ rõ để xác nhận split termination đúng. | Nếu split termination: hai 60 Ω mắc nối tiếp **giữa CANH và CANL**, điểm giữa có tụ theo thiết kế. Không đặt mỗi đường CANH/L một điện trở nối tiếp 60 Ω rồi gọi là termination. Chỉ đặt termination ở hai đầu bus. |
| Toàn bộ | Dùng nhiều ký hiệu mass giống nhau giữa sơ cấp/thứ cấp/driver nổi có thể vô tình nối chung các miền nếu dựng thành netlist. | Đặt tên riêng PE, DC_BUS_AM, GND_THU_CAP, SW_A, SW_B. Khoảng cách creepage/clearance và hàng rào cách ly phải được thể hiện trong PCB, không chỉ bằng nét đứt trong ảnh. |

## Pin STM32G474RET6 đã đối chiếu với dữ liệu chân ST của dự án trước

Nguồn cục bộ: `/workspace/ret6_hardware/control/sources/STM32G474R_B-C-E_Tx.xml`, `GPIO-STM32G47x_gpio_v1_0_Modes.xml` và `pin_verification.json`. Kiểm chứng pin MCU này không xác nhận toàn bộ ảnh mới.

| Chức năng | Chân GPIO | Chân LQFP64 |
|---|---|---:|
| HRTIM CHA1/CHA2, AF13 | PA8 / PA9 | 42 / 43 |
| HRTIM CHB1/CHB2, AF13 | PA10 / PA11 | 44 / 45 |
| HRTIM FLT1, AF13 | PA12 | 46 |
| ADC1_IN1/IN2/IN3 | PA0 / PA1 / PA2 | 12 / 13 / 14 |
| ADC1_IN6/IN7/IN8 | PC0 / PC1 / PC2 | 8 / 9 / 10 |
| SWDIO / SWCLK | PA13 / PA14 | 49 / 50 |
| NRST | PG10-NRST | 7 |
| BOOT0 | PB8-BOOT0 | 61 |
| VDD | — | 16 / 32 / 48 / 64 |
| VSS | — | 15 / 31 / 47 / 63 |
| VDDA / VSSA / VREF+ / VBAT | — | 29 / 27 / 28 / 1 |

## Điều kiện để chuyển từ ảnh tham khảo thành bo có thể lắp ráp

1. Chốt rõ loại pin và chế độ công suất/dòng, dải điện lưới, tần số PSFB và nguyên tắc điều khiển PFC.
2. Sơ đồ EDA phải chứa **từng linh kiện thật**, mã package/footprint, mọi nguồn và mạng nối; không giữ khối nét đứt hoặc chân suy đoán ở vị trí cần hàn.
3. Tính từ trường, nhiệt và bảo vệ, chọn linh kiện theo datasheet thật; lập BOM có công dụng và trạng thái “đã chốt/chờ chọn”.
4. Sau đó mới làm placement/routing, kiểm tra ERC/DRC, khoảng cách cách điện và dòng lớn, xuất bản đồ lắp linh kiện/polarity/connector.
5. ERC/DRC sạch không có nghĩa đã kiểm chứng điện áp 400 V hoặc công suất 2 kW. Bo điều khiển đã kiểm tra ở bản trước cũng không làm ảnh tổng hợp mới trở thành bản thiết kế đã thử nghiệm.

## Độ tin cậy của nguồn

- Các tỷ số chia áp, dòng/công suất và sai ngưỡng được tính trực tiếp từ chữ nhìn rõ trong ảnh.
- Pin STM32 dựa dữ liệu chân chính thức ST đã lưu cục bộ từ công việc trước.
- Gain INA241A1 trong báo cáo này dựa mô tả symbol KiCad, **chưa thay cho xác minh datasheet hãng trước chọn mua/hàn**.
- Chân UCC21520/DT và các đường dây mờ trên ảnh giữ trạng thái chưa xác minh; không suy ra chân số từ hình.
- Không có phép thử TIA/MATLAB/đồ án PID trước nào xác nhận tính đúng của bo sạc này.
