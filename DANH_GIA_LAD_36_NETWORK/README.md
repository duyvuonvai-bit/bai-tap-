# Rà soát LAD đài phun nước — bản để chạy thử

**Bản gốc đúng phần công nghệ chính.** Cần bổ sung chẩn đoán bước ngoài miền 0–5 và làm rõ I/O, tên tag, instance. Đây là gói độc lập, chưa đưa vào đồ án.

Mở theo thứ tự:

1. [Báo cáo Word](Danh_gia_va_sua_LAD_36_Network.docx) hoặc [PDF](Danh_gia_va_sua_LAD_36_Network.pdf): nhận xét từng Network gốc, sửa tối thiểu, hướng dẫn bản 26, bảng thử và đủ hình LAD mới.
2. [Bộ hình LAD vector, 26 Network + OB100](LAD_DE_XUAT/LAD_DE_XUAT_26_NETWORK_VA_OB100.pdf): phóng lớn để dựng trong TIA. Có PNG/SVG từng Network trong cùng thư mục.
3. [Bảng tag/DB](BANG_TAG_VA_DB.csv) và [bảng alias](LAD_DE_XUAT/BANG_ALIAS.md): đối chiếu tên trong hình với DB `daiphunnuoc` và I/O hiện có.
4. [Hướng dẫn đọc trực tiếp trên GitHub](HUONG_DAN_SUA_VA_THU_LAD.md): phần 4 sửa ít nhất trên chương trình đang có; phần 5–7 là bản tổ chức lại 26 Network.
5. [Kết quả kiểm thử](KIEM_THU/KET_QUA_KIEM_THU.md): 31/31 nhóm ca mô hình đạt, gồm tái hiện trường hợp bước sai của bản gốc và xác nhận bản sửa dừng/chốt lỗi.

`LAD_GOC` giữ nguyên 43 hình của ZIP để đối chiếu, không sửa ảnh gốc. Hai lần tải ZIP có cùng SHA256 `1bf66bf07fd26391f29db4564bd355bb1974a2416f4af7d903057f499dccd1e5`.

**Phạm vi kiểm chứng:** rà soát sơ đồ và mô hình Python. Chưa có dự án `.ap16/.zap16`; chưa Compile trong TIA hoặc chạy PLCSIM/phần cứng. Các hình mới là thiết kế LAD, không phải ảnh chụp TIA đã biên dịch. CSV là bảng tra, không khẳng định định dạng import PLC tags của TIA.

Chọn một trong hai cách: sửa ít trên bản 36 hoặc dựng bản 26. Không gọi cả hai cùng ghi ngõ ra. Bản 26 giữ năm TON, current/next và thêm startup/bảo vệ bước; RTC lỗi khi AUTO được chốt nên phục hồi cần OFF → RESET → AUTO. Lịch và ma trận van giữ đúng đề.

Chạy lại mô hình với Python 3.10+: `cd KIEM_THU` rồi `python test_lad_model.py`. Chi tiết evidence trong JSON; không coi kết quả đó là log PLC.

Để tải từ GitHub: mở tệp và dùng **Download raw file**, hoặc tải ZIP `LAD_DA_RA_SOAT_TRON_BO.zip`. Không dùng liên kết artifact của phiên cũ.
