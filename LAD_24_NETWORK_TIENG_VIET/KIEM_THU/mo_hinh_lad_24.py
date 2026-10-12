"""Mô hình độc lập theo thứ tự 24 network LAD, không phải chương trình Siemens.

Tên PLC trong hai bảng người dùng được giữ trong các từ điển. Đây là Python để
kiểm tra hành vi, không thể nhập trực tiếp vào TIA Portal. Bộ định thời dùng thời
gian đơn điệu, độc lập RTC; chưa mô phỏng trễ phần cứng, dội tiếp điểm hoặc CPU.
"""
from dataclasses import dataclass


@dataclass
class DinhThoi:
    bat_dau_ms: int | None = None
    Q: bool = False
    ET_ms: int = 0

    def thuc_hien(self, IN, hien_tai_ms, PT_ms=10_000):
        if not IN:
            self.bat_dau_ms, self.Q, self.ET_ms = None, False, 0
        else:
            if self.bat_dau_ms is None:
                self.bat_dau_ms = hien_tai_ms
            self.ET_ms = min(hien_tai_ms-self.bat_dau_ms, PT_ms)
            self.Q = hien_tai_ms-self.bat_dau_ms >= PT_ms
        return self.Q


def dau_vao_mac_dinh(**thay_doi):
    gia_tri = {"chon auto": False, "du nuoc": True, "nut reset": False,
               "dung khan ok": True, "qua tai": True, "stop": True,
               "trangthai rtc": 0, "gio": 7, "phut": 0, "giay": 0}
    gia_tri.update(thay_doi)
    return gia_tri


class ChuTrinh24:
    def __init__(self):
        self.khoi_tao()

    def khoi_tao(self):
        """Mô hình OB100 và trạng thái không Retain; không đọc đầu vào tại đây."""
        self.daiphunnuoc = {ten: False for ten in (
            "rtc_ok", "ca_sang", "ca_toi", "trong_gio", "an_toan",
            "loi_hientai", "nho_loi", "nho_stop", "xung_reset", "xung_auto",
            "da_gat_tat", "huy_phep_chay", "cho_phep_auto", "tu_dong_chay",
            "co_van_mo", "xac_nhan_loi")}
        self.daiphunnuoc.update({"gio plc": {"HOUR": 0, "MINUTE": 0, "SECOND": 0},
                                "trangthai rtc": 0, "buoc_hientai": 0,
                                "buoc_tieptheo": 0, "khoi_tao_cho": True})
        self.nho_canh = {"nhocanh auto": False, "nhocanh reset": False}
        self.dinh_thoi = {f"dem_buoc{buoc}": DinhThoi() for buoc in range(1, 6)}
        self.ngo_ra = {ten: False for ten in ("bom nuoc", "van 1", "van 2",
                                             "van 3", "van 4", "den bao loi")}
        self.lan_quet_truoc_ms = None

    def quet(self, dau_vao, thoi_diem_ms):
        if self.lan_quet_truoc_ms is not None and thoi_diem_ms <= self.lan_quet_truoc_ms:
            raise ValueError("Thời gian vòng quét phải tăng nghiêm ngặt")
        self.lan_quet_truoc_ms = thoi_diem_ms
        bien = self.daiphunnuoc
        dau = dau_vao
        la_quet_dau = bien["khoi_tao_cho"]

        # 01: Mô hình kết quả RD_LOC_T và kiểm tra RTC; HOUR/MINUTE/SECOND là USInt.
        bien["gio plc"] = {"HOUR": dau["gio"], "MINUTE": dau["phut"], "SECOND": dau["giay"]}
        bien["trangthai rtc"] = dau["trangthai rtc"]
        bien["rtc_ok"] = (dau["trangthai rtc"] in (0, 1)
                          and 0 <= dau["gio"] <= 23
                          and 0 <= dau["phut"] <= 59
                          and 0 <= dau["giay"] <= 59)
        # 02–04: Lịch có đầu ca, không gồm thời điểm hết ca.
        bien["ca_sang"] = bien["rtc_ok"] and 6 <= dau["gio"] < 8
        bien["ca_toi"] = bien["rtc_ok"] and (17 <= dau["gio"] < 20
                             or (dau["gio"] == 20 and dau["phut"] < 30))
        bien["trong_gio"] = bien["ca_sang"] or bien["ca_toi"]
        # 05–06: Đầu vào bảo vệ đều bằng 1 khi bình thường.
        bien["an_toan"] = all(dau[ten] for ten in ("du nuoc", "dung khan ok", "qua tai", "stop"))
        bien["loi_hientai"] = (not dau["du nuoc"] or not dau["dung khan ok"]
                             or not dau["qua tai"] or (dau["chon auto"] and not bien["rtc_ok"])
                             or bien["buoc_hientai"] < 0 or bien["buoc_hientai"] > 5)
        # 07: Bộ nhớ M vẫn chứa giá trị đầu vào của scan trước.
        bien["xung_reset"] = dau["nut reset"] and not self.nho_canh["nhocanh reset"] and not bien["khoi_tao_cho"]
        bien["xung_auto"] = dau["chon auto"] and not self.nho_canh["nhocanh auto"] and not bien["khoi_tao_cho"]
        # 08: Chỉ xác nhận khi OFF, đã hết lỗi, có cạnh nhấn mới.
        bien["xac_nhan_loi"] = (bien["xung_reset"] and not dau["chon auto"]
                               and bien["an_toan"] and bien["rtc_ok"] and not bien["loi_hientai"])
        # 09–10: Siemens SR với chân R1 ưu tiên reset.
        bien["nho_loi"] = (bien["nho_loi"] or bien["loi_hientai"]) and not bien["xac_nhan_loi"]
        bien["nho_stop"] = (bien["nho_stop"] or not dau["stop"]) and not bien["xac_nhan_loi"]
        # 11: Cuộn S, không phải cuộn thường.
        if not dau["chon auto"]:
            bien["da_gat_tat"] = True
        # 12: Tái sử dụng điều kiện hủy; ngoài giờ không hủy quyền.
        bien["huy_phep_chay"] = (not dau["chon auto"] or not bien["an_toan"]
                                or not bien["rtc_ok"] or bien["nho_loi"]
                                or bien["nho_stop"] or bien["khoi_tao_cho"])
        yeu_cau_cap_quyen = bien["xung_auto"] and bien["da_gat_tat"] and not bien["huy_phep_chay"]
        bien["cho_phep_auto"] = (bien["cho_phep_auto"] or yeu_cau_cap_quyen) and not bien["huy_phep_chay"]
        # 13: Quyền đã bị thu hồi ngay trong scan có lỗi/STOP.
        bien["tu_dong_chay"] = bien["cho_phep_auto"] and bien["trong_gio"] and not bien["huy_phep_chay"]
        # 14: Ba rung phải giữ thứ tự.
        bien["buoc_tieptheo"] = bien["buoc_hientai"]
        if not bien["tu_dong_chay"]:
            bien["buoc_tieptheo"] = 0
        if bien["tu_dong_chay"] and bien["buoc_hientai"] == 0:
            bien["buoc_tieptheo"] = 1
        # 15–19: Năm TON luôn gọi; chưa ghi buoc_hientai tại đây.
        for buoc in range(1, 6):
            bo_dem = self.dinh_thoi[f"dem_buoc{buoc}"]
            bo_dem.thuc_hien(bien["tu_dong_chay"] and bien["buoc_hientai"] == buoc, thoi_diem_ms)
            if bo_dem.Q:
                bien["buoc_tieptheo"] = buoc+1 if buoc < 5 else 1
        # 20: Chỉ commit sau đủ năm TON.
        bien["buoc_hientai"] = bien["buoc_tieptheo"]
        # 21: Có lệnh mở van, không phải cảm biến phản hồi van.
        bien["co_van_mo"] = bien["tu_dong_chay"] and 1 <= bien["buoc_hientai"] <= 5
        # 22–23: Mỗi ngõ ra một nơi ghi.
        self.ngo_ra["bom nuoc"] = bien["co_van_mo"]
        self.ngo_ra["van 1"] = bien["co_van_mo"] and bien["buoc_hientai"] <= 4
        self.ngo_ra["van 2"] = bien["co_van_mo"] and bien["buoc_hientai"] >= 2
        self.ngo_ra["van 3"] = bien["co_van_mo"] and 3 <= bien["buoc_hientai"] <= 4
        self.ngo_ra["van 4"] = bien["co_van_mo"] and bien["buoc_hientai"] >= 4
        self.ngo_ra["den bao loi"] = bien["nho_loi"]
        # 24: Sau mọi nơi dùng xung mới cập nhật Mbit và xóa bit khởi tạo.
        self.nho_canh["nhocanh auto"] = dau["chon auto"]
        self.nho_canh["nhocanh reset"] = dau["nut reset"]
        bien["khoi_tao_cho"] = False
        return {"db": dict(bien), "ngo_ra": dict(self.ngo_ra),
                "nho_canh": dict(self.nho_canh), "la_quet_dau": la_quet_dau,
                "ma_van": sum(1 << (buoc-1) for buoc in range(1, 5) if self.ngo_ra[f"van {buoc}"]),
                "Q_dinh_thoi": [bo_dem.Q for bo_dem in self.dinh_thoi.values()],
                "ET_dinh_thoi_ms": [bo_dem.ET_ms for bo_dem in self.dinh_thoi.values()]}
