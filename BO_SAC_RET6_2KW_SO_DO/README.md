# Bộ sạc Full Bridge 2 kW dùng STM32G474RET6 tự thiết kế

Bản 16/10/2026. Mục tiêu: 220 VAC → PFC 400 VDC → 58 V / 34,48 A; LiFePO₄ 16S.

- **[Mở hướng dẫn và toàn bộ sơ đồ (PDF)](BO_SAC_RET6_2KW_HUONG_DAN_VA_SO_DO.pdf)**
- [Tài liệu tham khảo và ví dụ firmware](TAI_LIEU_THAM_KHAO.md)
- [Hướng dẫn dạng chữ](HUONG_DAN.md) · [Word](HUONG_DAN_VA_TAI_LIEU.docx)
- [Ảnh tổng thể](HINH_TONG_THE/01_TONG_THE_BO_SAC_RET6.png)
- [Mạch công suất](HINH_TONG_THE/02_MACH_DONG_LUC_FULL_BRIDGE.png)
- [Sơ đồ chân RET6](HINH_TONG_THE/03_CHAN_BO_DIEU_KHIEN_RET6.png)
- [Sơ đồ điều khiển KiCad (PDF)](DIEU_KHIEN/BO_DIEU_KHIEN_RET6.pdf)
- [Đấu giắc J2/J3](DIEU_KHIEN/BANG_NOI_LIEN_BO.md)
- [Danh sách mua bo điều khiển, có link tìm Shopee](DANH_SACH_MUA_BO_DIEU_KHIEN.csv)

Bo điều khiển đã được kiểm tra ERC và đối chiếu 147 kết nối vật lý với netlist. Chưa có PCB/Gerber, firmware bộ sạc hoàn chỉnh hoặc thử nghiệm 400 V/2 kW. Driver/đo lường và công suất còn mục TBD; đặc biệt mạch bảo vệ nhanh/giữ lỗi, ngắt đo khi MCU mất nguồn, từ tính, nguồn lái và layout. Không sử dụng các bản vẽ sơ bộ như bộ hướng dẫn hàn hoàn chỉnh để cấp điện lưới.

Mở `DIEU_KHIEN/BO_DIEU_KHIEN_RET6.kicad_pro` bằng KiCad 9; giữ nguyên thư mục thư viện kèm theo. Dữ liệu chân đã đối chiếu từ ST; không có tài liệu cá nhân hoặc tên/MSSV trong gói này.

Liên kết Shopee là kết quả tìm kiếm, chưa xác minh người bán/tồn kho/giá. Tài liệu ghi rõ nguồn đã đọc và nguồn hãng chưa tải được. Mẫu code buck, Full Bridge PWM và PSFB có mục đích khác nhau; không nạp nguyên mẫu vào tầng 2 kW.
