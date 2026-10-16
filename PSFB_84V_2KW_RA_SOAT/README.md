# Rà soát bộ sạc PSFB 2 kW — chuyển sang pin 20S / 84 V

Ngày16/10/2026. Đã xác nhận với người dùng: pin20S theo hình84 V; dùng **bo STM32G474RET6 hàn sẵn**, không phải chip rời; cần cuối cùng cả sơ đồ nguyên lý và PCB/Gerber có vị trí lắp linh kiện.

## Kết quả của đợt rà soát này

- Kiểm tra sơ đồ khối và ảnh nguyên lý: [báo cáo chi tiết](AUDIT_IMAGE.md).
- Tính dòng, duty, biến áp theo điều kiện lõi, cuộn cảm, tụ, shunt, chia áp và ngưỡng bảo vệ: [bảng tính](TINH_TOAN_SO_BO.md). Mã tính `calc.py` và kết quả `calcs.json` đi kèm.
- [Bảng linh kiện có cột công dụng](BANG_LINH_KIEN_VA_CONG_DUNG.md).
- [Sơ đồ sửa các kết nối công suất chính](SO_DO_KET_NOI_DA_SUA.pdf), [ảnh PNG](SO_DO_KET_NOI_DA_SUA.png). Hình này là sơ đồ kết nối chức năng, chưa phải bản vẽ hàn từng chân IC.
- [PDF báo cáo tổng hợp](BAO_CAO_PSFB_84V_2KW.pdf).

## Bộ thông số thiết kế đang chọn

- Pin mục tiêu: Li-ion20S, 4,2 V/cell,50 Ah. Đây là thông số **chọn cho thiết kế**, không phải thông số đã đo/xác minh của bộ pin đang có.
- BMS mục tiêu: đúng hóa học20S, dòng **sạc liên tục** ít nhất30 A, giám sát áp từng cell và nhiệt. Dòng xả ghi trên BMS không thay thông số dòng sạc.
- CC tối đa: 2.000/84≈23,81 A, tương đương0,476C nếu pin thực sự50 Ah. Ở60 V với dòng này công suất chỉ1,43 kW; không phải bộ sạc giữ2 kW trên toàn dải.
- CV mục tiêu:84 V; sai số, ngưỡng bảo vệ và giới hạn từng cell cần phối hợp với cell/BMS thật.
- PSFB: khảo sát50 kHz; PFC khảo sát65 kHz. Đây là lựa chọn ban đầu để tính, chưa đo tối ưu tổn hao.
- Bus: chọn danh định400 V và xét380–420 V trong tính thiết kế, gồm dự trữ cho ripple/quá độ; chưa phải dải vận hành đã đo.

Không được mặc định20 viên18650 là bộ pin50 Ah hoặc chịu dòng23,81 A. Dung lượng/cách ghép và dòng sạc cho phép phải xác minh trước khi nối pin thật.

## Trạng thái PCB: CHƯA CÓ GERBER ĐỂ ĐẶT GIA CÔNG

Ảnh nguyên lý ban đầu có các lỗi tên net, ngưỡng bảo vệ và cấu trúc driver/đo lường, nên không thể chuyển trực tiếp thành PCB đáng tin cậy. Bộ này chưa có `.kicad_pcb`, Gerber hoặc bản vẽ lắp ráp hoàn chỉnh. Không gọi hình bố trí khối là PCB.

Bo MCU người dùng cung cấp: https://shopee.vn/product/1573220776/56315356231 . Tên trang có cả RCT6/RET6 và biến thể khác; người dùng xác nhận đang dùng RET6. Môi trường trả403 khi mở trang nên **chưa đọc được ảnh, kích thước, pinout đầu cắm hoặc schematic của bo**. Không suy ra đầu cắm từ pin IC LQFP64.

Để chốt footprint bo MCU cần ảnh rõ hai mặt có chữ chân, kích thước/bước hàng chân hoặc schematic/pinout chính thức của đúng biến thể. Có thể dùng cáp nối tới giắc giao diện riêng để không phụ thuộc footprint cắm trực tiếp, nhưng vẫn cần biết chân nguồn và chức năng nào đang được bo sử dụng.

Những phần thiết kế còn phải hoàn thiện trước khi xuất PCB: chọn mã và xác minh datasheet/footprint linh kiện công suất, driver và nguồn cách ly; thiết kế từ tính với lõi thực; bảo vệ nhanh sơ cấp và chốt lỗi; đo lường/ADC khi mất nguồn; khối nối pin; PFC/nguồn phụ chi tiết; bố trí dòng công suất và cách điện. Không có kiểm tra ERC/DRC hay thử phần cứng cho sơ đồ ảnh mới trong gói này.

## Phạm vi nguồn

Nguồn chính của rà soát là ba ảnh người dùng gửi và dữ liệu chân RET6 đã đối chiếu từ ST trong đợt trước. Các trang hãngTI/ST và trang Shopee không tải được trong phiên này; những thông số chưa xác minh được ghi rõ trong báo cáo. Kiểm tra công thức và tệp không chứng minh mạch đã đạt2 kW, ZVS, hiệu suất hoặc cách điện.
