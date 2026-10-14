# Thiết kế và tinh chỉnh bộ sạc pin 2 kW dùng hai vòng PI

Đồ án môn Thiết kế và tinh chỉnh PID — hoàn thiện ngày 14/10/2026. Thông số được tự chọn theo yêu cầu người dùng. Đối tượng nghiên cứu là tầng DC/DC và điều khiển CC–CV; phần chỉnh lưu/PFC được biểu diễn bằng nguồn DC tương đương.

## 1. Mục tiêu và thông số lựa chọn

Thiết kế bộ sạc có công suất đầu ra danh định 2.000 W cho pin LiFePO₄ 16S, 100 Ah. Chọn điều khiển PI nối tầng: vòng trong điều khiển dòng cuộn cảm, vòng ngoài điều khiển điện áp pin. PI là trường hợp PID có Kd = 0. Tối ưu ở đây là chọn bộ tham số có chỉ tiêu động học tốt nhất trong lưới khảo sát đã xác định; không phải chứng minh hiệu suất, giá thành hoặc tuổi thọ pin tối ưu toàn cục.

| Đại lượng | Giá trị chọn | Ý nghĩa |
|---|---|---|
| Nguồn vào | 220 V AC, 50 Hz | Nguồn lưới dự kiến |
| Công suất đầu ra | 2.000 W | Định mức bộ sạc, không phải công suất động cơ |
| Pin | LiFePO₄, 16S, 100 Ah | Giả định cho đồ án; chưa chọn hãng/cell cụ thể |
| Điện áp danh định pin | 51,2 V | 16 × 3,2 V |
| Giới hạn điện áp pin giả định | 58,4 V | 16 × 3,65 V; phải xác nhận lại bằng datasheet cell/BMS thực |
| Giá trị đặt CV | 58,0 V | 3,625 V/cell trung bình; chừa 0,4 V dưới giới hạn pack |
| Dòng CC | 34,4827586 A | 2.000/58,0; xấp xỉ 0,345 C với pin 100 Ah |
| Bus PFC dự kiến | 400 V DC | Tầng PFC không được mô phỏng trong bài này |
| Tỷ số biến áp tương đương | n = Ns/Np = 0,20 | Veq = nVdc = 80 V |
| L; điện trở cuộn cảm | 100 µH; 0,01 Ω | Tham số tầng lọc quy đổi thứ cấp |
| C đầu ra | 1.000 µF | Chưa đưa ESR vào mô hình động học |
| Điện trở pin tương đương Rb | 0,08 Ω | Tham số đối tượng minh họa, không phải giá trị đã đo của pack 100 Ah |
| Chu kỳ lấy mẫu | 20 µs | fs = 50 kHz; trễ tác động 1 mẫu |
| Giới hạn điều khiển | 0 ≤ d ≤ 0,90 | Duty hiệu dụng của mô hình quy đổi |
| Tốc độ tăng dòng đặt | 1.000 A/s | Khoảng 34,5 ms để tăng từ 0 lên dòng CC |
| Bộ lọc đo | Dòng 5 kHz; áp 1 kHz | Bộ lọc bậc nhất rời rạc |

58,0 V là giá trị đặt, còn 58,4 V là giới hạn pin giả định; không dùng lẫn hai số này. Giới hạn tổng điện áp pack không bảo đảm từng cell đều dưới 3,65 V: BMS phải giám sát từng cell và có quyền ngắt sạc. Dòng cho phép thực tế còn bị giới hạn bởi cell, BMS, dây dẫn và nhiệt độ.

Với CC cố định 34,483 A, công suất tăng theo điện áp pin: tại 51,2 V là khoảng 1.765,5 W, tại 58,0 V là 2.000 W. Đây là CC–CV có giới hạn công suất, không phải sạc công suất không đổi 2 kW trong toàn bộ chu trình.

## 2. Kiến trúc và tính chọn sơ bộ mạch công suất

Sơ đồ khối: 220 VAC → bảo vệ/lọc EMI và chỉnh lưu → PFC bus 400 VDC → cầu toàn phần dịch pha có biến áp cách ly → chỉnh lưu thứ cấp/lọc LC → pin và BMS. Có thể cân nhắc chỉnh lưu đồng bộ ở thứ cấp vì dòng sạc trên 34 A. PSFB được chọn vì thuận tiện xây dựng mô hình điều khiển quy đổi; chưa có so sánh tổn hao để kết luận tốt hơn LLC cho phần cứng thực.

Đầu ra điều khiển trong bài là d hiệu dụng của PSFB quy đổi kiểu buck. Quan hệ v ≈ nVdc·d chỉ là xấp xỉ lý tưởng; khi thiết kế cầu dịch pha thật phải tính dead-time, điện cảm rò, sụt áp và mất duty. Không đưa trực tiếp d trong mã MATLAB vào cổng công suất khi chưa thiết kế bộ PWM/driver tương ứng.

Giả sử hiệu suất mục tiêu η = 94% và PF = 0,99:

```text
IAC ≈ Pout/(VAC × η × PF)
    = 2000/(220 × 0,94 × 0,99) ≈ 9,77 A rms.
```

η và PF ở đây là mục tiêu để tính sơ bộ đầu vào; mô hình trung bình hiện tại không chứng minh đạt 94% hoặc PF 0,99.

Duty danh định tại cuối vùng CC:

```text
d ≈ (Vref + rL·ICC)/Veq
  = (58 + 0,01×34,48276)/80 = 0,72931.
```

Ở Veq = 72 V, duty yêu cầu khoảng 0,81035, còn khoảng dự phòng so với dmax = 0,90. Tính sơ bộ gợn với tần số xung hiệu dụng sau chỉnh lưu feq = 50 kHz:

```text
ΔiL,pp ≈ Vout(1−d)/(L·feq) ≈ 3,14 A tại Veq = 80 V.
ΔvC,pp ≈ ΔiL,pp/(8·feq·C) ≈ 7,9 mV, chưa kể ESR.
```

Nếu ESR tổng là 5 mΩ thì phần gợn ESR ước tính khoảng 15,7 mV. Đây là ước lượng chuyển mạch sơ bộ; đồ thị mô phỏng trung bình không thể hiện hay xác nhận gợn này. Tần số hiệu dụng của xung thứ cấp phải được đối chiếu với tần số cầu PSFB thực, không đồng nhất tùy tiện với tần số đóng cắt của từng khóa.

| Hạng mục | Lựa chọn sơ bộ | Việc còn phải kiểm tra khi làm phần cứng |
|---|---|---|
| Cuộn cảm đầu ra | 100 µH, mục tiêu dòng bão hòa ≥45 A | Dòng đỉnh gồm gợn, suy giảm L theo dòng/nhiệt, tổn hao lõi và đồng |
| Tụ đầu ra | 1.000 µF, cấp điện áp 100 V | ESR, dòng ripple và sự cố tải hở |
| Tụ bus PFC | Khoảng 1.000 µF/450 V để khảo sát | Dòng ripple, tuổi thọ, hold-up, dòng nạp và xả tụ |
| Biến áp cách ly | Khoảng 2 kW, tỷ số quy đổi 5:1 | Lõi, số vòng, điện cảm từ hóa/rò, cách điện và nhiệt |
| Khóa công suất/driver | Chưa chốt mã linh kiện | Chọn theo áp đỉnh, dòng RMS/đỉnh, tổn hao và phối hợp driver |
| Đo dòng/áp | Đo iL và điện áp pin; nên giám sát cả ibat | Dải đo, offset, băng thông, cách ly và sai số ADC |

Ví dụ tụ bus: với gợn 20 V đỉnh–đỉnh, giả thiết PFC một pha lý tưởng, Cbus ≈ P/(2πfline·Vdc·ΔVpp) ≈ 796 µF; chọn 1.000 µF chỉ là điểm xuất phát. Mô hình này chưa tính PFC, EMI, tổn hao đóng cắt, nhiệt và cách điện; bảng trên chưa phải BOM chế tạo.

## 3. Mô hình toán học của đối tượng

Gọi i là dòng cuộn cảm; v là điện áp đầu cực pin; E là sức điện động tương đương; Rb là điện trở pin; rL là điện trở cuộn cảm; Veq = nVdc. Phương trình trung bình:

```text
L·di/dt = Veq·d − v − rL·i
C·dv/dt = i − (v−E)/Rb
ibat = (v−E)/Rb = i − C·dv/dt
```

Dòng cuộn cảm và dòng pin chỉ bằng nhau ở trạng thái xác lập. Vòng trong điều khiển iL, còn tiêu chí dòng sạc và công suất trong báo cáo được tính từ ibat. Khởi tạo i(0)=0, v(0)=E(0)=50 V; không đặt tụ đầu ra 0 V khi đang nối nguồn pin lý tưởng vì sẽ tạo dòng phóng giả.

Tuyến tính hóa tại E và Veq cố định, đặt:

```text
D(s) = L·Rb·C·s² + (L+rL·Rb·C)·s + (rL+Rb)
Gi,d(s) = i(s)/d(s) = Veq(Rb·C·s+1)/D(s)
Gv,d(s) = v(s)/d(s) = Veq·Rb/D(s)
```

Thay số: D(s) = 8×10⁻⁹s² + 1,008×10⁻⁴s + 0,09. Hai cực hở xấp xỉ −967,08 và −11.632,92 rad/s; zero của đường dòng ở −12.500 rad/s. Đây là mô hình điện trung bình của đối tượng đã chọn, chưa phải mô hình điện hóa LiFePO₄.

Rb = 80 mΩ là giả định để học mô hình và tinh chỉnh; không suy ra từ dung lượng 100 Ah. Với dòng CC, nó gây sụt áp khoảng 2,76 V trong mô hình. Khi có pack thật, phải nhận dạng lại Rb và bổ sung nhánh phân cực/OCV–SOC nếu muốn dự báo quá trình sạc, nhiệt hoặc tuổi thọ.

## 4. Thiết kế hai vòng PI nối tầng

Vòng áp sinh dòng đặt; vòng dòng sinh điện áp điều khiển bù, sau đó chuẩn hóa thành duty:

```text
ev = Vref − vdo
uv = Kpv·ev + zv
Icap = min(ICC, IBMS, 2000/max(vdo,58))
Iref = sat(uv, 0, Icap), có giới hạn tốc độ tăng 1000 A/s

ei = Iref − ido
ui = Kpi·ei + zi                    [ui tính bằng V]
d = sat((vdo + ui)/Veq, 0, 0,90)
```

Trong mã mô phỏng, `lim` là giới hạn dòng ngoài để thử lệnh giảm dòng BMS; chưa có truyền thông BMS thực. Khi vòng áp muốn dòng lớn hơn giới hạn, bộ sạc làm việc ở CC. Khi gần Vref, dòng đặt giảm và điện áp được giữ ở CV. Hai chế độ dùng cùng vòng điều khiển, không phải đổi đột ngột sang bộ tích phân khác.

Với feedforward chỉ bù v và chuẩn hóa Veq chính xác, bỏ qua lọc/trễ/bão hòa để tính bộ ban đầu:

```text
Gi,ui(s) = 1/(L·s+rL)
Kpi = L·ωi;          Kii = rL·ωi
Gv,i(s) = Rb/(Rb·C·s+1)
Kpv = C·ωv;          Kiv = ωv/Rb
ωi = 2πfi;           ωv = 2πfv
```

Không cộng thêm rL·i đo vào feedforward rồi vẫn sử dụng nguyên công thức trên, vì việc đó làm thay đổi đối tượng vòng dòng. Bộ cuối dùng đầu ra PI dòng theo đơn vị volt, không phải duty; đây là điểm quan trọng khi nhập gain vào mô hình khác.

| Vòng / tham số | Bộ ban đầu (fi=1000 Hz, fv=20 Hz) | Bộ đã chỉnh (fi=1200 Hz, fv=100 Hz) | Đơn vị |
|---|---|---|---|
| Kpi | 0,62831853 | 0,75398224 | V/A |
| Kii | 62,8318531 | 75,3982237 | V/(A·s) |
| Kdi | 0 | 0 | Không dùng thành phần D |
| Kpv | 0,12566371 | 0,62831853 | A/V |
| Kiv | 1570,796327 | 7853,981634 | A/(V·s) |
| Kdv | 0 | 0 | Không dùng thành phần D |

Nếu đầu ra PI dòng là duty trực tiếp tại Veq cố định 80 V, hệ số tương đương là Kpi,d = 0,00942478 A⁻¹ và Kii,d = 0,94247780 (A·s)⁻¹, đồng thời vẫn cần bù v/80. Không trộn hai quy ước này. Bản mã được giao dùng quy ước volt để chuẩn hóa biến thiên bus.

Lý do chọn PI: đối tượng điện sau bù có cấu trúc bậc thấp, thành phần I loại sai lệch xác lập, còn thành phần D khuếch đại nhiễu đo. Không có bằng chứng trong bài rằng cần thêm D để đạt chỉ tiêu. Nếu môn học bắt buộc so sánh PID đủ ba thành phần, phải thêm bộ lọc D và đánh giá lại trên cùng tập thử; không tự gán Kd khác 0 để gọi là PID.

Hai tích phân dùng chống tích lũy khi bão hòa kiểu clamping. Với vòng áp, phải tính cả giới hạn dòng và giới hạn tốc độ tăng dòng; chỉ cập nhật zv khi sai số không đẩy lệnh sâu hơn vào giới hạn. Tương tự với zi và giới hạn duty. Cập nhật tích phân Euler thuận bằng Ki·e·Ts, không nhân Ts hai lần.

## 5. Cách tìm tham số và phạm vi của chữ “tối ưu”

Khảo sát fi ∈ {600,800,1000,1200,1400,1600,1800} Hz và fv ∈ {40,60,80,100,120,140,160,180} Hz, giữ fi ≥ 10fv: tổng cộng 35 cặp. Tất cả dùng cùng tín hiệu nhiễu giả lập, seed 20261012: độ lệch chuẩn đo dòng 0,03 A và áp 0,003 V trước bộ lọc.

Chỉ tiêu không thứ nguyên được đặt trước khi tìm kiếm:

```text
J = IAECC/0,01 + (OVCV/0,15)² + IAECV/0,001
    + 0,3·(RMS(Δd)/0,001)²
IAECC: tích phân |ibat−Iref| từ 0,035 đến 0,095 s [A·s]
IAECV: tích phân |v−Vref| từ 0,25 đến 0,40 s [V·s]
OVCV: max(0, max(v−Vref)) trên toàn phép thử [V]
```

Không phạt điện áp thấp hơn Vref trong vùng CC như một lỗi điều khiển áp: khi CC, điện áp phụ thuộc trạng thái pin. Thành phần RMS(Δd) hạn chế lựa chọn gain quá nhạy, nhưng không phải mô hình tổn hao đóng cắt hay phép đo hiệu suất.

Điều kiện lọc ứng viên: Vpeak <58,30 V; Ibat,peak <35,2 A; Pbat,peak <2.040 W. Ngưỡng 2.040 W là tiêu chí cho quá độ 2%, không thay định mức liên tục 2.000 W. Trong các ca đã kiểm tra, công suất đỉnh thực tế của bộ được chọn vẫn dưới 2.000 W.

Kết quả chọn fi = 1.200 Hz, fv = 100 Hz; J ≈ 2,17165. Đây là cặp tốt nhất trong 35 cặp, trên đối tượng và hàm mục tiêu đã công bố; không khẳng định là nghiệm tối ưu toàn cục. Lưới đầy đủ nằm trong BANG_TIM_KIEM_PI.csv.

## 6. Kết quả mô phỏng và ổn định

Mô hình kiểm chứng dùng ZOH chính xác cho phần tuyến tính trong mỗi mẫu, chu kỳ 20 µs, trễ tác động một mẫu, hai bộ lọc đo, bão hòa duty, giới hạn dòng/tốc độ tăng và chống windup. Gần dòng bằng 0 có chặn iL ≥0 để xấp xỉ chỉnh lưu; chưa mô hình hóa DCM chi tiết.

Phép thử chuyển CC–CV: E bắt đầu ở 50 V, tăng đến 57,8 V trong khoảng 0,10–0,22 s; giới hạn dòng ngoài giảm xuống 20 A tại 0,05–0,07 s; Veq thay đổi 80→72→88 V ở 0,27/0,32 s. Đây là kích thích của bộ giả lập pin để thử động học, không phải pin 100 Ah được sạc đầy trong 0,4 s.

| Chỉ tiêu, các ca không thêm nhiễu | Bộ ban đầu | Bộ đã chỉnh |
|---|---|---|
| Vượt áp lớn nhất trong phép thử chuyển CC–CV | 0,51410 V | 0,12089 V |
| Điện áp đỉnh tương ứng | 58,51410 V | 58,12089 V |
| Xác lập dòng CC, dải ±2% của ICC | 35,64 ms | 34,30 ms |
| Xác lập bước CV 57,6→58,0 V, dải ±8 mV | 30,14 ms | 8,16 ms |
| Dòng pin đỉnh trong phép thử chuyển chế độ | 34,5022 A | 34,4997 A |

Bộ ban đầu vượt giới hạn 58,4 V trong phép thử nhanh, nên không được chọn. Bộ đã chỉnh giảm độ vượt áp khoảng 76,5%. Thời gian tăng dòng bị chủ ý giới hạn bằng ramp, do đó không đánh giá chất lượng chỉ qua việc khởi động càng nhanh càng tốt.

Kiểm tra độc lập ngoài tập tinh chỉnh: L lệch ±20%, C lệch ±30%, Rb lệch ±50%, đủ 8 tổ hợp biên, có cùng mức nhiễu đo. Cả 8 đạt tiêu chí kiểm tra; điện áp đỉnh lớn nhất 58,21105 V, công suất đỉnh lớn nhất khoảng 1.997,47 W. Kiểm tra này không chứng minh cho mọi cell, mọi nhiệt độ hoặc mọi sự cố phần cứng.

| Chỉ tiêu tín hiệu nhỏ rời rạc danh định | Vòng dòng | Vòng áp |
|---|---|---|
| Tần số cắt thực tế | 1148,20 Hz | 99,38 Hz |
| Dự trữ pha | 72,86° | 79,72° |
| Dự trữ biên độ | 16,42 dB | 25,86 dB |

Các dự trữ được tính từ mô hình rời rạc có lọc, ZOH, một mẫu trễ và PI Euler, tại điểm CV không bão hòa, bus/E cố định. Vòng áp được xét khi vòng dòng đã đóng. Mô hình kín 7 trạng thái có mọi trị riêng nằm trong vòng tròn đơn vị cả danh định và 8 tổ hợp biên; bán kính phổ danh định khoảng 0,998001. Không lấy dự trữ của mô hình tuyến tính để đảm bảo ổn định khi tải hở hoặc sự cố chuyển mạch.

Thử bão hòa riêng: Veq giảm xuống 55 V trong 0,08–0,14 s. Bộ sạc không đủ áp để giữ dòng CC và duty chạm 0,90; sau phục hồi, dòng trở lại đặt, đỉnh khoảng 34,733 A. Mục tiêu là kiểm tra hồi phục tích phân, không tuyên bố vẫn cung cấp 2 kW khi nguồn không đủ.

## 7. Trình tự sạc và các bảo vệ cần bổ sung cho hệ thống thật

Trình tự đề xuất: kiểm tra pin/BMS và điều kiện cho phép → tăng dòng mềm → CC → CV → kết thúc sạc khi dòng pin nhỏ hơn 5 A liên tục 5 s trong vùng CV → tắt lệnh công suất. Chỉ đếm điều kiện kết thúc sau khi đã thực sự vào vùng CV; không kết luận đầy pin từ dòng nhỏ ở thời điểm khởi động hoặc do thiếu áp đầu vào.

Ngưỡng 5 A (0,05 C) và thời gian 5 s là giá trị lựa chọn cho đồ án; phải chỉnh theo cell/BMS thực. Không sạc nhỏ giọt vô thời hạn sau khi kết thúc. BMS giảm dòng/ngắt khi cell hoặc nhiệt độ yêu cầu; không chỉ kiểm tra điện áp tổng pack.

Hệ thống chế tạo cần có bảo vệ quá dòng nhanh, quá áp, ngắn mạch, ngược cực, mất kết nối pin, quá nhiệt, quá/thiếu áp bus, liên động BMS, mạch nạp/xả tụ và cách ly phù hợp. Các chức năng này không được thay bằng một vòng PI. Phần mềm kèm theo tập trung kiểm chứng điều khiển; chưa triển khai firmware PWM, truyền thông BMS, bộ quản lý kết thúc sạc hoặc động học ngắt sự cố.

Chỉ riêng phép tính lý tưởng 60 Ah/34,483 A cho đoạn 20%→80% SOC là khoảng 1,74 giờ nếu toàn đoạn giữ CC và hiệu suất coulomb 100%. Đây không phải thời gian sạc đầy: pha CV, giới hạn nhiệt, dung lượng thực và trạng thái pin làm thay đổi kết quả. Mã hiện tại không tính SOC hoặc dự báo thời gian sạc.

## 8. Cách chạy MATLAB và dựng mô hình trên Simulink

Mở THIET_KE_BO_SAC_2KW.m rồi Run toàn bộ. Script dùng MATLAB cơ bản R2018b trở lên, không cần Control System Toolbox. Nó chạy bộ ban đầu và bộ đã chỉnh, ba ca transition/cc/cv_step; bật runSaturationStress=true để chạy thêm ca bão hòa. Kết quả CSV, PNG, FIG và MAT được ghi vào ket_qua_MATLAB bên cạnh tệp .m.

MATLAB mặc định không thêm nhiễu để đối chiếu với các số liệu không nhiễu trong báo cáo. Phép tìm kiếm 35 cặp và 8 ca biên có nhiễu được thực hiện bằng mã Python trong thư mục KIEM_CHUNG_PYTHON. Script MATLAB dùng bộ hệ số đã chọn; không tự thực hiện tìm kiếm tối ưu khi Run.

Để dựng Simulink: dùng khối State-Space liên tục với hai trạng thái [iL,v], ma trận A/B như trong code; khối đo dòng/áp và bộ lọc; hai PI rời rạc; giới hạn dòng, ramp tăng, clamping; khối chuẩn hóa (v+ui)/Veq; Saturation 0…0,90; Unit Delay Ts ở duty. Để khớp hoàn toàn phép thử số, có thể dùng Discrete State-Space với Ad/Bd từ expm và các khối rời rạc Ts=20 µs. Lưu ý đầu vào plant là [Veq·d_applied,E], không phải chỉ duty.

Không đồng thời dùng PI liên tục và gain Ki đã nhân Ts trong mã rời rạc. Bộ lọc dùng y[k]=a·y[k−1]+(1−a)·x[k], a=exp(−2πfcTs). Tên tín hiệu trong MATLAB sử dụng quy ước kỹ thuật và chú thích tiếng Việt không dấu để hạn chế lỗi font.

Đã kiểm tra cú pháp bằng MISS_HIT theo MATLAB 2018b, và chạy mô hình Python tương ứng. Môi trường này không có MATLAB/Simulink/Octave, nên chưa có kết quả thực thi MATLAB gốc hay tệp .slx đã xác nhận chạy. Cần chạy script trong MATLAB của bạn, đối chiếu các chỉ tiêu và chỉnh tham số nếu đổi đối tượng.

## 9. Tài liệu tham khảo và kết luận thiết kế

[1] Richard M. Murray, Karl J. Åström, ví dụ Cruise control của Python Control Systems Library: https://raw.githubusercontent.com/python-control/python-control/main/examples/cruise.ipynb. Đã đọc phần PI, bão hòa và anti-windup. Ví dụ dùng back-calculation; bài này dùng clamping, không sao chép gain điều khiển xe sang bộ sạc.

[2] PyBaMM, Tutorial 5 – Run experiments: https://raw.githubusercontent.com/pybamm-team/PyBaMM/develop/docs/source/examples/notebooks/getting_started/tutorial-5-run-experiments.ipynb. Đã đọc cách biểu diễn pha CC, giữ điện áp CV và kết thúc theo dòng. Giá trị pin trong ví dụ không được dùng làm giới hạn LiFePO₄ của bài này.

[3] Python Control Systems Library, rootlocus_pid_designer trong control/sisotool.py: https://raw.githubusercontent.com/python-control/python-control/main/control/sisotool.py. Đã đọc quy ước PID song song, bộ lọc D và cách đánh giá đáp ứng/tần số.

Các thông số cell, mạch PSFB và PFC là lựa chọn thiết kế cần xác nhận khi chọn linh kiện. Các trang tài liệu MathWorks/TI thử truy cập bị chặn, nên không dùng chúng làm bằng chứng đã kiểm chứng phần cứng.

Kết quả của đồ án là mô hình điều khiển 2 kW, bộ PI có đơn vị và cách tính rõ ràng, thuật toán chống windup, kết quả tinh chỉnh có thể tái lập và mã MATLAB để chạy thử. Bước tiếp theo trước chế tạo là nhận dạng pack thật, mô phỏng chuyển mạch/driver, thiết kế từ tính–nhiệt–cách điện và thử công suất tăng dần với tải/nguồn thử phù hợp.
