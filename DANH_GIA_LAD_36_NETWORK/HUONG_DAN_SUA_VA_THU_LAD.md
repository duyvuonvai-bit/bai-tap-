# Rà soát và sửa chương trình LAD đài phun nước

Ngày: 11/10/2026. Đối tượng: CPU S7-1200 1214C AC/DC/Relay, TIA Portal V16. Tài liệu này độc lập với đồ án để chạy thử trước.

## 1. Kết luận và phạm vi kiểm tra

Logic chính của 36 Network bạn gửi **đúng với yêu cầu công nghệ trên hình**: lịch sáng 06:00–08:00, lịch chiều 17:00–20:30, năm bước 10 s, bơm chạy liên tục trong chu trình và bốn van đúng bảng. Không cần viết lại toàn bộ chỉ vì có 36 Network.

Điểm cần bổ sung rõ nhất là **bảo vệ giá trị bước ngoài miền 0–5**. Nếu bước bị ghi thành 6 hoặc số âm, bản gốc có thể vẫn báo đang chạy nhưng tắt mọi bơm/van, không báo lỗi và không tự thoát. Đây là tình huống dữ liệu bị ghi sai; không phải lỗi tự xảy ra trong chu trình bình thường từ bước 0.

Các điểm cần làm rõ khi dựng trong TIA: I0.4 và I0.5 bằng 1 khi bình thường; tên DB/tag trong hình minh họa chưa trùng hoàn toàn ảnh dự án; R_TRIG và TON phải được thực hiện mỗi vòng quét, với instance riêng. Việc dùng năm TON, biến bước hiện tại/bước tiếp theo và chốt STOP riêng đều có lý do, không nên xóa tùy tiện.

Đã đọc 36 hình riêng và đối chiếu ảnh bảng tag/DB. Hai ZIP bạn gửi có cùng SHA256 và cùng 43 ảnh. Các hình Network có ghi “HÌNH LAD MINH HỌA · KHÔNG PHẢI ẢNH CHỤP TIA PORTAL”. Bộ gửi không chứa dự án .ap16/.zap16 hay nguồn XML của TIA. Vì vậy đây là **kiểm tra logic từ hình và kiểm thử mô hình độc lập**, chưa phải xác nhận Compile/PLCSIM thành công. Hình LAD mới là bản thiết kế để dựng lại và thử trong TIA, không phải ảnh chụp chương trình đã biên dịch.

## 2. Đối chiếu yêu cầu công nghệ

| Nội dung | Yêu cầu / kết quả đọc từ bản gốc | Đánh giá |
|---|---|---|
| Chế độ AUTO | I0.0 chọn AUTO; phải có quyền AUTO trước khi vận hành | Đúng; chống tự chạy sau cấp nguồn là phần thiết kế bổ sung |
| Ca sáng | 06:00:00 ≤ giờ < 08:00:00 | Đúng NW03 |
| Ca chiều | 17:00:00 ≤ giờ < 20:30:00 | Đúng NW04 |
| Thời gian mỗi bước | Năm TON riêng, PT = T#10s | Đúng cấu trúc; chuyển bước chịu độ trễ vòng quét |
| Bơm | Có lệnh ON liên tục ở cả năm bước khi được phép chạy | Đúng NW30–35 |
| Dừng | Hết giờ, STOP, quá tải, thiếu nước | Có đủ; dừng khẩn được bổ sung |
| RESET và khởi động lại | OFF → phục hồi điều kiện → nhấn RESET mới → AUTO sau STOP/lỗi | Chính sách bổ sung hợp lý, cần hướng dẫn người vận hành |

| Bước | Thời gian đặt | Van 1 | Van 2 | Van 3 | Van 4 | Mask, V1 là bit 0 | Bơm |
|---|---|---|---|---|---|---|---|
| 1 | 10 s | Mở | Đóng | Đóng | Đóng | 1 | ON |
| 2 | 10 s | Mở | Mở | Đóng | Đóng | 3 | ON |
| 3 | 10 s | Mở | Mở | Mở | Đóng | 7 | ON |
| 4 | 10 s | Mở | Mở | Mở | Mở | 15 | ON |
| 5 | 10 s | Đóng | Mở | Đóng | Mở | 10 | ON |

Khi dừng, bước về 0 và Q0.0–Q0.4 OFF. Chu kỳ hợp lệ lặp 1 → 2 → 3 → 4 → 5 → 1. Cách ghi chuỗi bốn bit theo thứ tự V1,V2,V3,V4 là 1000, 1100, 1110, 1111, 0101; không đọc chuỗi này như số nhị phân với V1 là bit cao nhất rồi nhầm với cột mask.

## 3. Nhận xét từng Network gốc

| NW gốc | Chức năng | Nhận xét / việc cần làm |
|---|---|---|
| 01 | RD_LOC_T | Giữ; gọi mỗi scan. Cấu hình CPU UTC+7, DST tắt ở Việt Nam; kiểm tra giờ thực tế. |
| 02 | rtc_ok khi RET_VAL=0 | Hợp lệ ở cấu hình Việt Nam. Bản đề xuất nhận 0 hoặc 1 và kiểm tra miền giờ/phút/giây; 1 là thành công khi DST có hiệu lực. |
| 03 | Ca sáng | Đúng 06:00 đến trước 08:00; giữ. |
| 04 | Ca chiều | Đúng 17:00 đến trước 20:30; giữ. |
| 05 | Trong giờ | Đúng OR hai ca; giữ. |
| 06 | Điều kiện đầu vào | Đúng nếu nước, E-stop, quá tải, STOP đều healthy=1; làm rõ tên I0.4/I0.5. |
| 07 | Lỗi công nghệ hiện tại | Giữ ba lỗi gốc; thêm lỗi bước. Chốt lỗi RTC khi AUTO là cải tiến tùy chính sách. |
| 08 | Cạnh RESET | Đúng ý định; dùng instance riêng, gọi mỗi scan, nút nối CLK. |
| 09 | Chốt lỗi SR | Đúng. SR có R1 ưu tiên RESET; khi thêm loại lỗi mới, điều kiện ACK phải yêu cầu loại lỗi đó đã hết. |
| 10 | Chốt STOP SR | Hợp lý; STOP không tự chạy lại khi nhả nút. Có thể dùng chung điều kiện ACK. |
| 11 | Ghi nhận đã TẮT | Giữ cuộn SET, start FALSE, không Retain; không đổi thành cuộn thường. |
| 12 | Cạnh AUTO | Đúng ý định; instance riêng với RESET, gọi mỗi scan. |
| 13 | Thu hồi quyền AUTO | Đúng. Không thêm “ngoài giờ” vào đây nếu muốn ca kế tiếp tự chạy. |
| 14 | Chốt quyền AUTO | Đúng; ưu tiên thu hồi quyền. Bản mới bổ sung chặn vòng quét khởi tạo. |
| 15 | Điều kiện chạy | Đúng; các điều kiện lặp là kiểm tra cuối dễ đọc, không phải lỗi. |
| 16 | next = current | Giữ, đặt trước các nhánh đổi bước. |
| 17 | Dừng → next = 0 | Đúng; timer vẫn phải được gọi để reset. |
| 18 | Bắt đầu từ 0 → 1 | Đúng; không thay bằng “ngoài miền → 1” vì dễ tự khởi động lại âm thầm. |
| 19 | TON bước 1 | Giữ PT=10s, instance riêng, IN=Run AND bước=1. |
| 20 | TON bước 2 | Giữ PT=10s, instance riêng, IN=Run AND bước=2. |
| 21 | TON bước 3 | Giữ PT=10s, instance riêng, IN=Run AND bước=3. |
| 22 | TON bước 4 | Giữ PT=10s, instance riêng, IN=Run AND bước=4. |
| 23 | TON bước 5 | Giữ PT=10s, instance riêng, IN=Run AND bước=5. |
| 24 | 1 → 2 | Đúng; ghi NextStep, không ghi CurrentStep. Có thể thêm Run vào điều kiện để dễ kiểm tra. |
| 25 | 2 → 3 | Đúng; không thay đổi CurrentStep ở đây. |
| 26 | 3 → 4 | Đúng; không thay đổi CurrentStep ở đây. |
| 27 | 4 → 5 | Đúng; không thay đổi CurrentStep ở đây. |
| 28 | 5 → 1 | Đúng vòng lặp; không chuyển sang bước 6. |
| 29 | Chốt current = next | Đúng vị trí sau cả năm timer/chuyển bước; giữ một điểm commit trong vận hành. |
| 30 | Van 1, bước 1–4 | Đúng. |
| 31 | Van 2, bước 2–5 | Đúng. |
| 32 | Van 3, bước 3–4 | Đúng. |
| 33 | Van 4, bước 4–5 | Đúng, kể cả bước 5. |
| 34 | Có lệnh mở van | Đúng cho giám sát lệnh; không chứng minh van đã mở cơ khí. Bản tối ưu thay bằng guard bước hợp lệ. |
| 35 | Lệnh bơm | Đúng, không cố ý tắt bơm giữa các bước. |
| 36 | Đèn lỗi | Đúng chính sách gốc. Nếu đã chốt cả RTC vào Nho_Loi, chỉ cần đèn = Nho_Loi. |

Không có cơ sở khẳng định thiếu instance timer chỉ vì ảnh DB1 không hiện timer: chúng có thể nằm trong các instance DB khác. Cần kiểm tra cây Program blocks và Cross-reference của dự án thực.

## 4. Cách sửa ít nhất trên chương trình hiện có

Nếu muốn thử ngay mà ít thay đổi, giữ cấu trúc 36 Network và bổ sung bảo vệ bước vào phần trước khi chốt lỗi. Phần này dùng tên DB/tag đúng ảnh bạn gửi; là biểu thức logic để dựng LAD, không phải file import.

### 4.1. Thêm một Bool trong DB1

Thêm `loi_buoc : Bool`, start FALSE, không Retain. Chèn một rung **trước rung tạo loi_hientai của NW07**:

```text
"daiphunnuoc".loi_buoc :=
    ("daiphunnuoc".buoc_hientai < 0)
    OR ("daiphunnuoc".buoc_hientai > 5);
```

Trong LAD: hai khối so sánh Int `< 0` và `> 5` mắc hai nhánh song song, ra cuộn thường `loi_buoc`. Không coi bước 0 là lỗi.

### 4.2. Bổ sung vào lỗi hiện tại và ACK

```text
loi_hientai := NOT "du nuoc"
              OR NOT "dung khan ok"
              OR NOT "qua tai"
              OR loi_buoc;

ACK := xung_reset AND NOT "chon auto"
       AND an_toan AND NOT loi_buoc;
```

Các biến không có dấu ngoặc kép trong ví dụ ACK thuộc DB `"daiphunnuoc"`. I0.4 `"qua tai"` trong ví dụ phải mang nghĩa **quá tải bình thường = 1**. Dùng ACK này cho R1 của cả NW09 và NW10. Không dùng ACK làm lệnh chạy bơm.

Khi có lỗi bước, NW09 chốt lỗi, NW13–15 mất quyền chạy, NW17 đặt bước tiếp theo về 0, NW29 chốt 0 và các đầu ra tắt. Lỗi đã chốt được giữ để người vận hành biết; OFF → điều kiện bình thường → nhấn RESET mới → AUTO mới được chạy lại. Nếu có writer khác tiếp tục ghi sai bước, phải xử lý writer đó; không liên tục RESET để che lỗi.

### 4.3. RTC và khởi động: lựa chọn bổ sung

Bản gốc đã dừng khi RTC lỗi và không tự chạy lại khi RTC hồi phục; nó cần OFF → AUTO nhưng không bắt buộc RESET riêng cho RTC. Điều đó không trái yêu cầu đã cho. Nếu muốn mọi lỗi được xác nhận cùng một cách, thêm `("chon auto" AND NOT rtc_ok)` vào loi_hientai, thêm `rtc_ok` vào ACK và đơn giản NW36 thành `"den bao loi" := nho_loi`. **Bản 26 Network dùng chính sách chốt RTC này.**

Giữ trạng thái điều khiển, bước, bộ nhớ cạnh không Retain. Ảnh hiện đã bỏ Retain; đó là điểm đúng. OB100/khởi tạo vòng quét đầu trong bản 26 là phần củng cố startup, không phải bằng chứng bản gốc luôn tự khởi động sai.

Không cần đổi timer thành 9.99 s. PT=10 s là đúng ý đồ; sai số thực tế phải đo bằng trace và chu kỳ quét của CPU.

## 5. Bản tổ chức lại 26 Network để dễ bảo trì

Bộ hình trong `LAD_DE_XUAT` mô tả đầy đủ 26 Network chạy tuần hoàn và một hình OB100. Giữ năm TON độc lập, giữ CurrentStep/NextStep; gom timer và chuyển bước liên quan vào cùng một Network. Số Network giảm chủ yếu do cách nhóm rung, **không phải số đo CPU chạy nhanh hơn**.

| Nhóm gốc | Nhóm mới | Thay đổi chính |
|---|---|---|
| Startup bằng start value | OB100 + NW01, NW26 | Cờ InitPending/FirstScan; không nhận lệnh cạnh ở scan khởi tạo |
| 01–05 | 02–06 | RTC + lịch; thêm kiểm tra miền và chấp nhận mã thành công 1 |
| 06–07 | 07–08 | Safe; thêm BadStep và lỗi RTC khi AUTO |
| 08, 12 | 09 | Hai R_TRIG riêng cùng Network, gọi mỗi scan |
| Điều kiện reset tại 09–10 | 10 | Tạo ACK chung, đòi OFF + khỏe + RTC tốt + bước hợp lệ |
| 09–10 | 11–12 | Hai SR riêng: lỗi và STOP |
| 11, 13–15 | 13–15 | OffSeen, chốt AUTO, Run; thêm chặn startup |
| 16–18 | 16 | Ba rung theo thứ tự default, stop, start |
| 19–28 | 17–21 | Mỗi TON và chuyển bước đi cùng nhau; chỉ ghi NextStep |
| 29 | 22 | Commit CurrentStep một lần |
| 30–35 | 23–24 | Guard bước 1–5; năm rung lệnh bơm/van |
| 36 | 25 | Alarm = FaultLatched, RTC đã được chốt |

Khi chạy bản mới, dùng **một** chương trình điều khiển đầu ra. Không để cả bản 36 và bản 26 cùng được gọi và cùng ghi Q0.0–Q0.5. Có thể giữ bản cũ trong bản sao dự án để đối chiếu.

NW16 phải giữ thứ tự ba rung. NW17–21 gọi đủ năm TON trước NW22. Tại NW24, mỗi Q được ghi đúng một lần; chương trình dùng ảnh tiến trình Q thông thường, không ghi đầu ra ngoại vi trực tiếp. `OutputEnable` đúng ở các bước 1–5, mà mọi bước đó đều có ít nhất một lệnh mở van, nên bơm = OutputEnable vẫn liên tục và giữ đúng ma trận.

## 6. Bảng tag và biến cần khai báo

### 6.1. I/O: giữ đúng địa chỉ hiện có

| Alias trên hình mới | Tag trong ảnh TIA của bạn | Địa chỉ | Ý nghĩa |
|---|---|---|---|
| AutoSelected | chon auto | %I0.0 | 1=AUTO, 0=TẮT |
| WaterOK | du nuoc | %I0.1 | 1=đủ nước |
| ResetButton | nut reset | %I0.2 | 1=nhấn RESET, nút NO |
| EStopOK | dung khan ok | %I0.3 | 1=mạch dừng khẩn bình thường |
| OverloadOK | qua tai | %I0.4 | 1=quá tải bình thường; nên đổi tên/comment rõ *_OK |
| StopOK | stop | %I0.5 | 1=chưa nhấn STOP, tiếp điểm NC |
| Pump | bom nuoc | %Q0.0 | Lệnh bơm |
| Valve1 | van 1 | %Q0.1 | Lệnh van 1 |
| Valve2 | van 2 | %Q0.2 | Lệnh van 2 |
| Valve3 | van 3 | %Q0.3 | Lệnh van 3 |
| Valve4 | van 4 | %Q0.4 | Lệnh van 4 |
| Alarm | den bao loi | %Q0.5 | Đèn lỗi đã chốt |

Tên alias là ký hiệu đọc hình, không phải yêu cầu tạo thêm tag trùng địa chỉ. Trong TIA chọn tag bằng danh sách hoặc đổi tên nhất quán qua hệ thống tham chiếu. DB thật là `"daiphunnuoc"`, không phải tên minh họa `DBdaiphunnuoc`. Ví dụ đúng theo ảnh: `"daiphunnuoc"."gio plc".HOUR`, `"daiphunnuoc".buoc_hientai`.

### 6.2. DB hiện có và biến bổ sung

Các alias được ánh xạ đầy đủ trong bảng `BANG_TAG_VA_DB.csv` kèm bộ hình. Biến hiện có: PLC_LocalTime→`gio plc`, RTC_Status→`trangthai rtc`, RTC_OK→`rtc_ok`, Morning→`ca_sang`, Evening→`ca_toi`, InSchedule→`trong_gio`, Safe→`an_toan`, FaultNow→`loi_hientai`, FaultLatched→`nho_loi`, StopLatched→`nho_stop`, ResetEdge→`xung_reset`, AutoEdge→`xung_auto`, OffSeen→`da_gat_tat`, AutoArmed→`cho_phep_auto`, Run→`tu_dong_chay`, CurrentStep→`buoc_hientai`, NextStep→`buoc_tieptheo`.

| Alias mới | Trường mới trong DB1 | Kiểu / start | Chức năng |
|---|---|---|---|
| InitPending | khoi_tao_cho | Bool / TRUE | OB100 SET; NW26 RESET sau scan đầu |
| FirstScan | vong_quet_dau | Bool / FALSE | NW01 sao chép InitPending, giữ suốt scan |
| BadStep | loi_buoc | Bool / FALSE | Bước ngoài miền 0–5 |
| Ack | xac_nhan_loi | Bool / FALSE | Xác nhận phục hồi chung |
| OutputEnable | cho_phep_ngo_ra | Bool / FALSE | Run và bước 1–5 sau commit |

Các cờ và bước điều khiển không Retain. DTL là DTL, mã RTC là Int, CurrentStep/NextStep là Int, PT là Time. Không đổi bước sang UInt nếu vẫn dùng phép so sánh `<0` cho kiểm tra lỗi.

R_TRIG cần hai instance độc lập và TON cần năm instance độc lập. Dựng ở OB1 có thể dùng các instance DB riêng do TIA tạo; dựng trong FB thì dùng Static multi-instance. Không khai báo timer/trigger là TEMP mất trạng thái. Tại các hình, `ResetTrigger.Q`/`Timer1.Q` là đầu ra của instance tương ứng; chọn instance thật bằng TIA.

### 6.3. Phần có thể bỏ sau khi kiểm tra Cross-reference

Hai tag `%M0.0 nhocanh auto`, `%M0.1 nhocanh reset` có thể không cần nếu dùng R_TRIG với instance riêng. Nếu dùng tiếp điểm P/khối bắt cạnh cần bit nhớ thì phải giữ chúng. Ảnh chỉ hiện 14 trong 43 tag, nên chưa đủ bằng chứng để xóa ngay.

Năm cờ `xong_buoc1…5` có thể bỏ nếu đọc trực tiếp Q của TON và không có HMI hay network khác sử dụng. `co_van_mo` có thể bỏ trong bản 26 vì đã có guard bước và ma trận xác định. Bộ hình giữ `huy_phep_chay` làm CancelAuto để nhánh thu hồi quyền dễ đọc. Kiểm tra Cross-reference trước khi xóa từng tag, và giữ nếu cần hiển thị/chẩn đoán.

HMI chỉ đọc các biến bước, chốt, quyền chạy và các Q trạng thái; không dùng chúng làm tag lệnh ghi. Việc ảnh hiện “Writable” được chọn chưa chứng minh HMI đã ghi sai, nhưng cần giới hạn quyền ghi đối với biến trạng thái.

## 7. Trình tự dựng và thử trong TIA Portal V16

1. Lưu một bản sao dự án để chạy thử. Chọn sửa tối thiểu theo mục 4 hoặc dựng bản 26 theo bộ hình, không gọi song song cả hai bản điều khiển Q.
2. Đối chiếu đúng CPU1214C AC/DC/Relay đang dùng; giữ địa chỉ I/O, sửa comment cho healthy=1. Khi mô phỏng, đặt I0.1, I0.3, I0.4, I0.5 = TRUE trước thử chạy; để mặc định tất cả bằng 0 sẽ báo lỗi/dừng là đúng.
3. Dùng bảng ánh xạ DB/tag để dựng. Tạo hai instance R_TRIG và năm instance TON riêng. Để block được thực hiện ở mọi scan; điều kiện vào chân CLK/IN, không bỏ qua việc gọi block khi tín hiệu FALSE.
4. Nếu dùng bản 26, tạo startup OB100 đặt `khoi_tao_cho` TRUE; NW01 đọc sang `vong_quet_dau`, NW26 xóa `khoi_tao_cho`. Các trạng thái không Retain; current/next khởi tạo 0.
5. Thiết lập múi giờ CPU UTC+07:00, DST tắt. Dùng RD_LOC_T, không lẫn giờ hệ thống UTC của RD_SYS_T. Xác nhận đồng hồ ngày/giờ thực tế; RTC_OK chỉ nói việc đọc hợp lệ, không đảm bảo người dùng đã đặt đồng hồ đúng.
6. Compile software toàn bộ, đọc mọi error/warning có liên quan. Dùng Cross-reference kiểm tra mỗi đầu ra chỉ có một nơi ghi và không còn force trước khi thử tình huống khác.
7. Tạo Watch table: I0.0–I0.5, RTC_Status/DTL, RTC_OK, InSchedule, FaultNow, FaultLatched, StopLatched, AutoArmed, Run, CurrentStep/NextStep, BadStep, FirstScan, Timer1…5.Q/ET, Q0.0–Q0.5.
8. Chạy các ca bên dưới, ghi pass/fail thực tế. Chỉ chuyển sang tải thật sau khi phần logic và điều kiện bảo vệ phần cứng được kiểm tra.

| Ca thử trong TIA/PLCSIM | Thao tác | Kết quả phải thấy ở bản 26 |
|---|---|---|
| Cấp nguồn khi AUTO | Healthy=1, trong giờ, I0.0=1 từ trước startup | Q bơm/van OFF; phải OFF rồi AUTO để có quyền |
| Chu kỳ sạch | OFF, healthy, AUTO trong giờ | Bước 1–5, mask 1/3/7/15/10, lặp về 1; bơm không ngắt giữa bước |
| Đủ 10 s | Theo dõi ET và Q mỗi bước | Không chuyển trước PT; đo độ trễ theo scan, không yêu cầu 10.000 s tuyệt đối |
| Biên sáng | 05:59:59, 06:00:00, 07:59:59, 08:00:00 | OFF, ON, ON, OFF nếu đã có quyền AUTO |
| Biên chiều | 16:59:59, 17:00:00, 20:29:59, 20:30:00 | OFF, ON, ON, OFF |
| Ca sau tự chạy | Giữ AUTO qua 08:00 rồi đến 17:00, không lỗi/STOP | Dừng giữa ca, tự bắt đầu lại bước 1 lúc 17:00 |
| STOP tại từng bước | I0.5=0 rồi trả 1 | Q0.0–4 OFF; StopLatched giữ TRUE; không tự chạy lại |
| Thiếu nước / quá tải / E-stop | Lần lượt I0.1/I0.4/I0.3=0 tại mỗi bước | Dừng, chốt lỗi, Q0.5 ON; nhả lỗi không tự chạy |
| RESET khi AUTO | Nhấn RESET khi I0.0=1 | Không xóa chốt, không khởi động |
| Giữ RESET sẵn | Giữ nút trước khi phục hồi healthy | Không ACK tự động; phải thả rồi nhấn lại lúc OFF |
| Phục hồi bình thường | OFF, đầu vào tốt, RTC tốt, nhấn RESET mới rồi AUTO | Xóa chốt, bắt đầu lại bước 1 |
| RTC lỗi | Mô phỏng trạng thái đọc lỗi trong bản test, không sửa đầu ra tải thật | Thu hồi quyền và chốt lỗi khi AUTO; phục hồi cần OFF–RESET–AUTO |
| Bước sai | Ghi -1, 6 hoặc 100 vào bước khi đang chạy trong bản test | Dừng/chốt lỗi cùng scan tính logic, bước về 0; không Run=TRUE kéo dài |
| Không nhảy dồn | Theo dõi tại thời điểm hết timer | Mỗi scan nhiều nhất một chuyển bước hợp lệ |
| Bắt cạnh lần hai | Nhấn–nhả–nhấn RESET; OFF–AUTO nhiều lần | Có xung ở mỗi cạnh lên mới, không chỉ lần đầu |

Với RTC lỗi hoặc dữ liệu bước, dùng bản test/PLCSIM hoặc đầu vào thử có kiểm soát; RD_LOC_T và chương trình có thể ghi đè giá trị bạn vừa Modify trong Watch table. Không kết luận ca đã thử nếu giá trị giả lập chưa tới được network cần kiểm tra. Xóa mọi force và nhánh thử khi kết thúc.

## 8. Cách hiểu kết quả kiểm thử kèm theo

Thư mục KIEM_THU có mô hình quét Python cho logic gốc và logic đề xuất, ca thử tự động, kết quả và dấu vết chu kỳ. Mô hình dùng thời gian quét định sẵn và timer mô phỏng, không chạy mã máy Siemens. Nó giúp kiểm chứng lịch, ma trận, các chốt, điều kiện chuyển bước và tái hiện lỗi bước 6; không thay thế Compile, PLCSIM hay nghiệm thu phần cứng.

Với mô hình quét 10 ms, timer bước mới chỉ nhận IN=TRUE ở scan sau khi CurrentStep được commit và đầu ra đã đổi. Vì vậy mỗi pha có thể dài khoảng 10.010 s trong mô hình; ngoài thực tế còn phụ thuộc chu kỳ quét/IO. Giữ PT=T#10s, không tự bù bằng một giá trị đoán trước.

Bộ bàn giao tập trung vào LAD: hình, bảng tag, mô tả từng rung và các ca thử. Không có file dự án TIA native hay nguồn SCL đã biên dịch trong gói này.

## 9. Khuyến nghị tối ưu và phạm vi còn lại

Nên giữ năm TON và cơ chế current/next ở giai đoạn chạy thử. Nếu phát triển tiếp, đưa logic vào một FB với multi-instance timer/trigger để quản lý gọn; giữ các biến trạng thái chỉ đọc từ HMI, chuẩn hóa tên tag và bổ sung mã nguyên nhân lỗi cho chẩn đoán. Chỉ bỏ cờ trung gian sau khi đã kiểm tra nơi sử dụng.

Một timer 50 s chia cửa sổ không tự động tốt hơn: phải giải quyết ranh giới cuối chu kỳ, reset khi dừng, khởi động lại và độ chính xác pha. Không đổi sang cách đó chỉ để có ít network hơn.

`Pump`, `Valve1…4` và `co_van_mo` là lệnh phần mềm. Chúng không xác nhận động cơ đang quay hoặc van thực đã mở. CPU1214C tiêu chuẩn và LAD này không thay thế mạch dừng khẩn, contactor/bảo vệ quá tải và liên động phần cứng khi nối tải thật. Đây là giới hạn chức năng cần mô tả đúng, không phải yêu cầu thêm một biến giả để chứng minh cơ cấu đã hoạt động.

Tài liệu tham khảo chính: phiếu yêu cầu công nghệ và 36 hình bạn cung cấp; bảng tag/DB trong ảnh TIA; tài liệu S7-1200 có trong kho về TON, RD_LOC_T và DTL. Khi dựng dự án, dùng trợ giúp F1 đúng phiên bản TIA V16 cho RD_LOC_T, TON, R_TRIG và SR/RS để đối chiếu chân khối, kiểu dữ liệu và mã trả. Không có kết quả tra catalogue/biên dịch trực tuyến nào được dùng làm bằng chứng chạy thật.
