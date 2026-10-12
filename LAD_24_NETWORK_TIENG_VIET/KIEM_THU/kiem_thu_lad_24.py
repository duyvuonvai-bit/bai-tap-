"""Chạy: python kiem_thu_lad_24.py. Không Compile TIA hoặc chạy PLCSIM.

doi_chieu_26.py là mô hình bản26 được lưu nguyên trạng làm đối chứng hành vi;
tên Python tiếng Anh trong tệp đối chứng không phải tên tag PLC bản24.
"""
from pathlib import Path
from itertools import product
import json
import random
import traceback
from mo_hinh_lad_24 import ChuTrinh24, dau_vao_mac_dinh
from doi_chieu_26 import LADModel, Inputs

THU_MUC = Path(__file__).resolve().parent
KET_QUA = []
MA_VAN_DUNG = {1: 1, 2: 3, 3: 7, 4: 15, 5: 10}

def kiem_tra(ten, ham):
    try:
        bang_chung = ham()
        KET_QUA.append({"ten": ten, "dat": True, "bang_chung": bang_chung})
    except Exception as loi:
        KET_QUA.append({"ten": ten, "dat": False, "loi": str(loi), "chi_tiet": traceback.format_exc()})

def dung_het(trang_thai):
    assert not trang_thai["ngo_ra"]["bom nuoc"] and trang_thai["ma_van"] == 0, trang_thai

def bat_dau(**thay_doi):
    mo_hinh = ChuTrinh24()
    dau = dau_vao_mac_dinh(**thay_doi)
    dau["chon auto"] = False
    mo_hinh.quet(dau, 0)
    dau["chon auto"] = True
    trang_thai = mo_hinh.quet(dau, 10)
    return mo_hinh, dau, 10, trang_thai

def thay(dau, **sua):
    moi = dict(dau)
    moi.update(sua)
    return moi

def lich_24_gio(buoc_giay):
    mo_hinh = ChuTrinh24()
    dem = 0
    for thu_tu, giay in enumerate(range(0, 86400, buoc_giay)):
        dau = dau_vao_mac_dinh(gio=giay//3600, phut=giay%3600//60, giay=giay%60)
        ket_qua = mo_hinh.quet(dau, thu_tu*10)
        dung_lich = 21600 <= giay < 28800 or 61200 <= giay < 73800
        assert ket_qua["db"]["trong_gio"] == dung_lich
        dem += dung_lich
    assert dem*buoc_giay == 19800
    return {"mau": 86400//buoc_giay, "tong_giay_van_hanh": 19800}

kiem_tra("Lịch đủ 1.440 phút", lambda: lich_24_gio(60))
kiem_tra("Lịch đủ 86.400 giây, gồm ranh giới ca", lambda: lich_24_gio(1))

def chu_trinh(thoi_gian_quet_ms):
    mo_hinh, dau, thoi_diem, trang_thai = bat_dau()
    buoc_cu, bat_dau_buoc = 1, thoi_diem
    thoi_luong = []
    while len(thoi_luong) < 10:
        thoi_diem += thoi_gian_quet_ms
        trang_thai = mo_hinh.quet(dau, thoi_diem)
        buoc = trang_thai["db"]["buoc_hientai"]
        assert trang_thai["ngo_ra"]["bom nuoc"] and not trang_thai["ngo_ra"]["den bao loi"]
        assert trang_thai["ma_van"] == MA_VAN_DUNG[buoc]
        if buoc != buoc_cu:
            assert buoc == buoc_cu%5+1
            do_dai = thoi_diem-bat_dau_buoc
            assert 10000 <= do_dai <= 10000+2*thoi_gian_quet_ms
            thoi_luong.append(do_dai)
            buoc_cu, bat_dau_buoc = buoc, thoi_diem
    return {"chu_ky_quet_ms": thoi_gian_quet_ms, "thoi_gian_10_buoc_ms": thoi_luong}

for chu_ky in (1, 10, 37):
    kiem_tra(f"Hai chu trình, bơm liên tục, quét {chu_ky} ms", lambda n=chu_ky: chu_trinh(n))

def den_buoc(buoc_can):
    mo_hinh, dau, thoi_diem, trang_thai = bat_dau()
    while trang_thai["db"]["buoc_hientai"] != buoc_can:
        thoi_diem += 10
        trang_thai = mo_hinh.quet(dau, thoi_diem)
    return mo_hinh, dau, thoi_diem, trang_thai

def dau_bao_ve(ten):
    for buoc in range(1, 6):
        mo_hinh, dau, thoi_diem, _ = den_buoc(buoc)
        cat = mo_hinh.quet(thay(dau, **{ten: False}), thoi_diem+10)
        dung_het(cat)
        assert not cat["db"]["tu_dong_chay"] and cat["db"]["buoc_hientai"] == 0
        assert cat["db"]["nho_stop" if ten == "stop" else "nho_loi"]
        phuc_hoi = mo_hinh.quet(dau, thoi_diem+20)
        dung_het(phuc_hoi)
        khong_nhan = mo_hinh.quet(thay(dau, **{"nut reset": True}), thoi_diem+30)
        assert not khong_nhan["db"]["xac_nhan_loi"]
        mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+40)
        xac_nhan = mo_hinh.quet(thay(dau, **{"chon auto": False, "nut reset": True}), thoi_diem+50)
        assert xac_nhan["db"]["xac_nhan_loi"]
        dung_het(xac_nhan)
        chay_lai = mo_hinh.quet(dau, thoi_diem+60)
        assert chay_lai["ma_van"] == 1 and chay_lai["ngo_ra"]["bom nuoc"]
    return {"dau_vao": ten, "thu_tai_buoc": [1, 2, 3, 4, 5], "phuc_hoi": "TẮT → nhấn RESET mới → AUTO"}

for ten in ("du nuoc", "dung khan ok", "qua tai", "stop"):
    kiem_tra(f"Dừng và phục hồi {ten} ở cả năm bước", lambda t=ten: dau_bao_ve(t))

def giu_reset_khoi_dong(chon_auto):
    mo_hinh = ChuTrinh24()
    dau = dau_vao_mac_dinh(**{"chon auto": chon_auto, "nut reset": True, "du nuoc": False})
    mot = mo_hinh.quet(dau, 0)
    assert mot["la_quet_dau"] and not mot["db"]["xung_reset"] and not mot["db"]["xung_auto"]
    assert mot["db"]["nho_loi"]
    dung_het(mot)
    hai = mo_hinh.quet(thay(dau, **{"chon auto": False, "du nuoc": True}), 10)
    assert not hai["db"]["xung_reset"] and hai["db"]["nho_loi"]
    mo_hinh.quet(dau_vao_mac_dinh(), 20)
    bon = mo_hinh.quet(dau_vao_mac_dinh(**{"nut reset": True}), 30)
    assert bon["db"]["xac_nhan_loi"] and not bon["db"]["nho_loi"]
    dung_het(bon)
    nam = mo_hinh.quet(dau_vao_mac_dinh(**{"chon auto": True}), 40)
    assert nam["ngo_ra"]["bom nuoc"]
    return {"AUTO_luc_cap_nguon": chon_auto, "RESET_giu": "Không xóa lỗi cho đến nhả/nhấn mới"}

for chon in (False, True):
    kiem_tra(f"RESET giữ khi khởi động, AUTO={int(chon)}", lambda c=chon: giu_reset_khoi_dong(c))

def giu_auto_khoi_dong():
    mo_hinh = ChuTrinh24()
    dau = dau_vao_mac_dinh(**{"chon auto": True})
    for thoi_diem in range(0, 100, 10):
        trang_thai = mo_hinh.quet(dau, thoi_diem)
        dung_het(trang_thai)
        assert not trang_thai["db"]["cho_phep_auto"]
    mo_hinh.quet(thay(dau, **{"chon auto": False}), 100)
    bat = mo_hinh.quet(dau, 110)
    assert bat["ngo_ra"]["bom nuoc"] and bat["ma_van"] == 1
    return "Cấp nguồn AUTO=1 bị chặn, OFF→AUTO mới chạy"

kiem_tra("AUTO giữ khi khởi động", giu_auto_khoi_dong)

def giu_reset_phuc_hoi():
    mo_hinh, dau, thoi_diem, _ = bat_dau()
    mo_hinh.quet(thay(dau, **{"du nuoc": False}), thoi_diem+10)
    mo_hinh.quet(thay(dau, **{"chon auto": False, "du nuoc": False, "nut reset": True}), thoi_diem+20)
    giu = mo_hinh.quet(thay(dau, **{"chon auto": False, "nut reset": True}), thoi_diem+30)
    assert giu["db"]["nho_loi"] and not giu["db"]["xac_nhan_loi"]
    mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+40)
    bam = mo_hinh.quet(thay(dau, **{"chon auto": False, "nut reset": True}), thoi_diem+50)
    assert bam["db"]["xac_nhan_loi"] and not bam["db"]["nho_loi"]
    return "RESET giữ không tự xác nhận khi nước trở lại"

kiem_tra("RESET giữ xuyên suốt phục hồi lỗi", giu_reset_phuc_hoi)

def tat_bat_binh_thuong():
    mo_hinh, dau, thoi_diem, _ = den_buoc(4)
    tat = mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+10)
    dung_het(tat)
    assert not tat["db"]["nho_loi"] and not tat["db"]["nho_stop"]
    bat = mo_hinh.quet(dau, thoi_diem+20)
    assert bat["ngo_ra"]["bom nuoc"] and bat["ma_van"] == 1
    return "OFF thông thường rồi AUTO không cần RESET"

kiem_tra("OFF→AUTO không có lỗi", tat_bat_binh_thuong)

def qua_ca():
    mo_hinh, dau, thoi_diem, trang_thai = bat_dau(gio=5, phut=59, giay=59)
    dung_het(trang_thai)
    for thu_tu, (gio, phut, chay) in enumerate(((6, 0, True), (8, 0, False), (17, 0, True), (20, 30, False)), 1):
        trang_thai = mo_hinh.quet(thay(dau, gio=gio, phut=phut, giay=0), thoi_diem+10*thu_tu)
        assert trang_thai["ngo_ra"]["bom nuoc"] == chay
        assert trang_thai["db"]["cho_phep_auto"] and not trang_thai["ngo_ra"]["den bao loi"]
    return "Giữ quyền qua 08:00/20:30, tự chạy ca sau; không báo lỗi ngoài giờ"

kiem_tra("Tự chạy ca kế tiếp", qua_ca)

def dong_ho_loi():
    mo_hinh, dau, thoi_diem, _ = bat_dau()
    loi = mo_hinh.quet(thay(dau, **{"trangthai rtc": -32768}), thoi_diem+10)
    dung_het(loi)
    assert loi["db"]["nho_loi"]
    dung_het(mo_hinh.quet(dau, thoi_diem+20))
    mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+30)
    dung_het(mo_hinh.quet(dau, thoi_diem+40))
    mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+50)
    xac_nhan = mo_hinh.quet(thay(dau, **{"chon auto": False, "nut reset": True}), thoi_diem+60)
    assert xac_nhan["db"]["xac_nhan_loi"]
    assert mo_hinh.quet(dau, thoi_diem+70)["ngo_ra"]["bom nuoc"]
    return "Lỗi RTC khi AUTO chốt và yêu cầu OFF→RESET→AUTO"

kiem_tra("Lỗi RTC và phục hồi", dong_ho_loi)

def trang_thai_rtc(ma):
    _, _, _, trang_thai = bat_dau(**{"trangthai rtc": ma})
    assert trang_thai["db"]["rtc_ok"] == (ma in (0, 1))
    assert trang_thai["ngo_ra"]["bom nuoc"] == (ma in (0, 1))
    return {"ma_tra": ma, "duoc_phep": ma in (0, 1)}

for ma in (0, 1, -32768, 2):
    kiem_tra(f"Trạng thái RD_LOC_T {ma}", lambda m=ma: trang_thai_rtc(m))

def mien_rtc(ten, gia_tri):
    mo_hinh, dau, thoi_diem, _ = bat_dau()
    trang_thai = mo_hinh.quet(thay(dau, **{ten: gia_tri}), thoi_diem+10)
    dung_het(trang_thai)
    assert not trang_thai["db"]["rtc_ok"] and trang_thai["db"]["nho_loi"]
    return {ten: gia_tri, "ket_qua": "Dừng và chốt lỗi"}

for ten, gia_tri in (("gio", 24), ("phut", 60), ("giay", 60)):
    kiem_tra(f"Miền RTC {ten}={gia_tri}", lambda t=ten, g=gia_tri: mien_rtc(t, g))

def buoc_hong(tu_buoc):
    ket_qua = []
    for gia_tri in (-32768, -1, 6, 100, 32767):
        mo_hinh, dau, thoi_diem, _ = den_buoc(tu_buoc)
        mo_hinh.daiphunnuoc["buoc_hientai"] = gia_tri
        trang_thai = mo_hinh.quet(dau, thoi_diem+10)
        dung_het(trang_thai)
        assert trang_thai["db"]["nho_loi"] and not trang_thai["db"]["tu_dong_chay"]
        assert trang_thai["db"]["buoc_hientai"] == 0
        dung_het(mo_hinh.quet(dau, thoi_diem+20))
        mo_hinh.quet(thay(dau, **{"chon auto": False}), thoi_diem+30)
        xac_nhan = mo_hinh.quet(thay(dau, **{"chon auto": False, "nut reset": True}), thoi_diem+40)
        assert xac_nhan["db"]["xac_nhan_loi"] and not xac_nhan["db"]["nho_loi"]
        assert mo_hinh.quet(dau, thoi_diem+50)["ma_van"] == 1
        ket_qua.append(gia_tri)
    return {"buoc_truoc_loi": tu_buoc, "gia_tri_hong": ket_qua}

for buoc in range(1, 6):
    kiem_tra(f"Ghi sai bước khi đang ở bước {buoc}", lambda b=buoc: buoc_hong(b))

def dung_luc_het_timer():
    mo_hinh, dau, thoi_diem, _ = bat_dau()
    mo_hinh.quet(dau, thoi_diem+10)
    trang_thai = mo_hinh.quet(thay(dau, **{"stop": False}), thoi_diem+10010)
    dung_het(trang_thai)
    assert trang_thai["db"]["buoc_hientai"] == 0 and not any(trang_thai["Q_dinh_thoi"])
    return "STOP cùng scan TON tới hạn vẫn thắng; đủ năm TON được reset"

kiem_tra("STOP trùng lúc TON đủ 10 giây", dung_luc_het_timer)

def vao_doi_chieu(dau):
    return Inputs(auto=dau["chon auto"], water=dau["du nuoc"], reset=dau["nut reset"],
                  estop_ok=dau["dung khan ok"], overload_ok=dau["qua tai"], stop_ok=dau["stop"],
                  rtc_status=dau["trangthai rtc"], hour=dau["gio"], minute=dau["phut"], second=dau["giay"])

def so_hanh_vi(moi, cu):
    bien = moi["db"]
    cap = {"rtc_ok": "rtc_ok", "trong_gio": "in_schedule", "an_toan": "safe",
           "loi_hientai": "fault_now", "nho_loi": "fault_latched", "nho_stop": "stop_latched",
           "da_gat_tat": "off_seen", "xung_reset": "reset_edge", "xung_auto": "auto_edge",
           "xac_nhan_loi": "ack", "cho_phep_auto": "armed", "tu_dong_chay": "run",
           "buoc_hientai": "step"}
    for ten_moi, ten_cu in cap.items():
        assert bien[ten_moi] == cu[ten_cu], (ten_moi, moi, cu)
    assert moi["ngo_ra"]["bom nuoc"] == cu["pump"]
    assert moi["ngo_ra"]["den bao loi"] == cu["alarm"]
    assert moi["ma_van"] == cu["mask"]
    assert moi["Q_dinh_thoi"] == cu["timer_done"]
    assert moi["ET_dinh_thoi_ms"] == cu["timer_et_ms"]

def doi_chieu_ngau_nhien():
    ngau_nhien = random.Random(20261011)
    moi, cu = ChuTrinh24(), LADModel("revised26")
    dau, thoi_diem = dau_vao_mac_dinh(), 0
    so_hanh_vi(moi.quet(dau, 0), cu.scan(vao_doi_chieu(dau), 0))
    so_lan = 50000
    for thu_tu in range(so_lan):
        thoi_diem += ngau_nhien.choice((1, 7, 10, 37, 100, 1000))
        if ngau_nhien.random() < .04:
            ten = ngau_nhien.choice(("chon auto", "du nuoc", "nut reset", "dung khan ok", "qua tai", "stop"))
            dau[ten] = not dau[ten]
        if ngau_nhien.random() < .01:
            dau.update(gio=ngau_nhien.randrange(25), phut=ngau_nhien.randrange(61), giay=ngau_nhien.randrange(61))
        if ngau_nhien.random() < .005:
            dau["trangthai rtc"] = ngau_nhien.choice((0, 0, 1, -32768))
        if ngau_nhien.random() < .002:
            buoc_hong = ngau_nhien.choice((-32768, -1, 6, 100, 32767))
            moi.daiphunnuoc["buoc_hientai"] = cu.step = buoc_hong
        moi_quet = moi.quet(dau, thoi_diem)
        cu_quet = cu.scan(vao_doi_chieu(dau), thoi_diem)
        so_hanh_vi(moi_quet, cu_quet)
        if moi_quet["ngo_ra"]["bom nuoc"]:
            assert moi_quet["db"]["an_toan"] and moi_quet["db"]["trong_gio"]
            assert moi_quet["ma_van"] == MA_VAN_DUNG[moi_quet["db"]["buoc_hientai"]]
        if not moi_quet["db"]["tu_dong_chay"]:
            dung_het(moi_quet)
    return {"so_vong_quet": so_lan, "hat_giong": 20261011,
            "pham_vi": "Trạng thái, cạnh, latch, đầu ra, Q/ET timer; có lỗi bước và RTC"}

kiem_tra("So sánh 24 với 26 trên 50.000 scan ngẫu nhiên", doi_chieu_ngau_nhien)

def doi_chieu_to_hop():
    so_cap = 0
    for bo_vao_dau in product((False, True), repeat=6):
        for bo_vao_sau in product((False, True), repeat=6):
            moi, cu = ChuTrinh24(), LADModel("revised26")
            for thoi_diem, bo_vao in ((0, bo_vao_dau), (10, bo_vao_sau)):
                dau = dau_vao_mac_dinh(**dict(zip(("chon auto", "du nuoc", "nut reset", "dung khan ok", "qua tai", "stop"), bo_vao)))
                so_hanh_vi(moi.quet(dau, thoi_diem), cu.scan(vao_doi_chieu(dau), thoi_diem))
            so_cap += 1
    return {"cap_dau_vao_scan_dau_va_scan_sau": so_cap, "so_dau_vao_bool": 6}

kiem_tra("So sánh 4.096 cặp đầu vào startup với bản26", doi_chieu_to_hop)

def doi_chieu_khi_chay():
    moi, cu = ChuTrinh24(), LADModel("revised26")
    dau = dau_vao_mac_dinh()
    so_hanh_vi(moi.quet(dau, 0), cu.scan(vao_doi_chieu(dau), 0))
    dau["chon auto"] = True
    for thoi_diem in range(10, 150_011, 37):
        so_hanh_vi(moi.quet(dau, thoi_diem), cu.scan(vao_doi_chieu(dau), thoi_diem))
    return {"thoi_gian_mo_phong_ms": 150000, "chu_ky_quet_ms": 37,
            "pham_vi": "Hơn hai chu trình liên tục, so sánh từng scan và Q/ET năm TON"}

kiem_tra("So sánh 24/26 khi chạy liên tục 150 giây", doi_chieu_khi_chay)

def khoi_dong_lai():
    mo_hinh, dau, thoi_diem, _ = den_buoc(5)
    mo_hinh.khoi_tao()
    cho = mo_hinh.quet(dau, 0)
    dung_het(cho)
    assert not cho["db"]["cho_phep_auto"] and not cho["db"]["da_gat_tat"]
    assert not any(cho["Q_dinh_thoi"])
    mo_hinh.quet(thay(dau, **{"chon auto": False}), 10)
    bat = mo_hinh.quet(dau, 20)
    assert bat["ma_van"] == 1 and bat["ngo_ra"]["bom nuoc"]
    return "OB100 mô phỏng reset trạng thái, OFF→AUTO lại sau khởi động"

kiem_tra("Khởi động lại lúc đang ở bước 5", khoi_dong_lai)

def bo_nho_canh_ban_dau():
    for nho_auto, nho_reset in product((False, True), repeat=2):
        mo_hinh = ChuTrinh24()
        mo_hinh.nho_canh.update({"nhocanh auto": nho_auto, "nhocanh reset": nho_reset})
        dau = dau_vao_mac_dinh(**{"chon auto": True, "nut reset": True, "du nuoc": False})
        dau_tien = mo_hinh.quet(dau, 0)
        dung_het(dau_tien)
        assert not dau_tien["db"]["xung_auto"] and not dau_tien["db"]["xung_reset"]
        assert dau_tien["db"]["nho_loi"] and not dau_tien["db"]["cho_phep_auto"]
        assert all(dau_tien["nho_canh"].values())
        dau.update({"chon auto": False, "du nuoc": True})
        giu_reset = mo_hinh.quet(dau, 10)
        assert not giu_reset["db"]["xac_nhan_loi"] and giu_reset["db"]["nho_loi"]
        dung_het(giu_reset)
        dau["nut reset"] = False
        mo_hinh.quet(dau, 20)
        dau["nut reset"] = True
        nhan_moi = mo_hinh.quet(dau, 30)
        assert nhan_moi["db"]["xac_nhan_loi"] and not nhan_moi["db"]["nho_loi"]
        dung_het(nhan_moi)
        dau.update({"chon auto": True, "nut reset": False})
        chay = mo_hinh.quet(dau, 40)
        assert chay["ngo_ra"]["bom nuoc"] and chay["ma_van"] == 1
    return "Cả 4 trạng thái M ban đầu đều bị chặn cạnh scan đầu; giữ RESET không xóa lỗi; OFF + cạnh RESET mới + AUTO mới chạy."

kiem_tra("Bốn trạng thái M ban đầu không tạo cạnh giả", bo_nho_canh_ban_dau)

so_dat = sum(ca["dat"] for ca in KET_QUA)
bao_cao = {"pham_vi": "Mô hình Python độc lập; chưa Compile TIA/PLCSIM/CPU thực tế",
           "tong_nhom": len(KET_QUA), "dat": so_dat, "khong_dat": len(KET_QUA)-so_dat,
           "gia_dinh": ["Ảnh vào ổn định trong scan, một nơi ghi Mbit và mỗi Q",
                         "TON độc lập, gọi mọi scan; IN FALSE xóa Q/ET",
                         "Timer theo thời gian đơn điệu, lịch theo RTC",
                         "OB100/state không Retain; địa chỉ M không chồng lấn",
                         "Quá tải và STOP bằng 1 khi bình thường"],
           "ket_qua": KET_QUA}
(THU_MUC/"ket_qua_kiem_thu_24.json").write_text(json.dumps(bao_cao, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
noi_dung = ["# Kết quả kiểm thử bản LAD 24 network", "",
            f"**{so_dat}/{len(KET_QUA)} nhóm ca đạt.**", "",
            "Kiểm tra bằng mô hình Python độc lập, chưa phải Compile TIA, PLCSIM hoặc thử CPU thật.", "",
            "Bản24 được so sánh với mô hình bản26 đã lưu nguyên trạng trong doi_chieu_26.py. "
            "Tên tiếng Anh trong tệp đối chứng thuộc mô hình cũ; tên tag PLC bản24 dùng đúng bảng người dùng.", "",
            "Chạy lại: `python kiem_thu_lad_24.py` (Python 3.10+, không cần gói ngoài).", "",
            "| Nhóm ca | Kết quả |", "|---|---|"]
noi_dung.extend(f"| {ca['ten']} | {'Đạt' if ca['dat'] else 'KHÔNG ĐẠT'} |" for ca in KET_QUA)
(THU_MUC/"KET_QUA_KIEM_THU_24.md").write_text("\n".join(noi_dung)+"\n", encoding="utf-8")
print(f"{so_dat}/{len(KET_QUA)} nhóm ca đạt")
if so_dat != len(KET_QUA):
    for ca in KET_QUA:
        if not ca["dat"]:
            print(ca["ten"], ca["loi"])
    raise SystemExit(1)
