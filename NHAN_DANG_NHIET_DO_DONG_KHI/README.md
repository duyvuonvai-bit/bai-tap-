# Nhận dạng hệ thống nhiệt độ dòng khí

Từ 96 mẫu nhiệt độ chép từ hai trang ảnh (0–950 s, chu kỳ 10 s), với nhiệt độ ban đầu **29,2°C**, nhiệt độ xác lập cho trước **44,3°C** và bước PWM **55 điểm phần trăm**, mô hình bậc nhất có trễ (FOPDT) nhận dạng được là:

$$G(s)=\frac{\Delta T(s)}{\Delta d(s)}\approx\frac{0.274545\,e^{-32.35286s}}{194.50113s+1}.$$

Trong biểu thức này, `d` được biểu diễn bằng số phần trăm từ 0 đến 100. Nếu dùng duty từ 0 đến 1, thay hệ số 0,274545 bằng **27,454545**, và bước đầu vào là 0,55. Hai cách dùng cho cùng đáp ứng nhiệt độ.

Sai số trên 96 mẫu dùng để nhận dạng: **RMSE = 0,4942555°C**, MAE = 0,3799930°C. Giữ nguyên toàn bộ điểm đo, kể cả 950 s = 42,5°C. Đây là đánh giá độ khớp trên dữ liệu nhận dạng, chưa phải kiểm định bằng một thí nghiệm độc lập.

## Các tệp chính

| Tệp | Nội dung |
|---|---|
| `KET_QUA_NHAN_DANG_NHIET_DO.docx` | Bản Word có lời giải, hai đồ thị và đủ 96 điểm đo |
| `KET_QUA_NHAN_DANG_NHIET_DO.pdf` | Bản PDF để xem/in |
| `hinh_1_dac_tinh_thuc_nghiem.png` | Đồ thị thực nghiệm, ảnh 240 dpi |
| `hinh_2_so_sanh_dap_ung.png` | Đồ thị thực nghiệm và FOPDT, kèm RMSE |
| Hai tệp hình `.pdf` tương ứng | Hình dạng vector để chèn báo cáo |
| `NHAN_DANG_NHIET_DO_DONG_KHI.m` | MATLAB độc lập, đã nhúng toàn bộ số liệu |
| `du_lieu_thuc_nghiem.csv` | Dữ liệu đầu vào, 96 mẫu, dấu chấm thập phân |
| `so_sanh_tung_mau.csv` | Nhiệt độ đo, nhiệt độ mô hình và sai số từng mẫu |
| `ket_qua_nhan_dang.json` | Thông số và sai số đầy đủ |
| `GHI_CHU_DOC_SO_LIEU.md` | Nguồn dữ liệu, các ô đã xác nhận và độ nhạy do đọc ảnh |
| `tai_tao_ket_qua.py` | Chương trình Python tái tạo kết quả và hình |

## Chạy bằng MATLAB

1. Lưu tệp `NHAN_DANG_NHIET_DO_DONG_KHI.m` vào một thư mục có quyền ghi. Nếu tải ZIP, giải nén trước.
2. Mở tệp bằng MATLAB R2018b trở lên và nhấn **Run**.
3. Chương trình tự nhận dạng, in hàm truyền, vẽ hai hình và lưu kết quả vào thư mục `KET_QUA_MATLAB` bên cạnh tệp `.m`.

Phần nhận dạng và vẽ không yêu cầu Optimization Toolbox hoặc Control System Toolbox. Nếu có Control System Toolbox, chương trình có thể tạo thêm đối tượng `tf` có trễ. Mã MATLAB đã được kiểm tra cú pháp và đối chiếu số liệu; môi trường tạo tài liệu không có MATLAB để chạy trực tiếp.

## Cách tính

Độ tăng nhiệt độ: ΔT = 44,3 − 29,2 = **15,1°C**. Hệ số khuếch đại: K = 15,1/55 = **0,274545°C/điểm phần trăm**.

Với bước PWM đặt tại t = 0 s, đáp ứng tuyệt đối dùng để khớp là:

$$T_m(t)=\begin{cases}29.2,&0\leq t<L\\29.2+15.1\left(1-e^{-(t-L)/\tau}\right),&t\geq L.\end{cases}$$

Tìm τ > 0 và L ≥ 0 để cực tiểu tổng bình phương sai số trên 96 mẫu, giữ nguyên T₀, T∞ và K theo thông số đã cho. Không lọc hoặc ép đường đo tăng đơn điệu. Kết quả: **τ ≈ 194,50 s**, **L ≈ 32,35 s**.

Đối chiếu bằng cách hai điểm 28,3469% và 63,2121% cho τ ≈ 185,35 s, L ≈ 36,72 s, RMSE ≈ 0,5064°C. Bản báo cáo trình bày cả cách này để thuận tiện kiểm tra bằng tay; hình so sánh chính dùng kết quả khớp toàn bộ dữ liệu.

## Phạm vi và giả thiết

- Thời gian trên bảng được hiểu là giây; mốc t = 0 là lúc đổi PWM. Nếu mốc đặt bước thực tế khác, độ trễ suy ra sẽ thay đổi.
- Δd = 55% được hiểu là **tăng 55 điểm phần trăm PWM**, không phải tăng tương đối 55% so với một mức nền chưa biết.
- 44,3°C là nhiệt độ xác lập do người dùng cung cấp, không phải mẫu cuối bảng và cũng không phải giá trị được tối ưu lại.
- Mô hình gần đúng áp dụng quanh điều kiện thí nghiệm này; không khẳng định nó mô tả mọi mức PWM, tốc độ quạt hoặc điều kiện môi trường.
- Các chữ số thập phân của τ và L là kết quả tính toán. Bước lấy mẫu 10 s và chất lượng ảnh không cho phép khẳng định độ trễ thực đo chính xác đến 0,01 s.
- Ảnh bài mẫu chỉ dùng để định dạng mô hình FOPDT và hai loại đồ thị; không lấy nhiệt độ, thời gian hoặc RMSE của bài mẫu làm số liệu cho bài này.

Có thể tái tạo độc lập bằng `python tai_tao_ket_qua.py` sau khi cài `numpy scipy matplotlib`. Toàn bộ tính toán và đồ thị trong báo cáo đã được chạy bằng Python; một phép tối ưu độc lập cho cùng τ, L và RMSE.
