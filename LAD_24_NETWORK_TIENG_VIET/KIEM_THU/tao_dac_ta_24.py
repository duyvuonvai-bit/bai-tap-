"""Tạo JSON đặc tả ngữ nghĩa để đối chiếu sơ đồ; không phải XML nhập TIA."""
from pathlib import Path
import json

thu_muc = Path(__file__).resolve().parent
db = '"daiphunnuoc".'
def bien(ten):
    return db + ('"'+ten+'"' if ' ' in ten else ten)

mang = []
def them(ten, phep_tinh, ghi_chu=''):
    mang.append({'so': len(mang)+1, 'ten': ten, 'logic': phep_tinh, 'ghi_chu': ghi_chu})

them('Đọc đồng hồ và kiểm tra giờ hợp lệ', [
    f'RD_LOC_T(RET_VAL => {bien("trangthai rtc")}, OUT => {bien("gio plc")});',
    f'{bien("rtc_ok")} := (({bien("trangthai rtc")} = 0) OR ({bien("trangthai rtc")} = 1)) AND ({bien("gio plc")}.HOUR <= 23) AND ({bien("gio plc")}.MINUTE <= 59) AND ({bien("gio plc")}.SECOND <= 59);'],
    'RD_LOC_T gọi vô điều kiện, sau đó mới tính rtc_ok. Các trường DTL này kiểu USInt. UTC+7, DST tắt tại Việt Nam.')
them('Ca sáng', [f'{bien("ca_sang")} := {bien("rtc_ok")} AND ({bien("gio plc")}.HOUR >= 6) AND ({bien("gio plc")}.HOUR < 8);'])
them('Ca chiều và tối', [f'{bien("ca_toi")} := {bien("rtc_ok")} AND ((({bien("gio plc")}.HOUR >= 17) AND ({bien("gio plc")}.HOUR < 20)) OR (({bien("gio plc")}.HOUR = 20) AND ({bien("gio plc")}.MINUTE < 30)));'])
them('Tổng hợp lịch vận hành', [f'{bien("trong_gio")} := {bien("ca_sang")} OR {bien("ca_toi")};'])
them('Điều kiện đầu vào', [f'{bien("an_toan")} := "du nuoc" AND "dung khan ok" AND "qua tai" AND "stop";'],
    'I0.4 qua tai=1 là chưa quá tải; I0.5 stop=1 là chưa nhấn STOP. Giữ tên user, ghi comment để tránh đảo mức.')
them('Lỗi công nghệ, RTC và bước không hợp lệ', [f'{bien("loi_hientai")} := NOT "du nuoc" OR NOT "dung khan ok" OR NOT "qua tai" OR ("chon auto" AND NOT {bien("rtc_ok")}) OR ({bien("buoc_hientai")} < 0) OR ({bien("buoc_hientai")} > 5);'])
them('Tạo xung cạnh bằng hai Mbit có sẵn', [
    f'{bien("xung_reset")} := "nut reset" AND NOT "nhocanh reset" AND NOT {bien("khoi_tao_cho")};',
    f'{bien("xung_auto")} := "chon auto" AND NOT "nhocanh auto" AND NOT {bien("khoi_tao_cho")};'],
    'M0.0/M0.1 là trạng thái scan trước; chỉ cập nhật cuối NW24. Không dùng thêm R_TRIG/P_TRIG cho cùng bộ nhớ.')
them('Điều kiện xác nhận phục hồi lỗi', [f'{bien("xac_nhan_loi")} := {bien("xung_reset")} AND NOT "chon auto" AND {bien("an_toan")} AND {bien("rtc_ok")} AND NOT {bien("loi_hientai")};'])
them('Chốt lỗi', [f'SR {bien("nho_loi")}: S := {bien("loi_hientai")}; R1 := {bien("xac_nhan_loi")};'], 'SR/R1 ưu tiên RESET. S và R1 loại trừ nhau.')
them('Chốt STOP', [f'SR {bien("nho_stop")}: S := NOT "stop"; R1 := {bien("xac_nhan_loi")};'])
them('Ghi nhận đã gạt về TẮT', [f'IF NOT "chon auto" THEN SET {bien("da_gat_tat")}; END_IF;'], 'Cuộn S, không phải cuộn thường.')
them('Thu hồi hoặc cấp quyền AUTO', [
    f'{bien("huy_phep_chay")} := NOT "chon auto" OR NOT {bien("an_toan")} OR NOT {bien("rtc_ok")} OR {bien("nho_loi")} OR {bien("nho_stop")} OR {bien("khoi_tao_cho")};',
    f'SR {bien("cho_phep_auto")}: S := {bien("xung_auto")} AND {bien("da_gat_tat")} AND NOT {bien("huy_phep_chay")}; R1 := {bien("huy_phep_chay")};'],
    'Đúng thứ tự: tính hủy rồi chốt. Không đưa ngoài giờ vào hủy quyền.')
them('Cho phép chạy chu trình', [f'{bien("tu_dong_chay")} := {bien("cho_phep_auto")} AND {bien("trong_gio")} AND NOT {bien("huy_phep_chay")};'])
them('Bước tiếp theo mặc định', [
    f'{bien("buoc_tieptheo")} := {bien("buoc_hientai")};',
    f'IF NOT {bien("tu_dong_chay")} THEN {bien("buoc_tieptheo")} := 0; END_IF;',
    f'IF {bien("tu_dong_chay")} AND ({bien("buoc_hientai")} = 0) THEN {bien("buoc_tieptheo")} := 1; END_IF;'], 'Giữ thứ tự ba rung.')
for buoc in range(1, 6):
    tiep = buoc+1 if buoc < 5 else 1
    them(f'Định thời bước {buoc}, chuyển sang bước {tiep}', [
        f'"dem_buoc{buoc}".TON(IN := {bien("tu_dong_chay")} AND ({bien("buoc_hientai")} = {buoc}), PT := T#10s);',
        f'IF "dem_buoc{buoc}".Q THEN {bien("buoc_tieptheo")} := {tiep}; END_IF;'],
        'Sơ đồ ngữ nghĩa: dùng TON, mỗi timer có instance riêng do TIA tạo đúng loại. Gọi mọi scan; IN=0 reset Q/ET. Q sau lời gọi điều khiển MOVE, không ghi buoc_hientai tại đây.')
them('Chốt bước sau năm TON', [f'{bien("buoc_hientai")} := {bien("buoc_tieptheo")};'])
them('Xác nhận có lệnh mở van ở bước hợp lệ', [f'{bien("co_van_mo")} := {bien("tu_dong_chay")} AND ({bien("buoc_hientai")} >= 1) AND ({bien("buoc_hientai")} <= 5);'], 'Tái dùng biến có sẵn: đây là lệnh logic, không phải phản hồi van thật.')
them('Lệnh bơm và bốn van', [
    f'"bom nuoc" := {bien("co_van_mo")};',
    f'"van 1" := {bien("co_van_mo")} AND ({bien("buoc_hientai")} <= 4);',
    f'"van 2" := {bien("co_van_mo")} AND ({bien("buoc_hientai")} >= 2);',
    f'"van 3" := {bien("co_van_mo")} AND ({bien("buoc_hientai")} >= 3) AND ({bien("buoc_hientai")} <= 4);',
    f'"van 4" := {bien("co_van_mo")} AND ({bien("buoc_hientai")} >= 4);'], 'Mỗi Q một nơi ghi. YV1 là bit thấp: mask 1,3,7,15,10.')
them('Đèn báo lỗi', [f'"den bao loi" := {bien("nho_loi")};'])
them('Cập nhật bộ nhớ cạnh và kết thúc khởi tạo', [
    '"nhocanh auto" := "chon auto";', '"nhocanh reset" := "nut reset";',
    f'RESET {bien("khoi_tao_cho")};'], 'Bắt buộc đặt cuối OB1, sau mọi nơi dùng xung. Không ghi các Mbit ở nơi khác.')

dac_ta = {'dinh_dang': 'Đặc tả ngữ nghĩa LAD, không phải XML TIA hoặc mã đã biên dịch',
          'phien_ban': '24 network, tên biến đúng bảng người dùng',
          'OB100': {'khong_doc_dau_vao': True,
                    'reset_bool': ['nho_loi', 'nho_stop', 'da_gat_tat', 'cho_phep_auto'],
                    'reset_mbit': [],
                    'move_0': ['buoc_hientai', 'buoc_tieptheo'], 'set_bool': ['khoi_tao_cho'],
                    'chu_y': 'Các biến trạng thái/timer không Retain; các biến tổ hợp được ghi mọi scan trước sử dụng. Hai xung được tính lại ở NW07, bị chặn trong scan đầu; hai Mbit nhận đầu vào hiện tại ở NW24 trước khi xóa khoi_tao_cho, nên không cần rung RESET riêng trong OB100.'},
          'bien_DB_them': [{'ten': 'khoi_tao_cho', 'kieu': 'Bool', 'start': True, 'retain': False},
                          {'ten': 'xac_nhan_loi', 'kieu': 'Bool', 'start': False, 'retain': False}],
          'khong_con_dung_trong_thuat_toan': [f'xong_buoc{buoc}' for buoc in range(1, 6)],
          'chu_y_xoa': 'Chỉ xóa trường DB hoặc instance cũ sau kiểm tra cross-reference toàn dự án/HMI. Không coi bảng xuất bản là yêu cầu xóa mù.',
          'timer': [f'dem_buoc{buoc}' for buoc in range(1, 6)],
          'networks': mang}
assert len(mang) == 24
(thu_muc/'dac_ta_24_network.json').write_text(json.dumps(dac_ta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Đã tạo 24 network')
