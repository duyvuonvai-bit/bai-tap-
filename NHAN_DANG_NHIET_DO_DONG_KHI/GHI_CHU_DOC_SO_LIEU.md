# Ghi chú đọc số liệu từ ảnh

Dữ liệu gồm **96 mẫu**: trang thứ nhất 0–570 s và trang thứ hai 580–950 s. Trang thứ hai được gửi lặp lại, chỉ nhập một lần. CSV dùng dấu chấm thập phân; tài liệu và nhãn đồ thị dùng dấu phẩy khi trình bày tiếng Việt.

## Các giá trị người dùng đã xác nhận

| Thời gian (s) | Nhiệt độ (°C) |
|---:|---:|
| 290 | 41,1 |
| 360 | 42,0 |
| 370 | 42,9 |
| 380 | 42,9 |
| 430 | 42,9 |
| 460 | 42,0 |
| 470 | 41,8 |
| 590 | 42,5 |
| 870 | 43,7 |
| 950 | 42,5 |

## Những nét chữ còn cần đối chiếu nếu có bản gốc rõ hơn

Các ô dưới đây dùng cách đọc chính trong CSV. Không thay bằng giá trị khác chỉ để làm đường thực nghiệm đẹp hơn.

| Thời gian (s) | Giá trị đang dùng (°C) | Cách đọc khác đã xét (°C) |
|---:|---:|---:|
| 20 | 29,6 | 29,8 |
| 150 | 36,6 | 36,0 |
| 260 | 39,9 | 39,8 |
| 340 | 41,9 | 41,4 |
| 350 | 41,4 | 41,9 |

Kiểm tra toàn bộ **32 tổ hợp** của năm cặp giá trị trên, giữ nguyên 91 mẫu còn lại và các điều kiện T₀ = 29,2°C, T∞ = 44,3°C, cho:

- Hằng số thời gian τ: **193,8582–195,4385 s**.
- Độ trễ L: **32,1417–32,9037 s**.
- RMSE: **0,485407–0,499421°C**.

Đây là **phân tích độ nhạy do cách đọc chữ**, không phải khoảng tin cậy thống kê. Giá trị chính τ = 194,5011 s, L = 32,3529 s được tính đúng từ CSV đang cung cấp. Nếu sửa một ô theo bản gốc, cần chạy lại mã để cập nhật tham số và hình.

Giá trị cuối bảng **42,5°C** được giữ nguyên theo xác nhận. Không thay nó bằng **44,3°C**; 44,3°C là nhiệt độ xác lập đã cho để xác định hệ số K và tiệm cận của mô hình.
