# Tính toán sơ bộ bộ sạc PSFB 2 kW — 20S lithium

Ngày 16/10/2026. Người dùng xác nhận pin 20 cell lithium và **đã có bo STM32G474RET6 lắp sẵn**. Các phép tính dưới đây giả thiết cell nạp tối đa 4,2 V, nên CV=84 V. Người dùng cho phép chọn thông số mục tiêu: **20S, 50 Ah; BMS chịu dòng sạc liên tục ít nhất 30 A**. Với CC 23,81 A, tốc độ sạc danh nghĩa là 0,476 C. Đây là mục tiêu thiết kế, chưa xác nhận một bộ cell/BMS thực tế đáp ứng; phải đối chiếu datasheet trước khi sạc pin thật. Không mua lại chip MCU hoặc thiết kế lại bo MCU khi chưa kiểm tra đầu chân bo đang có.

Đây là tính chọn sơ bộ để sửa sơ đồ; chưa phải bộ thông số đã đo/kiểm chứng cho PCB 2 kW. Tệp `calc.py` tạo `calcs.json`, chứa cả số của hình gốc và các đề xuất mới, phân biệt theo tên nhóm. Chạy lại bằng `python calc.py`.

## 1. Bộ giả thiết thiết kế đang khảo sát

| Đại lượng | Giá trị/ý nghĩa |
|---|---|
| Nguồn vào | 220 VAC/50 Hz; kiểm tra sơ bộ 198–242 VAC |
| PFC | Boost CCM, tần số **65 kHz** là lựa chọn khảo sát |
| Bus đặt | **400 VDC danh định** |
| Dải bus dùng tính linh kiện | **380–420 V**; phải phối hợp với ripple, sai số và bảo vệ |
| Đầu ra | 60–84 V theo hình, CC tối đa **23,81 A**, CV **84 V** |
| Công suất | 2 kW tại 84 V; tại 60 V với CC này chỉ 1.428,6 W |
| PSFB | Tần số toàn chu kỳ cầu H **50 kHz**, gợn sau chỉnh lưu đối xứng **100 kHz** |
| Biến áp | Khảo sát Np:Ns=25:8, n=0,32; chưa chốt lõi, dây, cách điện |
| Giới hạn D tác dụng minh họa | 0,80; không phải duty riêng của MOSFET |
| L đầu ra đề xuất khảo sát | **100 µH**, xét dung sai −20% còn 80 µH |
| C đầu ra | 220+220+680=**1.120 µF/160 V**, cần xác minh dòng ripple/ESR |
| Hiệu suất dùng tính lưới | DC/DC 95%, PFC 97%, tổng 92,15%; PF=0,99 — chưa đo thực tế |

Pin được sạc CC–CV: P/V cho biết dòng tương ứng công suất, không chứng minh pin chịu được dòng. Nếu muốn giữ đủ 2 kW xuống 60 V, phải chịu 33,33 A và tính lại, không dùng bộ CC 23,81 A này.

## 2. Cầu H, tỷ số biến áp và độ lệch pha

Điện áp xung thứ cấp `Vs=n·Vbus` đạt **121,6–134,4 V** trong dải bus thiết kế. Mỗi nhánh cầu PSFB chạy xung bù gần 50% với dead-time; điều chỉnh công suất bằng lệch pha hai nhánh. Gọi D là tỷ phần thời gian có điện áp tác dụng lên biến áp trong mỗi nửa chu kỳ; theo quy ước này `D=phi/180°`. **Không nhập D này thành duty riêng cho cả bốn MOSFET.**

Mô hình gần đúng: `Vout≈n·Vbus·D−2Vf`. Lấy Vf=0,8 V/diode để minh họa:

| Điểm | Bus 380 V | Bus 400 V | Bus 420 V |
|---|---:|---:|---:|
| D cần tại 84 V | 0,7039 | 0,6688 | 0,6369 |
| Góc phi tương ứng | 126,71° | 120,38° | 114,64° |
| D cần tại 60 V | 0,5066 | 0,4813 | 0,4583 |

Chưa tính mất duty do điện cảm rò, chuyển mạch dòng, dead-time và sụt điện trở. Với Dmax=0,80 ở bus 380 V, điện áp khả dụng lý tưởng sau sụt diode là **95,68 V**, còn dự trữ 11,68 V so với 84 V. Cần mô phỏng và đo xem dự trữ có đủ. Tỷ số 25:8 có khả năng điều chỉnh điện áp, nhưng chưa chứng minh số vòng đủ chống bão hòa hoặc thiết kế đạt ZVS.

## 3. Vì sao thay L=33 µH bằng phương án khảo sát 100 µH

Mô hình CCM lý tưởng: `ΔILpp=Vout·(1−Vout/Vs)/(L·fr)`; `ILpk=Iout+ΔILpp/2`; `ILrms=sqrt(Iout²+ΔILpp²/12)`.

Cực đại ripple theo Vout xảy ra tại Vs/2. Với bus 420 V, Vs/2=67,2 V nằm trong dải pin 60–84 V:

| Cuộn cảm | ΔILpp lớn nhất | Tỷ lệ so với CC 23,81 A | IL đỉnh |
|---|---:|---:|---:|
| 33 µH theo hình | 10,18 A | 42,76% | 28,90 A |
| 68 µH danh định | 4,94 A | 20,75% | 26,28 A |
| 100 µH danh định | **3,36 A** | **14,11%** | **25,49 A** |
| 100 µH với −20% còn 80 µH | **4,20 A** | **17,64%** | **25,91 A** |

Mục tiêu ripple 20% đòi hỏi L hiệu dụng≥**70,56 µH**; nếu tính dung sai−20%, danh định≥88,2 µH. Vì vậy **100 µH** là lựa chọn khảo sát hợp lý hơn 33 µH ở tần số này. ILrms lớn nhất với 80 µH≈**23,84 A**.

Mục tiêu linh kiện: **L 100 µH, dòng nhiệt liên tục ít nhất khoảng 25 A ở môi trường thực, kiểm tra Isat≥35 A tại nhiệt độ nóng**. Đây là yêu cầu để chọn/thiết kế, không bảo đảm một cuộn cảm trên shop ghi 35 A đáp ứng. Phải xét suy giảm L theo DC bias/nhiệt, dung sai, dòng quá độ và thời gian bảo vệ. Năng lượng từ ở 100 µH và 35 A là 61,25 mJ. Dòng bão hòa phải vượt dòng cắt cộng overshoot; chưa được đặt ngưỡng cắt chỉ bằng 35 A.

Cuối pha CV khi dòng giảm có thể vào DCM; công thức CCM và điều khiển phải được kiểm tra lại. Nếu dạng PWM thực tế cho fr=50 kHz thay vì 100 kHz, ripple tăng gấp đôi.

## 4. Cụm tụ đầu ra

Giữ 1.120 µF/160 V để khảo sát; chưa có dữ liệu ESR/ripple/lifetime của mã tụ cụ thể. Với 80 µH, ΔILpp=4,20 A:

- `ΔVCpp≈ΔILpp/(8·fr·C)` = **4,69 mV** lý tưởng.
- `ICrms≈ΔILpp/(2sqrt(3))` = **1,21 A RMS** tổng cụm.
- Nếu ESR tổng 10 mΩ, thành phần ESR 42 mV; tổng gần **46,7 mVpp**.
- Nếu ESR tổng 25 mΩ, tổng gần **109,7 mVpp**.

Các số này chỉ là ripple ổn định, không gồm quá độ, ESL, dây, pin và vòng điều khiển. Các tụ chia dòng theo trở kháng, không chỉ theo dung lượng. Năng lượng tụ tại 84 V≈3,95 J; cần xử lý nối pin/dòng nạp tụ. Điện áp 160 V có dự trữ so với 84 V nhưng chưa xác nhận tổn hao và nhiệt.

## 5. Biến áp 25:8: điều kiện lõi, chưa có chỉ dẫn quấn hoàn chỉnh

Với kích thích đối xứng: `Bpk≈Vbus·D/(4·fs·Np·Ae)`.

| Ae giả định | Bpk ở 420 V, Dmax 0,80, Np 25 | Bpk nếu vô tình D=1 |
|---|---:|---:|
| 250 mm² | 0,2688 T | 0,3360 T |
| 350 mm² | 0,1920 T | 0,2400 T |
| 400 mm² | 0,1680 T | 0,2100 T |
| 420 mm² | 0,1600 T | 0,2000 T |
| 500 mm² | 0,1344 T | 0,1680 T |

Nếu chọn mục tiêu minh họa Bpk≤0,16 T, Np 25 đòi Ae≥**420 mm²** với Dmax 0,80. **0,16 T chưa phải giới hạn đã xác nhận của vật liệu lõi**; phải có datasheet lõi, tổn hao ở 50 kHz/nhiệt độ, Ae/Aw, bobbin, cửa sổ dây và cách điện. Tính tại điểm chạy ổn định không thay kiểm tra khởi động và mất cân bằng volt–giây.

Dòng tải phản xạ sơ cấp đỉnh khoảng n·25,91≈**8,29 A** trước dòng từ hóa và dòng chuyển mạch. PSFB có dòng tuần hoàn; không chọn dây/MOSFET chỉ bằng P/Vbus. Cần Lm, Llk/điện cảm chuyển mạch, điện trở AC, cấu trúc quấn và kiểm tra nhiệt.

**Chưa chứng minh ZVS.** Phải so sánh `0,5·Lcomm·Icomm²` với tổng Eoss của cặp MOSFET ở bus thực tế, cộng điện dung ký sinh; kiểm tra Qoss/dead-time theo dòng và tải. Llk lớn có thể hỗ trợ chuyển mạch nhưng tăng mất duty/ringing. Chưa có mã MOSFET nên chưa chốt Lcomm hoặc dead-time. Không thể lấy thông số 25:8 để tự quấn trên một lõi bất kỳ.

## 6. PFC, dòng lưới và cuộn cảm

Với các giả thiết hiệu suất ở mục 1: Pbus≈2.105 W, Pin≈2.170 W.

| Vac | IAC RMS | Đỉnh dòng sin gần đúng |
|---|---:|---:|
| 198 V | 11,07 A | 15,66 A |
| 220 V | 9,96 A | 14,09 A |
| 242 V | 9,06 A | 12,81 A |

Cuộn cảm boost CCM: `ΔI=Vrect·(1−Vrect/Vbus)/(LPFC·fPFC)`; cực đại theo điện áp tức thời tại Vrect=Vbus/2.

Khảo sát **LPFC 560 µH, fPFC 65 kHz**; ở −20% L còn 448 µH, bus 420 V: ΔImax≈**3,606 App**. Đây là 28,1% đỉnh dòng lưới tại 242 V; tỷ lệ được so với *đỉnh dòng lưới*, không phải dòng tức thời ở mọi góc pha.

Ở 198 V, đỉnh dòng cuộn cảm tại đỉnh điện lưới≈**17,26 A**. Dự trữ 25% cho kết quả 21,58 A; vì vậy khảo sát **Isat≥22 A ở nhiệt độ nóng**, dòng nhiệt khoảng≥12 A sau kiểm tra ripple/loss. Cần tăng biên nếu bảo vệ có trễ hoặc L giảm thêm theo dòng. Chưa chốt lõi/dây/IC điều khiển nên đây chưa phải cuộn cảm được đặt mua. CCM không duy trì tới sát zero crossing với tải nhẹ; cần mô hình điều khiển PFC riêng.

Cầu diode, lọc EMI, đầu cắm, cầu chì, điện trở/NTC nạp tụ và bypass phải chịu dòng/nhiệt tương ứng. Không suy ra trị số cầu chì chỉ từ công suất. Mã QPFC/diode boost còn phải chọn theo tổn hao, reverse recovery và tản nhiệt.

## 7. Tụ bus PFC và ghi chú “390–400 V” trong hình

Ripple năng lượng100 Hz: `ΔVpp≈Pbus/(2π·50·Cbus·Vbus)`.

Phương án **2 × 470 µF/450 V song song** =940 µF:

| Mức bus đặt | C hiệu dụng | Ripple 100 Hz | Khoảng điện áp xấp xỉ |
|---|---:|---:|---:|
| 390 V | 940 µF | 18,28 Vpp | 380,86–399,14 V |
| 390 V | 752 µF (−20%) | 22,85 Vpp | 378,58–401,42 V |
| 400 V | 940 µF | 17,82 Vpp | 391,09–408,91 V |
| 400 V | 752 µF (−20%) | 22,28 Vpp | 388,86–411,14 V |

Do đó bus 390–400 V **không thể hiểu là giới hạn tức thời** khi dùng cụm tụ này. Dải thiết kế 380–420 V tạo khoảng để tiếp tục kiểm tra ripple/dung sai/điều khiển; không bảo đảm phần cứng thực tế luôn ở trong dải. Dòng ripple 100 Hz tổng cụm≈**3,72 A RMS** ở 400 V, chưa gồm cao tần. Cần kiểm tra mỗi tụ, chia dòng, ESR, nhiệt và tuổi thọ. Năng lượng 940 µF tại 400 V≈75,2 J; phải có nạp mềm/xả tụ.

Nếu bắt buộc điện áp luôn 390–400 V, với tâm 395 V thì C hiệu dụng≥1.697 µF; dung sai−20% đòi danh định≥2.121 µF, chưa gồm quá độ/lão hóa. Ba tụ film 4,7 µF trên cầu H chỉ là bypass cao tần 14,1 µF, không thay tụ bulk PFC.

## 8. Đo dòng và bảo vệ quá dòng

Shunt 0,5 mΩ tại 23,81 A: Vsense≈**11,90 mV**, P≈**0,283 W**; nếu đo ILrms=23,84 A thì P≈0,284 W. Loại 3 W có dự trữ danh định nhưng phải đấu Kelvin và xét nhiệt/đồng PCB.

Hình ghi **INA241A1**, khác INA240A1 bản trước. Gain **10 V/V là giá trị có điều kiện cần đối chiếu datasheet đúng mã**. Với G=10 và REF=0, tín hiệu tại 23,81 A chỉ 0,119 V; ADC 12 bit/3,3 V cho 0,161 A/LSB lý tưởng. Độ chính xác thực còn phụ thuộc offset, gain, shunt và nhiễu. INA240 có common-mode vận hành tới 80 V, không phù hợp đo high-side trực tiếp 84 V.

`Vsignal=VREF+G·Rsh·I`; `Itrip=(2,70−VREF)/(G·Rsh)`.

| Gain giả thiết | Itrip nếu REF=0 | Itrip nếu REF=1,65 V |
|---:|---:|---:|
| 10 | 540 A | 210 A |
| 20 | 270 A | 105 A |
| 50 | 108 A | 42 A |
| 100 | 54 A | 21 A |
| 200 | 27 A | 10,5 A |

Vì vậy ngưỡng 2,70 V trên hình **chưa được tính đúng thành bảo vệ dòng của bộ sạc**. Phải chốt gain/REF/cực tính/ngưỡng/delay/hysteresis/chốt lỗi. Cấp cảm biến 12 V có thể cho đầu ra vượt ADC 3,3 V khi bão hòa/lỗi; RC không thay mạch giới hạn áp. Bảo vệ cuộn cảm, cầu H và pin có thể cần các điểm đo khác nhau, không dùng một shunt đầu ra thay cho mọi sự cố. BMS không thay bảo vệ của bộ sạc.

## 9. Chia áp 390 kΩ/10 kΩ và ngưỡng OVP

Tỷ lệ 1/40: 84 V→**2,10 V**, 100 V→2,50 V. Comparator 2,70 V sẽ tương đương **108 V**, không phải ngưỡng bảo vệ sát mức nạp 84 V. Chọn Vtrip theo cell/BMS và dung sai rồi dùng `Vref=Vtrip/40`, bổ sung hysteresis và chốt lỗi; chưa được tự đặt ngưỡng cuối cùng khi chưa có yêu cầu của cell thực tế.

Rth=9,75 kΩ. Nếu thêm 1 kΩ và hai tụ 1 nF+100 nF cùng nút như hình: τ≈1,086 ms, fc≈146,6 Hz; phải đưa độ trễ này vào mô hình vòng điều khiển. Nhánh bảo vệ nhanh không mặc nhiên dùng chung lọc chậm. Độ phân giải đầu ra lý tưởng của ADC 12 bit≈32,2 mV/LSB. Điện trở 390 kΩ mất 17,2 mW tại 84 V nhưng còn yêu cầu điện áp làm việc/package/dung sai. Cần xử lý pin còn điện khi MCU mất nguồn để tránh backfeed ADC.

## 10. NTC và nhiệt

Hình có kéo lên 10 kΩ và NTC 100 kΩ: ở 25° C tín hiệu **3,00 V**. Không dùng bảng chuyển đổi của NTC 10 kΩ cho mạch này. Với NTC 100 kΩ, B=3950 K chỉ minh họa: 60° C→2,353 V; 80° C→1,846 V; 100° C→1,356 V. Cần thống nhất R 25/B/dung sai/bảng nội suy/ngưỡng nhiệt và phát hiện đứt/chập. Ba vị trí MOSFET, tản nhiệt, biến áp có thể cần ngưỡng khác nhau.

## 11. Tổn hao và thông số linh kiện công suất

Cầu diode có hai diode dẫn, với Vf=0,8 V minh họa: `P≈2VfI≈38,1 W` tại 23,81 A, chưa gồm reverse recovery. Vs thứ cấp tối đa 134,4 V trước ringing nên không chọn diode chỉ theo 84 V. Có thể khảo sát lớp 200–250 V, nhưng mã cụ thể phải đạt biên điện áp, dòng, nhiệt và xung đo được; chưa phải đề xuất mua.

MOSFET 650 V mới là lớp điện áp: cần RDS(on) nóng, Qg, Eoss, Qoss, dead-time, spike VDS, tản nhiệt. Mỗi 1 mΩ trong đường DC làm mất 0,567 W ở 23,81 A; 10 mΩ làm mất 5,67 W. Đồng PCB, đầu nối, dây và Kelvin ảnh hưởng lớn tới hiệu suất.

“Tối ưu” cần tiêu chí chi phí/hiệu suất/kích thước và số đo. Chỉnh lưu đồng bộ có thể giảm tổn hao nhưng thêm MOSFET/driver/điều khiển. Chưa có cơ sở để gọi bản hiện tại tối ưu nhất.

## 12. Phụ lục: vì sao không giữ thông số 58 V cũ

| Thông số | 20S 84 V đang thiết kế | 58 V phương án cũ |
|---|---:|---:|
| Dòng tại 2 kW | 23,81 A | 34,48 A |
| Shunt 0,5 mΩ, tổn hao DC | 0,283 W | 0,595 W |
| Tổn hao hai diode, Vf=0,8 V | 38,1 W | 55,2 W |
| Mỗi 1 mΩ đường dẫn | 0,567 W | 1,189 W |

Chỉ là đối chiếu; **không dùng ngưỡng sạc của 84 V cho pin 58 V hoặc ngược lại**. File JSON vẫn giữ các điểm tính 58 V để truy vết.

## 13. Những thông số còn thiếu trước khi chốt PCB/Gerber

Cần sơ đồ chân bo STM32 đang có, datasheet cell/BMS thực tế; nguồn phụ và nguồn lái cách ly; IC điều khiển PFC; mã MOSFET/diode; lõi/dây/cách điện của biến áp và cuộn cảm; ngưỡng bảo vệ; tản nhiệt/cơ khí. Mục tiêu pin hiện tại là 20S/50 Ah và BMS cho phép dòng sạc liên tục ≥30 A, chưa phải tên sản phẩm đã xác minh. Sau đó mới chốt BOM/footprint/netlist, đường đồng, cách điện và kiểm tra ERC/DRC. Bản vẽ tổng hợp dễ nhìn không thay cho PCB đúng net và đã kiểm tra layout.
