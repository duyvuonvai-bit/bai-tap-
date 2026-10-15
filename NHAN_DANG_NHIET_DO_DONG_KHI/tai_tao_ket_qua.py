"""Tái tạo nhận dạng FOPDT và đồ thị từ 96 mẫu nhiệt độ đã chép từ ảnh.

Chạy: python tai_tao_ket_qua.py
Yêu cầu: Python 3, numpy, scipy, matplotlib.
CSV dùng dấu chấm thập phân; đơn vị thời gian là giây.
"""
from pathlib import Path
import csv
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/air_temperature_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/air_temperature_cache")
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THU_MUC = Path(__file__).resolve().parent
with (THU_MUC / "du_lieu_thuc_nghiem.csv").open(encoding="utf-8-sig") as tep:
    du_lieu = list(csv.DictReader(tep))
thoi_gian = np.array([float(d["thoi_gian_s"]) for d in du_lieu])
nhiet_do = np.array([float(d["nhiet_do_C"]) for d in du_lieu])
assert len(thoi_gian) == 96
assert np.array_equal(thoi_gian, np.arange(0, 951, 10))
assert np.all(np.isfinite(nhiet_do))

nhiet_do_dau = 29.2
nhiet_do_xac_lap = 44.3
do_tang_nhiet = nhiet_do_xac_lap - nhiet_do_dau
buoc_pwm = 55.0  # Điểm phần trăm, không phải 0.55 ở cách chuẩn hóa này.
he_so_k = do_tang_nhiet / buoc_pwm


def dap_ung(tham_so, thoi_diem):
    hang_so_thoi_gian, do_tre = tham_so
    return nhiet_do_dau + do_tang_nhiet * (
        -np.expm1(-np.maximum(thoi_diem - do_tre, 0) / hang_so_thoi_gian)
    )


nghiem = []
for tau_dau in [100.0, 200.0, 500.0]:
    for tre_dau in [0.0, 10.0, 30.0, 60.0, 100.0]:
        nghiem.append(least_squares(
            lambda p: dap_ung(p, thoi_gian) - nhiet_do,
            [tau_dau, tre_dau], bounds=([0.001, 0], [10000, 950]),
            xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=5000,
        ))
toi_uu = min(nghiem, key=lambda k: np.sum(k.fun ** 2))
tau, tre = toi_uu.x
nhiet_do_mo_hinh = dap_ung(toi_uu.x, thoi_gian)
sai_so = nhiet_do - nhiet_do_mo_hinh
rmse = np.sqrt(np.mean(sai_so ** 2))


def thoi_diem_cat(muc):
    chi_so = np.flatnonzero(nhiet_do >= muc)[0]
    assert chi_so > 0
    i = chi_so
    return thoi_gian[i-1] + (
        (muc - nhiet_do[i-1]) / (nhiet_do[i] - nhiet_do[i-1])
        * (thoi_gian[i] - thoi_gian[i-1])
    )


muc_28 = nhiet_do_dau + do_tang_nhiet * (1 - np.exp(-1/3))
muc_63 = nhiet_do_dau + do_tang_nhiet * (1 - np.exp(-1))
thoi_diem_28 = thoi_diem_cat(muc_28)
thoi_diem_63 = thoi_diem_cat(muc_63)
tau_hai_diem = 1.5 * (thoi_diem_63 - thoi_diem_28)
tre_hai_diem = 1.5 * thoi_diem_28 - 0.5 * thoi_diem_63
rmse_hai_diem = np.sqrt(np.mean(
    (nhiet_do - dap_ung([tau_hai_diem, tre_hai_diem], thoi_gian)) ** 2
))

ket_qua = {
    "so_mau": len(thoi_gian), "chu_ky_lay_mau_s": 10,
    "nhiet_do_dau_C": nhiet_do_dau,
    "nhiet_do_xac_lap_cho_truoc_C": nhiet_do_xac_lap,
    "do_tang_nhiet_C": do_tang_nhiet,
    "buoc_pwm_diem_phan_tram": buoc_pwm,
    "he_so_K_C_tren_diem_phan_tram": he_so_k,
    "he_so_K_C_tren_duty_0_1": he_so_k * 100,
    "hang_so_thoi_gian_s": float(tau), "do_tre_s": float(tre),
    "RMSE_C": float(rmse), "MAE_C": float(np.mean(np.abs(sai_so))),
    "sai_so_tuyet_doi_lon_nhat_C": float(np.max(np.abs(sai_so))),
    "R_binh_phuong": float(1 - np.sum(sai_so**2) / np.sum((nhiet_do-nhiet_do.mean())**2)),
    "phuong_phap_hai_diem": {
        "ty_le_1": float(1-np.exp(-1/3)), "ty_le_2": float(1-np.exp(-1)),
        "muc_1_C": float(muc_28), "muc_2_C": float(muc_63),
        "thoi_diem_1_s": float(thoi_diem_28), "thoi_diem_2_s": float(thoi_diem_63),
        "hang_so_thoi_gian_s": float(tau_hai_diem), "do_tre_s": float(tre_hai_diem),
        "RMSE_C": float(rmse_hai_diem),
    },
    "gia_thiet": [
        "Bước thay đổi PWM được đặt tại t=0 s.",
        "Thời gian ghi trong ảnh được hiểu là giây.",
        "55% được hiểu là độ tăng 55 điểm phần trăm PWM.",
        "Giữ T0=29.2 và T_xac_lap=44.3 theo thông số người dùng.",
        "RMSE tính trên chính 96 mẫu dùng nhận dạng, không phải bộ kiểm định độc lập.",
    ],
}
(THU_MUC / "ket_qua_nhan_dang.json").write_text(
    json.dumps(ket_qua, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
with (THU_MUC / "so_sanh_tung_mau.csv").open("w", encoding="utf-8", newline="") as tep:
    ghi = csv.writer(tep)
    ghi.writerow(["thoi_gian_s", "nhiet_do_thuc_nghiem_C", "nhiet_do_mo_hinh_C", "sai_so_thuc_nghiem_tru_mo_hinh_C"])
    ghi.writerows(zip(thoi_gian, nhiet_do, nhiet_do_mo_hinh, sai_so))

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 14, "axes.labelsize": 12,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.facecolor": "white",
})


def khung_bieu_do(tieu_de):
    hinh, truc = plt.subplots(figsize=(9.0, 5.4), constrained_layout=True)
    truc.set_title(tieu_de, pad=13, fontweight="bold")
    truc.set_xlabel("Thời gian (s)")
    truc.set_ylabel("Nhiệt độ (°C)")
    truc.set_xlim(0, 960)
    truc.set_ylim(28, 46)
    truc.set_xticks(np.arange(0, 951, 100))
    truc.set_yticks(np.arange(28, 47, 2))
    truc.grid(True, color="#dce3e9", linewidth=0.7)
    truc.spines[["top", "right"]].set_visible(False)
    return hinh, truc


hinh_1, truc_1 = khung_bieu_do(
    "Đặc tính thực nghiệm của hệ thống\nổn định nhiệt độ dòng khí"
)
truc_1.plot(thoi_gian, nhiet_do, color="#1764a0", lw=1.5,
            marker="o", markersize=2.8, label="Dữ liệu thực nghiệm (96 mẫu)")
truc_1.axhline(44.3, ls=":", color="#68727c", lw=1,
               label="Nhiệt độ xác lập cho trước: 44,3°C")
truc_1.legend(loc="lower right", framealpha=0.97, fontsize=10)
truc_1.text(0.025, 0.94, "T₀ = 29,2°C; Δd = 55 điểm phần trăm PWM",
            transform=truc_1.transAxes, fontsize=10, va="top",
            bbox={"facecolor": "white", "edgecolor": "#dce3e9", "pad": 5})

hinh_2, truc_2 = khung_bieu_do("So sánh đáp ứng thực nghiệm và mô hình FOPDT")
truc_2.plot(thoi_gian, nhiet_do, color="#1764a0", lw=1.2,
            marker="o", markersize=2.5, label="Dữ liệu thực nghiệm")
thoi_gian_min = np.linspace(0, 950, 1901)
truc_2.plot(thoi_gian_min, dap_ung(toi_uu.x, thoi_gian_min),
            color="#c03b31", ls="--", lw=2.1, label="Mô hình FOPDT")
truc_2.legend(loc="lower right", bbox_to_anchor=(0.99, 0.16), framealpha=0.97)
truc_2.text(0.975, 0.06, f"RMSE = {rmse:.4f}°C".replace(".", ","),
            transform=truc_2.transAxes, ha="right", fontsize=12, fontweight="bold",
            bbox={"facecolor": "white", "edgecolor": "#68727c", "pad": 7})
truc_2.text(0.025, 0.94,
            f"τ = {tau:.2f} s; L = {tre:.2f} s".replace(".", ","),
            transform=truc_2.transAxes, va="top", fontsize=10,
            bbox={"facecolor": "white", "edgecolor": "#dce3e9", "pad": 5})

for hinh, ten in [(hinh_1, "hinh_1_dac_tinh_thuc_nghiem"),
                  (hinh_2, "hinh_2_so_sanh_dap_ung")]:
    hinh.savefig(THU_MUC / (ten + ".png"), dpi=240,
                  metadata={"Title": ten, "Author": ""})
    hinh.savefig(THU_MUC / (ten + ".pdf"),
                  metadata={"Title": ten, "Author": "", "Creator": "Matplotlib"})
    plt.close(hinh)
print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
