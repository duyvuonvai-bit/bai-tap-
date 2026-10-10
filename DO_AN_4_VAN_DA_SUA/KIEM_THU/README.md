# Kiểm tra mô hình hành vi độc lập

Thư mục này cung cấp bằng chứng kiểm tra có thể chạy lại. Đây là **mô hình Python mô tả thuật toán**, không phải chương trình thông dịch SCL, bộ biên dịch TIA Portal, S7-PLCSIM hay mô hình thiết bị vật lý. Kết quả đạt không chứng minh mã đã được Siemens biên dịch hoặc PLC thật đã vận hành đúng.

## Chạy lại

Cần Python 3.10 trở lên; chỉ sử dụng thư viện chuẩn, không cài gói bên ngoài. Mở Terminal/PowerShell tại thư mục này và chạy:

```text
python run_checks.py
```

Trên Windows có thể dùng `py run_checks.py` nếu lệnh `python` chưa được đặt trong PATH. Để xem trực tiếp từng phép kiểm tra:

```text
python -m unittest -v test_plc_behavior.py
```

Để dựng lại hai đồ thị minh họa từ CSV, cần cài `matplotlib` rồi chạy `python plot_traces.py`. Thư viện này chỉ dùng để vẽ; 31 ca kiểm tra và việc tạo CSV không cần thư viện bên ngoài. Hai đồ thị SIM01/SIM02 thể hiện dữ liệu mô hình Python, không phải ảnh Trace của TIA.

## Các tệp kết quả

- `TEST_RESULTS.txt`: kết quả 31 ca unittest thực chạy trên mô hình.
- `TRACE_CHUYEN_BUOC.csv`: các thời điểm đổi bước từ lượt mô hình dùng chu kỳ quét 10 ms; đồng hồ lịch giữ ở 06:00, AUTO được chọn sau lượt khởi tạo. `monotonic_ms` là thời gian tương đối của mô hình, không phải giờ RTC; `mask_yv1_lsb` dùng bit 0 cho YV1.
- `TRACE_2_CHU_KY.csv`: toàn bộ 10.501 mẫu từ 0 đến 105 s, bước lấy mẫu 10 ms; gồm thời gian, bước, mask, lệnh bơm và 4 lệnh van.
- `TRACE_STOP_RESET_AUTO.csv`: cùng thời gian lấy mẫu; STOP được nhấn tại 65 s, nhả 66 s; chuyển TẮT tại 67 s; nhấn RESET tại 68 s, nhả 69 s; chọn AUTO tại 70 s. Bổ sung các cột đầu vào, chốt STOP và cảnh báo để đối chiếu việc không tự chạy lại khi chỉ nhả STOP.
- `RUN_SUMMARY.json`: số ca, trạng thái, các sự kiện và SHA-256 của mô hình, tests, nguồn SCL ở `../PLC/`. Hash chỉ xác định phiên bản nguồn được rà soát, **không có nghĩa tests thực thi nguồn SCL**.
- `plc_behavior_model.py`: máy trạng thái, cạnh AUTO/RESET, chốt lỗi và mô hình 5 timer.
- `test_plc_behavior.py`: kiểm tra theo yêu cầu và chính sách khởi động lại đã chọn.

31 ca bao gồm toàn bộ 1.440 phút/ngày; các biên lịch; 5 trạng thái van; 2 chu kỳ; bơm liên tục; STOP/E-STOP/mức nước/quá tải ở cả 5 bước; giữ RESET; OFF→RESET→AUTO; RTC lỗi; khởi động; chu kỳ quét không đều; toàn bộ 32 tổ hợp cảnh báo; dừng trùng thời điểm timer hết hạn; tích lũy lỗi; 20.000 lượt đầu vào ngẫu nhiên có seed cố định.

Một bước được đặt 10 s. Khi đổi mask ở cuối lượt quét, timer của bước mới bắt đầu được gọi ở lượt sau. Với lượt quét đều 10 ms trong mô hình này, bước đầu kéo dài 10.000 ms, các bước liên tiếp sau đó 10.010 ms. Không sử dụng CSV này làm số đo thời gian thực của PLC.

Trước nghiệm thu còn cần: sinh blocks và biên dịch bằng TIA; xác minh `TON_TIME`, `RD_LOC_T`, OB startup và non-retain; chạy PLCSIM/Watch/Trace; kiểm tra DB HMI/driver; thử đấu dây và bảo vệ phần cứng; đo thời gian, dòng điện, áp suất và lưu lượng thực tế.
