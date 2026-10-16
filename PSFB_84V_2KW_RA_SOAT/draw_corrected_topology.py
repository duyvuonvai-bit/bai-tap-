from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/psfb_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, Arc
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
P=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})
blue='#173f6b';wire='#176958';orange='#9c4b06'
f,a=plt.subplots(figsize=(16.5,11.7));a.set(xlim=(0,240),ylim=(170,0));a.axis('off')
def text(x,y,s,size=10,ha='left',c=blue):a.text(x,y,s,fontsize=size,va='center',ha=ha,color=c)
def line(x,y,X,Y,color=wire):a.plot([x,X],[y,Y],color=color,lw=1.5)
def dot(x,y):a.add_patch(Circle((x,y),.5,color=wire))
def box(x,y,w,h,s,size=10):
 a.add_patch(Rectangle((x,y),w,h,facecolor='#eef5fa',edgecolor=blue,lw=1.5));text(x+w/2,y+h/2,s,size,'center')
def cap(x,y,label):
 line(x,y-6,x,y-1);line(x-2,y-1,x+2,y-1);line(x-2,y+1,x+2,y+1);line(x,y+1,x,y+6);text(x+3,y,label,8)
def diode(A,K,label):
 A=np.array(A,dtype=float);K=np.array(K,dtype=float);v=(K-A)/np.linalg.norm(K-A);p=np.array([-v[1],v[0]]);m=(K+A)/2
 line(*A,*(m-2*v));line(*(m+2*v),*K)
 a.add_patch(Polygon([m-2*v+2*p,m-2*v-2*p,m+1.8*v],fill=False,edgecolor=wire,lw=1.4))
 line(*(m+1.8*v-2.2*p),*(m+1.8*v+2.2*p));text(*(m-4*p),label,8,'center')
def induct(x,y,label):
 for i in range(4):a.add_patch(Arc((x+1.5+i*3,y),3,5,theta1=180,theta2=360,color=wire,lw=1.5))
 text(x+6,y-6,label,9,'center')
text(5,5,'SƠ ĐỒ KẾT NỐI CÔNG SUẤT ĐÃ SỬA — FULL BRIDGE / PSFB 2 kW',18)
text(5,12,'Bản rà soát ảnh 16/10/2026. Đúng quan hệ kết nối chính; chưa phải PCB hoặc sơ đồ chế tạo đã chốt linh kiện.',10,c=orange)
text(5,21,'A. PFC BOOST: phải có diode boost và nhánh khóa xuống DC_AM',12)
box(5,31,31,25,'L / N → EMI\n+ chỉnh lưu BR1',9)
text(7,60,'PE → vỏ; không nối tắt PE với DC_AM',8)
line(36,35,45,35);induct(45,35,'L_PFC');line(57,35,67,35);dot(67,35)
diode((67,35),(94,35),'D_BOOST');line(94,35,124,35);text(125,35,'BUS+ 390–400 V',9)
line(67,35,67,45);box(62,45,10,12,'Qp',9);line(67,57,67,65)
line(55,51,62,51);text(54,51,'G',8,'right')
line(36,52,40,52);line(40,52,40,65);line(40,65,124,65);text(125,65,'DC_AM',9)
line(103,35,103,44);cap(103,50,'C_BUS');line(103,56,103,65)
text(5,71,'PFC cần bộ điều khiển riêng + đo áp/dòng + bảo vệ. Sơ đồ này chưa chốt mã và giá trị.',9,c=orange)
box(153,29,81,38,'NGUỒN DRIVER KHÔNG ĐƯỢC DÙNG CHUNG MASS\n\nKhóa trên A: +V_A / SW_A\nKhóa trên B: +V_B / SW_B\nHai khóa dưới: +V_L / DC_AM',10)
text(153,72,'Miền logic MCU: 3V3 / GND_THU_CAP',10)
text(5,82,'B. CẦU H — BIẾN ÁP CÁCH LY — CHỈNH LƯU — LỌC — PIN',12)
line(10,91,61,91);line(10,130,61,130);text(10,87,'BUS+',9);text(10,135,'DC_AM',9)
for x,qt,qb,sw in [(22,'Q1','Q2','SW_A'),(53,'Q3','Q4','SW_B')]:
 line(x,91,x,95);box(x-4,95,8,9,qt,9);line(x,104,x,116);box(x-4,116,8,9,qb,9);line(x,125,x,130)
 dot(x,110);line(x,110,x+9,110);text(x+10,110,sw,8)
 line(x-8,99,x-4,99);line(x-8,120,x-4,120)
 text(x-9,99,'G',7,'right');text(x-9,120,'G',7,'right')
box(79,94,20,33,'T1\nCÁCH LY\nNp:Ns\nchưa chốt',9)
line(72,99,79,99);text(71,99,'SW_A',8,'right');line(72,122,79,122);text(71,122,'SW_B',8,'right')
line(99,99,107,99);text(107,96,'SEC_A',8,'right');line(99,122,107,122);text(107,126,'SEC_B',8,'right')
L=(120,111);R=(147,111);plus=(134,92);minus=(134,130)
diode(L,plus,'D1');diode(R,plus,'D2');diode(minus,L,'D3');diode(minus,R,'D4')
for x,y in [L,R,plus,minus]:dot(x,y)
text(119,111,'SEC_A',8,'right');text(148,111,'SEC_B',8)
line(134,92,159,92);induct(159,92,'L_OUT');line(171,92,176,92)
box(176,90,6,4,'',8);text(179,85,'Shunt iL',8,'center');line(182,92,191,92);dot(191,92)
line(191,92,191,104);cap(191,110,'C_OUT');line(191,116,191,130);dot(191,130)
line(191,92,199,92);box(199,90,6,4,'',8);text(202,85,'Shunt pin',8,'center');line(205,92,224,92)
box(214,101,20,19,'Khối nối pin\n+ pin/BMS',9);line(224,92,224,101);line(224,120,224,130);line(134,130,224,130)
text(224,135,'GND_THU_CAP = âm đầu ra',9,'right')
text(5,143,'NHÃN DRIVER ĐÚNG: U10 → GATE_Q1 / GATE_Q2. U11 → GATE_Q3 / GATE_Q4.',11)
text(5,150,'VSSA nhánh A → SW_A; VSSA nhánh B → SW_B; VSSB hai nhánh → DC_AM. Không nối các điểm này vào mass MCU.',9)
text(5,157,'Thiếu để chế tạo: pinout driver đã xác minh, bảo vệ/giữ lỗi, thiết kế từ tính, nguồn lái, snubber, nối pin và PCB/cách điện.',9,c=orange)
text(5,164,'Cầu diode và MOSFET được vẽ tương đương để đọc topology; không suy ra package hoặc số chân hàn từ hình này.',9,c=orange)
f.savefig(P/'SO_DO_KET_NOI_DA_SUA.png',dpi=180,bbox_inches='tight')
f.savefig(P/'SO_DO_KET_NOI_DA_SUA.svg',bbox_inches='tight')
f.savefig(P/'SO_DO_KET_NOI_DA_SUA.pdf',bbox_inches='tight')
print('Exported corrected power topology (review only).')
