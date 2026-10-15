from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ret6_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon, Circle, Arc
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

OUT=Path(__file__).resolve().parent.parent/'HINH_TONG_THE'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'pdf.fonttype':42,'svg.fonttype':'none'})
INK='#18344d';BLUE='#1565a0';GREEN='#19725d';ORANGE='#9e4d00';GRAY='#637381'
FIGS=[]
def page(title,subtitle):
    f,a=plt.subplots(figsize=(16.5,11.7));a.set(xlim=(0,240),ylim=(150,0));a.axis('off')
    a.text(5,5,title,fontsize=20,fontweight='bold',color=INK,va='top')
    a.text(5,14,subtitle,fontsize=10,color=GRAY,va='top')
    a.text(5,146,'THIẾT KẾ NGUYÊN LÝ ĐỂ RÀ SOÁT / THỬ THẤP ÁP — chưa có PCB công suất, Gerber hoặc xác nhận chạy 400 V/2 kW.',
           fontsize=9,color=ORANGE)
    FIGS.append(f);return a
def txt(a,x,y,s,size=11,c=INK,ha='left',weight='normal'):
    a.text(x,y,s,fontsize=size,color=c,ha=ha,va='center',fontweight=weight)
def box(a,x,y,w,h,s,fc='#edf5fb',ec=BLUE,size=11):
    a.add_patch(Rectangle((x,y),w,h,fc=fc,ec=ec,lw=1.5))
    txt(a,x+w/2,y+h/2,s,size,ha='center')
def line(a,x,y,X,Y,c=GREEN,lw=1.7):a.plot([x,X],[y,Y],color=c,lw=lw)
def arrow(a,x,y,X,Y,label=None,c=BLUE):
    a.add_patch(FancyArrowPatch((x,y),(X,Y),arrowstyle='-|>',mutation_scale=14,lw=1.5,color=c))
    if label:txt(a,(x+X)/2,(y+Y)/2-3,label,9,c,ha='center')
def dot(a,x,y):a.add_patch(Circle((x,y),.55,fc=GREEN,ec=GREEN))
def res(a,x,y,label):
    line(a,x-6,y,x-3,y);line(a,x+3,y,x+6,y)
    a.add_patch(Rectangle((x-3,y-1.4),6,2.8,fc='white',ec=GREEN,lw=1.6));txt(a,x,y-4,label,9,ha='center')
def diode(a,A,K,label):
    A=np.array(A,dtype=float);K=np.array(K,dtype=float);v=(K-A)/np.linalg.norm(K-A);p=np.array([-v[1],v[0]]);m=(A+K)/2
    line(a,*A,*(m-2*v));line(a,*(m+2*v),*K)
    a.add_patch(Polygon([m-2*v+2*p,m-2*v-2*p,m+1.8*v],closed=True,fc='white',ec=GREEN,lw=1.5))
    line(a,*(m+1.8*v-2.3*p),*(m+1.8*v+2.3*p))
    txt(a,*(m+5*p),label,9,ha='center')
def cap(a,x,y,label):
    line(a,x,y-7,x,y-1);line(a,x-3,y-1,x+3,y-1);line(a,x-3,y+1,x+3,y+1);line(a,x,y+1,x,y+7)
    txt(a,x+5,y,label,9)

a=page('01 — Toàn bộ hệ thống dùng bo STM32G474RET6 tự thiết kế',
       'Thông số mục tiêu: 220 VAC → bus 400 VDC → 58 V / 34,48 A; pin LiFePO₄ 16S. Vị trí các khối là sơ đồ kết nối, không phải bố trí PCB.')
for x,w,s in [(5,32,'220 VAC\nEMI + bảo vệ'),(47,34,'Chỉnh lưu\nPFC 400 V'),(91,33,'Cầu H\nQ1–Q4'),(134,32,'Biến áp\ncao tần T1'),(176,28,'Cầu diode\nD1–D4'),(214,22,'Lọc LC\n+ pin')]:box(a,x,29,w,22,s)
for x,X in [(37,47),(81,91),(124,134),(166,176),(204,214)]:arrow(a,x,40,X,40)
txt(a,94,57,'SƠ CẤP: tham chiếu DC_AM',10,c=ORANGE)
txt(a,173,57,'THỨ CẤP: GND_THU_CAP',10,c=GREEN)
box(a,5,76,55,28,'Nguồn phụ cách ly\n12 V → 5 V → 3,3 V',fc='#f1f6f0')
box(a,80,76,61,28,'BO ĐIỀU KHIỂN TỰ LÀM\nSTM32G474RET6\nSWD + HRTIM + ADC',size=12)
box(a,167,76,69,28,'BO ĐO LƯỜNG / BẢO VỆ\nÁp ra · dòng L · dòng pin\nNTC · ngắt lỗi',fc='#f1f6f0')
arrow(a,60,90,80,90,'5 V');arrow(a,167,90,141,90,'Analog 3,3 V / lỗi')
arrow(a,224,76,224,51,'đo U, I')
box(a,80,119,61,18,'2 × UCC21520\n4 kênh lái cách ly')
arrow(a,110,104,110,119,'4 PWM + cho phép')
line(a,80,128,72,128,c=BLUE);line(a,72,128,72,67,c=BLUE);line(a,72,67,107,67,c=BLUE);arrow(a,107,67,107,51);txt(a,74,64,'G–S của Q1…Q4',9,c=BLUE)
box(a,167,119,69,18,'3 miền nguồn lái cách ly\n2 nguồn trên + 1 nguồn dưới',fc='#fff4e5',ec=ORANGE)
arrow(a,167,128,141,128,'12 V mỗi miền')
txt(a,5,112,'Giảm chi phí bo điều khiển:',11,weight='bold')
txt(a,5,120,'Không tích hợp ST-LINK, USB/HMI.',10)
txt(a,5,127,'Dùng ST-LINK rời khi nạp.',10)
txt(a,5,134,'0805 + SOIC; khởi động bằng HSI.',10)

a=page('02 — Sơ đồ nguyên lý tầng công suất Full Bridge',
       'Cầu chỉnh lưu vẽ theo diode tương đương; mã diode và phương án tản nhiệt chưa chốt. Đây là sơ đồ nguyên lý, chưa phải sơ đồ lắp ráp.')
line(a,6,25,62,25);line(a,6,78,62,78);txt(a,8,22,'BUS+ 400 V',10);txt(a,8,83,'DC_AM',10)
line(a,6,25,6,44);cap(a,6,51,'C_BUS*');line(a,6,58,6,78)
for x,qtop,qbot,sw in [(24,'Q1','Q2','SW_A'),(56,'Q3','Q4','SW_B')]:
    line(a,x,25,x,31);box(a,x-5,31,10,12,qtop,fc='white',ec=GREEN,size=11);line(a,x,43,x,59)
    box(a,x-5,59,10,12,qbot,fc='white',ec=GREEN,size=11);line(a,x,71,x,78)
    dot(a,x,51);line(a,x,51,x+10,51);txt(a,x+11,51,sw,9)
    line(a,x-11,37,x-5,37);txt(a,x-11,33,'G',8)
    line(a,x-11,65,x-5,65);txt(a,x-11,61,'G',8)
    txt(a,x+7,32,'D',8);txt(a,x+7,42,'S',8);txt(a,x+7,60,'D',8);txt(a,x+7,70,'S',8)
txt(a,20,90,'Q1–Q4: MOSFET 650 V\nDiode thân không vẽ trong hình này.',10)
box(a,84,32,24,38,'T1\nCách ly\nNp:Ns ≈5:1',fc='#f6f0ff',ec='#75518b',size=10)
line(a,75,39,84,39);txt(a,73,39,'SW_A',9,ha='right');line(a,75,63,84,63);txt(a,73,63,'SW_B',9,ha='right')
line(a,108,39,115,39);txt(a,116,39,'AC1',9);line(a,108,63,115,63);txt(a,116,63,'AC2',9)
left=(132,51);right=(160,51);plus=(146,29);minus=(146,73)
diode(a,left,plus,'D1');diode(a,right,plus,'D2');diode(a,minus,left,'D3');diode(a,minus,right,'D4')
for x,y in [left,right,plus,minus]:dot(a,x,y)
txt(a,130,51,'AC1',9,ha='right');txt(a,162,51,'AC2',9)
line(a,146,29,171.5,29)
for i in range(4):a.add_patch(Arc((173+i*3,29),3,6,theta1=180,theta2=360,color=GREEN,lw=1.7))
line(a,183.5,29,187,29);txt(a,177,21,'L1: 100 µH*',9,ha='center')
res(a,193,29,'R_SH1');line(a,199,29,207,29);dot(a,203,29)
res(a,213,29,'R_SH2');line(a,219,29,231,29);txt(a,231,23,'PIN+',10,ha='right')
line(a,203,29,203,44);cap(a,203,51,'C_RA\n≈1.000 µF*');line(a,203,58,203,73)
line(a,146,73,231,73);dot(a,203,73);txt(a,231,79,'PIN− = GND_THU_CAP',10,ha='right')
box(a,220,40,14,21,'PIN\n16S',fc='#f1f6f0',ec=GREEN,size=10);line(a,231,29,231,40);line(a,231,61,231,73)
txt(a,174,88,'R_SH1: đo iL; R_SH2: đo dòng pin.',10)
txt(a,8,102,'NỐI DRIVER ĐÚNG SOURCE',12,weight='bold')
txt(a,8,111,'Q1: LAI_Q1 → G; VSSA → SW_A.       Q2: LAI_Q2 → G; VSSB → DC_AM.',11)
txt(a,8,119,'Q3: LAI_Q3 → G; VSSA → SW_B.       Q4: LAI_Q4 → G; VSSB → DC_AM.',11)
txt(a,8,130,'* T1, L, C_RA là giá trị khởi đầu. C_BUS: tụ bus + tụ cao tần sát cầu H, giá trị chưa chốt. Từ tính, nhiệt và bảo vệ còn phải tính.',10,c=ORANGE)
txt(a,8,137,'Các nhãn SW_A, SW_B, AC1, AC2 cùng tên được nối với nhau. DC_AM và GND_THU_CAP là hai miền cách ly.',10)

a=page('03 — Bo STM32G474RET6 tối thiểu: chân và đầu nối cần dùng',
       'Pin vật lý LQFP64 được đối chiếu ST open pin data; xem sơ đồ KiCad đầy đủ để biết điện trở, tụ và nguồn từng chân.')
box(a,72,31,86,81,'',fc='#edf5fb')
txt(a,115,38,'STM32G474RET6 · LQFP64',15,ha='center',weight='bold')
left=[('PA8 · chân 42','PWM_A_TREN'),('PA9 · chân 43','PWM_A_DUOI'),('PA10 · chân 44','PWM_B_TREN'),('PA11 · chân 45','PWM_B_DUOI'),('PA12 · chân 46','NGAT_LAI / FLT1'),('PB0 · chân 24','CHO_PHEP_CHAY'),('PB1 · chân 25','XOA_LOI — dự phòng')]
right=[('PA0 · chân 12','Đo áp ra'),('PA1 · chân 13','Đo dòng cuộn cảm'),('PA2 · chân 14','Đo dòng pin'),('PC0 · chân 8','NTC 1'),('PC1 · chân 9','NTC 2'),('PC2 · chân 10','NTC 3'),('PA13 / PA14 · 49/50','SWDIO / SWCLK')]
for i,((pin,net),(pinr,netr)) in enumerate(zip(left,right)):
    y=49+i*8.5;line(a,65,y,72,y,c=BLUE);txt(a,74,y,pin,10);txt(a,63,y,net,10,ha='right')
    line(a,158,y,165,y,c=BLUE);txt(a,156,y,pinr,10,ha='right');txt(a,167,y,netr,10)
box(a,5,119,68,19,'5 V đã ổn áp → AP2112K-3.3\n→ 3V3; không cấp 12 V vào LDO',size=10)
box(a,85,119,68,19,'ST-LINK rời qua đầu SWD\n3V3 ở đầu SWD là VTREF',size=10)
box(a,165,119,70,19,'Reset chân 7 · Boot chân 61\nNguồn analog / VREF lọc riêng',size=10)
txt(a,5,23,'HRTIM A1/A2/B1/B2 và FLT1: AF13. Cặp cùng nhánh phải liên động; thuật toán PWM phải cân bằng volt–giây biến áp.',10)

names=['01_TONG_THE_BO_SAC_RET6','02_MACH_DONG_LUC_FULL_BRIDGE','03_CHAN_BO_DIEU_KHIEN_RET6']
with PdfPages(OUT/'SO_DO_TONG_THE_VA_CONG_SUAT.pdf') as pdf:
    for f,name in zip(FIGS,names):
        f.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight')
        f.savefig(OUT/(name+'.svg'),bbox_inches='tight')
        pdf.savefig(f,bbox_inches='tight')
        plt.close(f)
print('Created 3 engineering overview sheets.')
