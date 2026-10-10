# Nạp nguồn SCL cho mô hình đài phun 4 van

Tệp `Fountain_Auto_4Van.scl` là mã nguồn thiết kế để nhập vào STEP 7 (TIA Portal) cho S7-1200. Môi trường rà soát hiện tại không có TIA Portal, PLCSIM hoặc PLC thật: **chưa có kết quả biên dịch, mô phỏng Siemens hoặc chạy phần cứng**. Bộ 31 kiểm tra Python chỉ kiểm tra mô hình hành vi độc lập của thuật toán.

## 1. Phạm vi và yêu cầu công nghệ

- Chỉ hai vị trí AUTO/TẮT; không có Manual ẩn dưới vị trí TẮT.
- Lịch hằng ngày: `06:00:00 <= t < 08:00:00` và `17:00:00 <= t < 20:30:00`.
- Bơm duy trì lệnh ON trong toàn bộ chu trình chạy. Các mask van YV1..YV4 là `1, 3, 7, 15, 10`, tương đương `1000, 1100, 1110, 1111, 0101` khi viết theo thứ tự **YV1, YV2, YV3, YV4**.
- Mỗi bước có `PT := T#10s`. Năm timer đều được gọi một lần mỗi vòng quét; timer của bước không hoạt động được reset. Khi đổi bước không có trạng thái trung gian tắt bơm.
- Mất lịch, STOP, quá tải hoặc thiếu nước đưa mọi lệnh về OFF trong lượt xử lý PLC phát hiện. Đầu ra vật lý còn có thời gian cập nhật ảnh tiến trình, thời gian rơle/contactor và thời gian cơ khí; không đồng nhất với cắt tức thời tuyệt đối.
- Giám sát E-STOP, lỗi đọc RTC và chốt lỗi là bổ sung của thiết kế.

Một bước thực tế chịu lượng tử hóa chu kỳ quét: timer của bước mới bắt đầu được gọi ở vòng quét sau chuyển bước. Trong mô hình quét có chu kỳ tối đa `Tscan`, thời gian giữa hai lần đổi mask thuộc khoảng xấp xỉ `10 s` đến `10 s + 2*Tscan`; độ trễ phần cứng chưa nằm trong mô hình. Không ghi kết quả thực nghiệm "đúng 50,000 s" khi chưa đo Trace/Watch Table.

## 2. Địa chỉ vật lý bắt buộc

| Địa chỉ | Tên quy ước | Ý nghĩa mức 1 |
|---|---|---|
| %I0.0 | DI_AutoTat | Chọn AUTO |
| %I0.1 | DI_DuNuoc | Đủ nước |
| %I0.2 | DI_Reset | Nút RESET đang nhấn |
| %I0.3 | DI_DungKhanOK | Chuỗi E-STOP bình thường |
| %I0.4 | DI_QuaTaiOK | Rơle quá tải bình thường |
| %I0.5 | DI_StopOK | Nút STOP thường đóng chưa tác động |
| %Q0.0 | DO_Bom | Lệnh điều khiển rơle/contactor bơm |
| %Q0.1..%Q0.4 | DO_Van1..DO_Van4 | Lệnh cấp điện van thường đóng |
| %Q0.5 | DO_BaoLoi | Có chốt lỗi E-STOP/mức/quá tải/RTC |

Hai ngõ vào quá tải và STOP đã được bổ sung vào các vị trí trước đây ghi dự phòng. Không nối tắt chúng bằng hằng TRUE khi nghiệm thu. SCL dùng địa chỉ tuyệt đối trên đây, không phụ thuộc nhập PLC Tag Table; có thể đặt các tên quy ước tương ứng trong TIA để đọc Watch Table dễ hơn. Nếu địa chỉ đầu vào/đầu ra thực tế khác, phải sửa đồng bộ mã, bảng tag và bản vẽ.

Không có cảm biến xác nhận van mở, tiếp điểm phản hồi bơm hoặc đo áp suất trong cấu hình này. HMI phải ghi **lệnh bơm/lệnh van**, không ghi "bơm đang chạy thực tế" từ chính bit điều khiển. E-STOP và bảo vệ động cơ cần mạch cắt phần cứng được thiết kế, thử riêng; CPU tiêu chuẩn và chương trình này không phải bộ điều khiển an toàn được chứng nhận.

## 3. Quy tắc khởi động và RESET đã chọn

Đây là chính sách thiết kế bổ sung vì phiếu giao chỉ quy định các điều kiện dừng:

1. Sau cấp nguồn hoặc CPU STOP→RUN, nếu AUTO đang giữ thì đầu ra vẫn OFF. Đưa về TẮT rồi chọn lại AUTO để cho phép vận hành.
2. Khi đã được cho phép, hệ tự chạy trong lịch; hết giờ thì dừng. Đến khung giờ tiếp theo, hệ tự bắt đầu bước 1 nếu chưa có Stop/lỗi. Không cần Reset chỉ vì hết lịch.
3. Sau STOP hoặc lỗi: đưa công tắc về TẮT, xử lý nguyên nhân/nhả STOP hoặc khôi phục bảo vệ, bấm RESET mới, rồi chọn AUTO. Khi đang AUTO, RESET không xóa chốt và không khởi động.
4. RESET bắt cạnh lên; giữ nút từ trước khi hết lỗi không tự xóa lỗi. Nhả rồi nhấn lại sau khi đủ điều kiện.
5. AUTO/TẮT tắt hệ ngay; chọn lại AUTO khi không có chốt lỗi/STOP được phép bắt đầu bước 1.

`AlarmWord` giữ đồng thời nhiều nguyên nhân: bit 0 E-STOP, bit 1 thiếu nước, bit 2 quá tải, bit 3 RTC, bit 4 STOP. `FaultCode` chỉ là mã tổng hợp ưu tiên 1→2→3→4. STOP có bit riêng và không làm bật đèn lỗi Q0.5 trong phương án này.

## 4. Trình tự tạo project TIA

1. Tạo project và chọn đúng CPU, firmware, loại nguồn/I/O đang dùng. Báo cáo tham chiếu CPU 1214C AC/DC/Relay; không suy ra thiết bị thật chỉ từ ảnh minh họa.
2. Vào `External source files` → `Add new external file`, chọn `.scl` rồi `Generate blocks from source`. Dùng project mới hoặc sao lưu trước; nguồn có OB1 và OB100. Không ghi đè OB đang dùng của hệ thống khác.
3. Xác nhận OB1 là `Program cycle`, OB100 là `Startup`. Nếu phiên bản TIA không cho tạo số OB bằng nguồn ngoài, tạo hai OB này bằng giao diện rồi sao chép phần thân giữa BEGIN/END tương ứng. Không tạo một FC tên OB100 để thay startup OB.
4. Nguồn tạo `FC_ReadLocalClock`, `FB_Fountain`, `DB_Fountain` (instance), `DB_Runtime`, `DB_HMI`, OB1 và OB100. Các DB điều khiển và dữ liệu timer phải **non-retentive**. OB100 đặt `InitPending := TRUE`; OB1 truyền cờ này vào FB đúng lượt quét đầu rồi xóa.
5. Kiểm tra các instance timer `TON_TIME` và lời gọi `.TON`. Nếu thư viện/phiên bản STEP 7 yêu cầu metadata khác, chèn một TON IEC từ Instructions trong FB để TIA tự khai báo đúng kiểu, rồi ghép tham số IN/PT/Q/ET theo nguồn. Không thay bằng timer khác nghĩa hoặc bỏ gọi timer lúc dừng.
6. Cài thời gian hệ thống, múi giờ `UTC+07:00` cho Việt Nam; không dùng DST. `RD_LOC_T` trả `0` khi đọc thành công giờ chuẩn và `1` khi thành công giờ mùa hè; cả hai là hợp lệ. Trạng thái thành công của lệnh không chứng minh RTC đã được đặt đúng ngày/giờ, nên cần đối chiếu đồng hồ CPU trước nghiệm thu.
7. Biên dịch cả phần cứng và phần mềm; xử lý mọi lỗi/cảnh báo liên quan. Kết quả biên dịch phải ghi từ máy TIA thực tế, không lấy kết quả Python thay thế.
8. Với PLCSIM/đèn tải giả, kiểm tra toàn bộ kịch bản trong bảng nghiệm thu trước khi cấp nguồn động lực. CPU RUN, simulation support và driver truyền thông phải đúng phiên bản thực tế.

## 5. DB cho HMI Weintek

`DB_HMI` có `S7_Optimized_Access := 'FALSE'`. Nếu dùng driver Siemens S7-1200/1500 kiểu địa chỉ tuyệt đối, đặt số DB thành **200** hoặc sửa địa chỉ trong HMI theo số DB thực tế. Các trường đều dài 16 bit; `AlarmBits` là WORD, còn lại là INT. Dữ liệu là ảnh chỉ đọc từ PLC; HMI không ghi điều khiển trực tiếp vào DB này. Mất liên lạc HMI không tự thay đổi lịch chạy PLC; cần hiển thị cảnh báo chất lượng truyền thông trên HMI.

| Byte offset trong DB200 | Trường | Kiểu |
|---:|---|---|
| 0 | AutoSelect | INT |
| 2 | WaterOK | INT |
| 4 | EStopOK | INT |
| 6 | OverloadOK | INT |
| 8 | StopOK | INT |
| 10 | RTCValid | INT |
| 12 | RTCStatus | INT |
| 14 | Hour | INT |
| 16 | Minute | INT |
| 18 | InSchedule | INT |
| 20 | AutoArmed | INT |
| 22 | Running | INT |
| 24 | StepNo | INT |
| 26 | StepElapsed_ds | INT |
| 28 | PumpCmd | INT |
| 30 | Valve1Cmd | INT |
| 32 | Valve2Cmd | INT |
| 34 | Valve3Cmd | INT |
| 36 | Valve4Cmd | INT |
| 38 | Fault | INT |
| 40 | FaultCode | INT |
| 42 | AlarmBits | WORD |
| 44 | StopLatched | INT |
| 46 | ResetAllowed | INT |

Địa chỉ ví dụ phía PLC: `DB200.DBW24` là bước 0..5; `DB200.DBW26` là số phần mười giây đã trôi qua, hiển thị chia 10. Trước nối HMI cần đọc offset do TIA biên dịch, kiểm tra cách driver Weintek biểu diễn DB/offset và chọn kiểu 16-bit thích hợp. Không giả định cú pháp trường địa chỉ của EasyBuilder Pro giống chuỗi địa chỉ STEP 7. Chỉ bật quyền truy cập/truyền thông mà đúng driver và thiết kế mạng yêu cầu; không tự bật PUT/GET cho mọi trường hợp.

## 6. Kiểm chứng đã có và phần còn phải làm

Đã thực hiện: 31 ca unittest Python cho mô hình hành vi; toàn bộ 1.440 phút trong ngày; các biên lịch; hai chu kỳ đủ 5 mask; bơm liên tục; ngắt tại mọi bước cho cả bốn bảo vệ; RESET giữ; khởi động lại; RTC lỗi; nhiều lỗi đồng thời; chu kỳ quét không đều.

Chưa thực hiện: biên dịch TIA, chạy S7-PLCSIM, nạp CPU thật, xác nhận đấu dây, đo bước 10 s, thử E-STOP cắt cứng, đo dòng/áp, thử van/bơm thật, truyền thông HMI thật. Những mục này phải được ghi "chưa thực hiện" trong báo cáo nghiệm thu cho đến khi có dữ liệu.
