# Đánh giá và chỉnh sửa đồ án đài phun nước 4 van

Ngày rà soát: **10/10/2026**. Phạm vi: đối chiếu hai tài liệu được cung cấp, sửa thiết kế và mã nguồn, kiểm tra tính nhất quán giữa phần chữ, I/O, hình và chương trình. Thông tin cá nhân đã được loại khỏi bộ hồ sơ công khai.

## Kết luận đánh giá

Bản gốc đã mô tả đúng hai khung giờ và ma trận năm bước. Tuy nhiên, chưa đủ cơ sở kết luận đáp ứng toàn bộ phiếu giao: thiếu ánh xạ STOP/quá tải bắt buộc, mâu thuẫn AUTO/TẮT với MANUAL, RESET có thể khởi động lại trái mô tả, thiếu phần tích hợp RTC/OB, ảnh demo khác yêu cầu và chưa có bằng chứng biên dịch TIA hay thực nghiệm.

Bộ chỉnh sửa xử lý các mâu thuẫn trên ở mức hồ sơ thiết kế và nguồn chương trình, bổ sung bảy hình nguyên lý, bảng đối chiếu, phép tính có giả thiết và kiểm tra hành vi độc lập. Các mục mô phỏng Siemens, thiết kế HMI triển khai và thực nghiệm vẫn cần thực hiện bằng công cụ/thiết bị thực tế. Không quy đổi đánh giá này thành điểm số hoặc chứng nhận nghiệm thu.

## Đối chiếu phiếu giao đề tài

| Yêu cầu trong phiếu | Nhận xét bản gốc | Nội dung đã chỉnh sửa / bổ sung | Trạng thái và bằng chứng |
|---|---|---|---|
| AUTO đọc đồng hồ thời gian thực | Mô tả có RTC, phụ lục chưa tích hợp đầy đủ lệnh đọc | Có FC đọc `RD_LOC_T`, xử lý trạng thái trả về và OB1 gọi khối | Đã có nguồn thiết kế; cần biên dịch TIA và đối chiếu đồng hồ CPU |
| 06:00–08:00; 17:00–20:30 | Phần chữ đúng; demo HMI ghi lịch khác | Đồng nhất hai cửa sổ nửa mở; HMI thiết kế mới dùng đúng lịch | Mô hình kiểm tra đủ 1.440 phút/ngày và các biên có giây |
| Bơm chạy liên tục khi vận hành | Ý tưởng đúng nhưng có nhánh chạy tay dưới vị trí TẮT | Bỏ MANUAL khỏi cấu hình cơ sở; không ngắt lệnh bơm khi đổi bước | Đã kiểm tra hành vi chu trình; chưa đo đầu ra thực |
| Năm bước, 10 s/bước | Ma trận đúng; ảnh demo ghi 8 bước | Giữ ma trận đúng; timer `PT=T#10s`; hình chu trình 5 bước | Đã kiểm tra mô hình hai chu kỳ và quét không đều; chưa có Trace PLC |
| Dừng khi hết giờ | Đã có so sánh phút | Khóa lệnh chạy ngoài lịch; lần sau bắt đầu bước 1 | Kiểm tra mô hình tại mọi bước |
| Dừng khi nhấn nút STOP | Bảng I/O bỏ sót hoặc trùng địa chỉ mức nước | STOP NC riêng tại I0.5; có chốt dừng và quy tắc xác nhận | Đã thể hiện trong mã/bảng/sơ đồ; cần thử mạch thật |
| Dừng khi bơm quá tải | Có nơi ghi là tùy chọn, thiếu I/O | I0.4 nhận trạng thái OL bình thường; OL tham gia cắt cuộn KM trong sơ đồ nguyên lý | Đã có phương án; cần xác nhận tiếp điểm thực, chỉnh OL và thử ngắt |
| Dừng khi nước thấp | Có trong thiết kế | I0.1=đủ nước; mất tín hiệu khóa chạy và giữ lỗi | Đã kiểm tra mô hình; cần thử cảm biến thật |
| Các phương pháp điều khiển, chọn giải pháp | Có nội dung nhưng bố cục 5 chương | Sắp theo đề cương 3 chương; tách yêu cầu gốc và chính sách bổ sung | Hoàn thiện phần thuyết minh thiết kế |
| Mạch động lực, điều khiển, sơ đồ đấu dây | Hình khối thiếu/không thống nhất, EL-03 bị thiếu | Bổ sung EL-01 đến EL-04; dùng chung bảng 6DI/6DO | Sơ đồ nguyên lý; chưa là bộ bản vẽ thi công |
| Bản vẽ khổ A0 | Hình chèn A4 không thay bản vẽ A0 | Xuất 7 tờ A0 nằm ngang, 1.189 × 841 mm | Phiếu không ấn định số tờ; cần giáo viên duyệt phạm vi bản vẽ khi chốt mô hình |
| Lập trình PLC và giao diện | Mã/phần hướng dẫn chưa tạo project chạy; demo HMI sai | SCL và hướng dẫn nhập; DB_HMI chỉ đọc, bảng offset; mockup đúng đề | Chưa có tệp project TIA/EBPro, chưa thử truyền thông |
| Kết quả mô phỏng và thực nghiệm | Chủ yếu là giá trị dự kiến/kế hoạch | Ghi rõ kiểm tra Python đã thực hiện; lập danh mục thử Siemens và thử thật | 31/31 ca mô hình đạt; TIA/PLCSIM/thực nghiệm chưa thực hiện |

## Các sửa lỗi quan trọng

| Nhóm | Lỗi/mâu thuẫn cần sửa | Phương án thống nhất |
|---|---|---|
| I/O | STOP từng bị gán I0.1; E-STOP có chỗ I0.5; OL/STOP có chỗ là dự phòng | I0.0 AUTO; I0.1 đủ nước; I0.2 RESET; I0.3 KSR/E-STOP OK; I0.4 OL OK; I0.5 STOP OK. Q0.0 bơm; Q0.1–Q0.4 van; Q0.5 báo lỗi |
| Chế độ | `NOT AutoMode` được xem như MANUAL, dù công tắc ghi AUTO/TẮT | TẮT luôn tắt bơm/van; không có nhánh Manual trong cấu hình cơ sở |
| RESET/khởi động | Có đoạn nói RESET không khởi động nhưng mã có thể cho chạy ngay | RESET chỉ bắt cạnh mới, chấp nhận ở TẮT khi hết nguyên nhân; sau STOP/lỗi cần TẮT → RESET → AUTO. Sau cấp nguồn cần thấy TẮT rồi cạnh chọn AUTO |
| Lịch bình thường | Dễ lẫn hết lịch với lỗi hoặc yêu cầu xác nhận lại | Hết lịch dừng chờ, không sinh lỗi; khung sau tự chạy bước 1 nếu vẫn được cho phép AUTO |
| Chốt lỗi | Một mã ưu tiên có thể che việc nhiều nguyên nhân cùng xảy ra | `AlarmWord` giữ từng bit; `FaultCode` chỉ phục vụ hiển thị ưu tiên; STOP riêng, không coi vị trí TẮT là lỗi |
| Timer | Diễn đạt 10 s và 50 s như số đo tuyệt đối; reset TON chưa nhất quán | Năm timer gọi mỗi scan, PT=10 s; công khai sai số theo chu kỳ quét và yêu cầu đo Trace |
| HMI | Demo 5/8 bước, 18:00–21:00; lệnh dễ bị coi như phản hồi cơ cấu | Hình thiết kế mới 5 bước, đúng hai khung giờ; giám sát chỉ đọc và dùng nhãn “lệnh” |
| E-STOP | Nút ví dụ 1NO+1NC không đáp ứng hai kênh NC đã mô tả | Tiêu chí E-STOP hai NC phù hợp KSR; I0.3 chỉ là phản hồi phụ; cắt cứng độc lập với CPU tiêu chuẩn |
| Tiếp điểm bảo vệ | Trộn tiếp điểm cắt cứng với phản hồi PLC; có thể nhầm NO trip với NC bình thường | Tách nhánh cắt KM và phản hồi; chọn tiếp điểm/relay quy đổi tín hiệu `OK=1` đúng loại thiết bị |
| Thủy lực | Tính ở một điểm nhưng dễ bị diễn giải thành xác nhận toàn bộ đường đặc tính | Ghi rõ Q=1,2 m³/h, H tính≈17,96 m; chọn sơ bộ 20 m; phải kiểm tra Q–H từng trạng thái, Qmin và tổn thất nhánh |
| Công suất bơm | 58,7 W ở H≈17,96 m dễ bị gán cho điểm 20 m hoặc công suất nhãn | 58,7 W là thủy lực tại H tính; 65,4 W tại 20 m. Ước lượng điện theo hiệu suất giả thiết không phải thông số nhãn |
| Bypass/RV1 | Mặc nhiên coi van xả áp là bảo đảm lưu lượng tối thiểu | Tách chức năng xả áp và tuần hoàn tối thiểu; chưa xác nhận đạt khi chưa có đường cong/cài đặt/khả năng xả |
| Nguồn 24 VDC | Hai ngân sách khác nhau, thiếu KM1 và số đèn; ảnh nguồn 10 A nhưng chọn 5 A | Giữ một ngân sách có điều kiện: HMI 0,5 A và 4 coil 10 W/24 V là 2,1667 A; với dự phòng 25%, nguồn 5 A còn 1,8333 A cho toàn bộ tải phụ, chưa kể kiểm tra hút/derating |
| BOM | Thiếu STOP, OL, KM, KA, KSR và phụ kiện dù dùng trong thuyết minh | Bổ sung nhóm thiết bị và tiêu chí chọn; mục chưa chốt model ghi dự kiến, không gán số liệu catalogue giả |
| Định dạng | Mục lục thủ công, thiếu hình, phông/code không đều, trang trắng | Dựng lại bố cục, đánh số/caption, chữ Unicode và phần code dễ đọc; kiểm tra Word/PDF sau kết xuất |
| Nguồn tham khảo | Link Certificate dùng như manual, sai “YV4.7”, trùng tài liệu; có tài liệu không được gửi trong lượt này | Sửa tên/phiên bản, gộp trùng; không nói đã đọc nguồn chưa có hoặc catalogue bị chặn |

Quy tắc E-STOP, chốt lỗi và chống tự chạy lại là **lựa chọn thiết kế bổ sung**, không trình bày như câu chữ nguyên văn của phiếu giao. Bản nguồn cũng không thay hệ thống an toàn phần cứng đã được thiết kế và kiểm chứng.

## Bằng chứng kiểm tra hiện có

Mô hình hành vi Python độc lập chạy **31/31 ca đạt**, bao gồm:

- Toàn bộ 1.440 phút trong ngày, biên lịch có giây và giá trị đồng hồ không hợp lệ.
- Đúng thứ tự năm mask van, hai chu kỳ, không đổi bước trước ngưỡng đặt, bơm liên tục, chu kỳ quét không đều.
- TẮT luôn tắt các đầu ra; AUTO giữ lúc cấp nguồn không tự chạy.
- STOP, E-STOP, quá tải, thiếu nước tại mỗi bước; nhả nguyên nhân không tự khởi động.
- RESET khi AUTO, RESET giữ mức, RESET lúc nguyên nhân còn tồn tại, nhiều lỗi đồng thời và mất RTC.
- Hết lịch ở từng bước, chờ lịch kế tiếp, khởi động lại từ bước 1 và xóa trạng thái timer khi khởi động.

Các kết quả trên kiểm tra **mô hình thuật toán**, không chứng minh mã SCL đã được compiler Siemens chấp nhận hoặc thời gian/cơ cấu ngoài thực tế đạt yêu cầu. Độ trễ ảnh tiến trình, rơle, contactor, van và thủy lực chưa nằm trong các phép kiểm tra này.

## Phần còn thiếu để nghiệm thu đầy đủ

| Công việc | Bằng chứng cần bổ sung |
|---|---|
| Chốt CPU/firmware, loại bơm, mã van và toàn bộ BOM | Datasheet đúng mã; đường Q–H/NPSH/Qmin; coil/công suất; ren, Kv và áp chênh làm việc; thông số KM/OL/KSR |
| Hoàn thiện bản vẽ thi công | Sơ đồ đúng số pha, định mức bảo vệ, dây/PE, terminal, số tiếp điểm thực, chống xung, nhánh cầu chì, cắt nguồn van và phản hồi |
| TIA Portal | Project gốc, biên dịch HW/SW không lỗi, cấu hình non-retentive, OB100, RTC UTC+7, timer và bảng I/O |
| PLCSIM và đo chu trình | Watch/Trace tại biên 06:00, 08:00, 17:00, 20:30; 5 bước; thời gian đổi bước; mỗi điều kiện dừng tại mọi bước; RESET và khởi động lại |
| HMI | Project EasyBuilder Pro, driver/DB thật, xác nhận offset và kiểu dữ liệu, cảnh báo mất truyền thông; màn hình hiển thị đúng lệnh và trạng thái |
| Thử mạch và bảo vệ | Kết quả STOP/OL/KSR cắt cứng, mức nước, đứt tín hiệu, bật lại nguồn; log ngày thử, người thực hiện và điều kiện thử |
| Thử thủy lực/điện | Lưu lượng/áp tại từng cấu hình van, dòng bơm, dòng 24 VDC và hút ban đầu, nhiệt, bypass/xả áp, trạng thái mất điện |
| Chương thực nghiệm | Ảnh thật, bảng số đo và nhận xét từ các phép thử trên; không dùng mockup thay ảnh chạy thật |

## Nguồn ngoài và mức xác nhận

Hai tệp người dùng cung cấp là căn cứ đối chiếu trực tiếp. Các URL Siemens, Weintek, Bürkert, Grundfos, Schneider và Mean Well đã được thử truy cập nhưng proxy của môi trường trả lỗi 403 trước khi nhận tài liệu. Vì vậy, thông số catalogue chỉ được giữ ở mức tham chiếu/dự kiến, có yêu cầu kiểm tra đúng mã trước khi chốt thiết bị. Không có kết luận “đã xác thực catalogue” trong bộ chỉnh sửa.

Đã đọc thêm tài liệu học tập `Tai lieu huong dan S7-1200_07_2021.pdf` có sẵn trong kho GitHub (59 trang, đầu trang ghi Thainguyen Automation): trang PDF 1–2 về PLC/HMI, trang 7 về cấu hình CPU, trang 11 và 27 về TON, trang 16–17 về RD_LOC_T/DTL và so sánh giờ/phút. Đây là tài liệu tham khảo thực sự đã đối chiếu; không thay catalogue chính hãng, không xác nhận cú pháp SCL hoặc mã trả về RTC cho mọi phiên bản.

Danh mục nguồn chính thức và hướng kiểm tra nằm trong thuyết minh. Lỗi truy cập trong môi trường không chứng minh tài liệu của hãng đã bị xóa. Tài liệu mẫu về robot phân loại sản phẩm trong kho không được dùng làm căn cứ cho công nghệ đài phun nước.
