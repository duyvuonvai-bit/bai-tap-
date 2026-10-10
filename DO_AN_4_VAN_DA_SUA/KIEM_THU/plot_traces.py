"""Render recorded independent-model traces, not PLC/PLCSIM measurements."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/fountain_plot_cache')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/fountain_font_cache')
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parent
OUT=BASE.parent/'HINH'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})

def read(name):
    with (BASE/name).open() as f:
        data=list(csv.DictReader(f))
    return {k:[int(r[k]) for r in data] for k in data[0]}

def save(fig,name):
    for ext in ('png','pdf','svg'):
        fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',dpi=180)
    plt.close(fig)

d=read('TRACE_2_CHU_KY.csv'); t=[m/1000 for m in d['monotonic_ms']]
fig,axes=plt.subplots(6,1,figsize=(12,8),sharex=True,gridspec_kw={'height_ratios':[1.4,1,1,1,1,1]})
for ax,k,l in zip(axes,['step','pump_command','YV1','YV2','YV3','YV4'],['Bước','Lệnh bơm','YV1','YV2','YV3','YV4']):
    ax.step(t,d[k],where='post',color='#126c85',lw=1.6)
    ax.set_ylabel(l);ax.grid(alpha=.2)
    ax.set_yticks(range(6) if k=='step' else [0,1]);ax.set_xlim(0,105)
axes[-1].set_xlabel('Thời gian đơn điệu của mô hình (s)')
axes[0].set_title('SIM-01 | HAI CHU KỲ LIÊN TỤC — DỮ LIỆU MÔ HÌNH PYTHON',loc='left',fontweight='bold',pad=16)
fig.text(.1,.02,'10.501 mẫu; chu kỳ quét giả lập 10 ms; AUTO tại 0,01 s. Không phải Trace từ PLC/PLCSIM.',fontsize=9)
fig.subplots_adjust(hspace=.22,bottom=.10,top=.91)
save(fig,'SIM_01_hai_chu_ky_mo_hinh')

d=read('TRACE_STOP_RESET_AUTO.csv');t=[m/1000 for m in d['monotonic_ms']]
fig,axes=plt.subplots(6,1,figsize=(12,8),sharex=True)
for ax,k,l in zip(axes,['auto','stop_ok','reset','stop_latched','pump_command','step'],['AUTO','STOP_OK','RESET','Chốt STOP','Lệnh bơm','Bước']):
    ax.step(t,d[k],where='post',color='#126c85',lw=1.6)
    ax.set_ylabel(l);ax.grid(alpha=.2);ax.set_xlim(63,73)
    ax.set_yticks(range(6) if k=='step' else [0,1])
    for x in [65,66,67,68,69,70]:ax.axvline(x,color='#b5bdc3',lw=.6,ls=':')
axes[0].set_title('SIM-02 | STOP → TẮT → RESET → AUTO — DỮ LIỆU MÔ HÌNH PYTHON',loc='left',fontweight='bold',pad=18)
axes[-1].set_xlabel('Thời gian đơn điệu của mô hình (s)')
fig.text(.10,.016,'65 s: STOP; 66 s: nhả STOP; 67 s: TẮT; 68 s: RESET; 69 s: nhả RESET; 70 s: AUTO.\nNhả STOP và nhấn RESET riêng đều không phát lệnh chạy. Chỉ AUTO mới cho chạy lại bước 1.',fontsize=9)
fig.subplots_adjust(hspace=.23,bottom=.12,top=.91)
save(fig,'SIM_02_stop_reset_auto_mo_hinh')
print('Rendered SIM_01 and SIM_02 from delivered CSV files.')
