from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent.parent/'DRIVER_DO_LUONG'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','pdf.fonttype':42})
INK='#17324d'; WIRE='#1b6858'; WARN='#9a4f04'; BLUE='#155c97'; LIGHT='#f3f8fc'
figs=[]
def page(title,sub):
 f,a=plt.subplots(figsize=(16.5,11.7));a.set(xlim=(0,170),ylim=(120,0));a.axis('off')
 a.text(4,3,title,fontsize=20,weight='bold',color=INK,va='top')
 a.text(4,9,sub,fontsize=10,color=INK,va='top')
 a.text(4,118,'RET6 / 2 kW — SƠ BỘ: còn mục CHƯA CHỐT; chưa có PCB, chưa thử phần cứng, chưa dùng cấp bus 400 V.',fontsize=9,color=WARN)
 figs.append(f);return a

def line(a,x1,y1,x2,y2,c=WIRE,lw=1.5,ls='-'):a.plot([x1,x2],[y1,y2],c=c,lw=lw,ls=ls)
def text(a,x,y,s,size=10,c=INK,ha='left',va='center',weight='normal'):a.text(x,y,s,fontsize=size,color=c,ha=ha,va=va,weight=weight)
def dot(a,x,y):a.add_patch(Circle((x,y),.42,color=WIRE))
def resistor(a,x,y,h=True,label=None):
 if h:
  line(a,x-5,y,x-3,y);line(a,x+3,y,x+5,y);a.add_patch(Rectangle((x-3,y-1.2),6,2.4,fc='white',ec=WIRE,lw=1.4))
  if label:text(a,x,y-3.3,label,8,ha='center')
 else:
  line(a,x,y-5,x,y-3);line(a,x,y+3,x,y+5);a.add_patch(Rectangle((x-1.2,y-3),2.4,6,fc='white',ec=WIRE,lw=1.4))
  if label:text(a,x+3,y,label,8)
def cap(a,x,y,label):
 line(a,x,y-5,x,y-1);line(a,x-2,y-1,x+2,y-1);line(a,x-2,y+1,x+2,y+1);line(a,x,y+1,x,y+5);text(a,x+3,y,label,8)
def gnd(a,x,y,label='GND_THU_CAP'):
 line(a,x,y,x,y+1);line(a,x-2,y+1,x+2,y+1);line(a,x-1.4,y+2,x+1.4,y+2);line(a,x-.7,y+3,x+.7,y+3);text(a,x,y+5,label,8,ha='center')
def box(a,x,y,w,h,label=None,c=INK,fc=LIGHT,ls='-'):
 a.add_patch(Rectangle((x,y),w,h,fc=fc,ec=c,lw=1.4,ls=ls))
 if label:text(a,x+w/2,y+h/2,label,10,ha='center')

# D1: input/output naming is identical to control-board interface J2.
a=page('D1 — Hai driver cách ly UCC21520DW','U10 lái Q1/Q2 của nhánh A; U11 lái Q3/Q4 của nhánh B. Phía logic cùng GND_THU_CAP với MCU.')
text(a,4,16,'Đầu vào mỗi IN: 0 Ω dự phòng trên bo driver + kéo xuống 10 kΩ tại IC. Bo MCU đã có 33 Ω nối tiếp.',10)
for idx,y,leg in [(1,23,'A'),(2,66,'B')]:
 x=73;w=43;h=34
 box(a,x,y,w,h);text(a,x+w/2,y+3,f'U{idx+9} · UCC21520DW',11,ha='center',weight='bold')
 pins=[(y+9,'1 INA',f'PWM_{leg}_TREN_RA'),(y+14,'2 INB',f'PWM_{leg}_DUOI_RA'),(y+19,'5 DIS','NGAT_LAI'),(y+24,'6 DT',f'R_DT{idx} → GND_THU_CAP'),(y+29,'4 GND','GND_THU_CAP')]
 for yy,p,n in pins:
  line(a,63,yy,x,yy);text(a,x+1,yy,p,9);text(a,61,yy,n,10,ha='right')
 for yy,p,n in [(y+8,'16 VDDA',f'+12V_{leg}'),(y+13,'15 OUTA',f'LAI_Q{1 if idx==1 else 3}'),(y+18,'14 VSSA',f'SW_{leg}'),(y+23,'11 VDDB','+12V_DUOI'),(y+28,'10 OUTB',f'LAI_Q{2 if idx==1 else 4}'),(y+33,'9 VSSB','DC_AM')]:
  line(a,x+w,yy,126,yy);text(a,x+w-1,yy,p,9,ha='right');text(a,128,yy,n,10)
 text(a,4,y+37,f'U{idx+9}: VCCI chân 3 → 3V3. DT và chân 8 chưa chốt; xem ghi chú bên dưới.',9,c=WARN)
text(a,4,107,'Mỗi cặp nguồn–mass của IC: 100 nF // 1 µF đặt sát chân. Ba miền nguồn lái: +12V_A/SW_A, +12V_B/SW_B, +12V_DUOI/DC_AM.',9)
text(a,4,112,'CHƯA CHỐT: pin 8 và R_DT phải kiểm tra bằng datasheet đúng mã/revision. Không suy ra dead-time từ thư viện KiCad.',9,c=WARN)

# D2: exact net connections without implying a fault latch exists.
a=page('D2 — Cổng MOSFET và khóa driver mặc định','Các giá trị R_G / diode kẹp là giá trị khởi đầu, cần đo dạng sóng cổng và kiểm tra theo MOSFET thực tế.')
text(a,5,18,'MẠCH CỔNG LẶP LẠI CHO Q1…Q4',12,weight='bold')
text(a,5,30,'OUTA / OUTB',10);line(a,26,30,35,30);resistor(a,40,30,label='R_G = 10 Ω, 1206');line(a,45,30,83,30);dot(a,58,30);dot(a,77,30);text(a,85,30,'G — MOSFET',12)
line(a,58,30,58,36);resistor(a,58,41,h=False,label='10 kΩ');line(a,58,46,58,53)
line(a,77,30,77,39);a.add_patch(Polygon([(75,44),(79,44),(77,39)],closed=True,fill=False,edgecolor=WIRE,lw=1.5));line(a,75,39,79,39);line(a,75,39,75,38);line(a,79,39,79,40);line(a,77,44,77,53);text(a,83,41,'BZT52C15\nK về G, A về S',9)
line(a,26,53,99,53);dot(a,58,53);dot(a,77,53);text(a,5,53,'VSSA / VSSB',10);text(a,102,53,'S — cùng source MOSFET',10)
text(a,5,60,'Đường OUT → R_G → G → S → VSS phải ngắn. SW_A, SW_B, DC_AM không nối với GND_THU_CAP.',10,c=WARN)
text(a,5,70,'NGAT_LAI = 1: TẮT CẢ HAI DRIVER / BÁO FAULT HRTIM',12,weight='bold')
text(a,50,76,'3V3',10,ha='center');line(a,50,78,50,80);resistor(a,50,85,h=False,label='4,7 kΩ');line(a,50,90,50,92);dot(a,50,92);line(a,50,92,78,92);text(a,81,92,'NGAT_LAI → DIS hai IC + J2.9 / PA12',10)
line(a,50,92,50,95);box(a,45,95,10,5,'Q_EN',fc='white');line(a,50,100,50,102);box(a,45,102,10,5,'Q_OK',fc='white');line(a,50,107,50,110);text(a,50,113,'GND_THU_CAP',8,ha='center')
line(a,55,97.5,78,97.5);text(a,81,97.5,'G1 = CHO_PHEP_CHAY (PB0 / J2.7)',9)
line(a,55,104.5,78,104.5);text(a,81,104.5,'G2 = BAO_VE_OK_3V3; mặc định 0',9)
box(a,5,80,34,29,fc='white');text(a,7,84,'Hai 2N7002 nối tiếp:',9,weight='bold');text(a,7,90,'D1=NGAT_LAI; S1=D2',8.5);text(a,7,96,'S2=GND_THU_CAP',8.5);text(a,7,102,'Mỗi G: 100 kΩ xuống GND',8)
text(a,81,110,'CHƯA CÓ mạch tạo BAO_VE_OK_3V3,',9,c=WARN);text(a,81,114,'chốt lỗi, ngưỡng OCP/OVP. XOA_LOI dự phòng.',9,c=WARN)

# D3 current channels.
a=page('D3 — Hai kênh đo dòng INA240A1D','Hai shunt, mỗi shunt 4 đầu Kelvin. Đường công suất khoảng 34,5 A không đi qua giắc tín hiệu J3.')
for y,idx,label,out,jpin in [(21,1,'Dòng cuộn cảm: sau L, trước nút tụ','DONG_L_DA_DO',2),(67,2,'Dòng pin: sau nút tụ, trước pin','DONG_PIN_DA_DO',3)]:
 text(a,5,y-4,f'Kênh {idx}: {label}',12,weight='bold')
 text(a,5,y+4,'Phía nguồn',10);line(a,23,y+4,40,y+4);resistor(a,45,y+4,label=f'R_SH{idx} = 1 mΩ / 5 W');line(a,50,y+4,75,y+4);text(a,77,y+4,'Phía tải',10)
 dot(a,37,y+4);dot(a,53,y+4);line(a,37,y+4,37,y+17);line(a,53,y+4,53,y+22);line(a,37,y+17,76,y+17);line(a,53,y+22,76,y+22)
 x=76;box(a,x,y+9,39,25);text(a,x+19.5,y+12,f'U{idx+19} INA240A1D',10,ha='center',weight='bold');text(a,x+1,y+17,'8 IN+',9);text(a,x+1,y+22,'1 IN−',9);text(a,x+38,y+20,'5 OUT',9,ha='right')
 line(a,115,y+20,124,y+20);resistor(a,129,y+20,label='100 Ω');line(a,134,y+20,164,y+20);text(a,162,y+14,out,9,ha='right');text(a,164,y+23,f'→ J3.{jpin}',8,ha='right');dot(a,142,y+20);line(a,142,y+20,142,y+22);cap(a,142,y+27,'2,2 nF');gnd(a,142,y+32)
 text(a,5,y+31,'Chân 6 VS → 3V3; chân 2 và 4 → GND_THU_CAP.',9);text(a,5,y+36,'Chân 7 REF1 → 3V3; chân 3 REF2 → GND_THU_CAP.',9)
 text(a,77,y+39,'VS–GND: 100 nF // 1 µF sát IC.',9)
text(a,5,111,'V_ADC = V_3V3 / 2 + 0,020 × I. Với 3,300 V: 0 A → 1,650 V; 34,5 A → 2,340 V.',10)
text(a,5,115,'IN± ở miền điện áp ra, không phải bus 400 V. Cần kiểm tra power-off/overvoltage của IC và ADC theo datasheet.',9,c=WARN)

# D4 voltage sensing includes a visible unimplemented interruption, not a working battery-to-ADC circuit.
a=page('D4 — Đo điện áp ra: còn thiếu bảo vệ khi mất nguồn MCU','Mạch chia áp chỉ là phần tính toán. Không nối pin trực tiếp vào bộ chia khi chưa giải quyết cấp ngược vào ADC.')
text(a,5,28,'V_RA+',10);line(a,17,28,21,28)
box(a,21,19,40,24,c=WARN,fc='#fff6e8',ls='--');text(a,41,24,'KHỐI CHƯA THIẾT KẾ',9,c=WARN,ha='center',weight='bold');text(a,41,30,'Ngắt đo khi mất 3V3 /',9,c=WARN,ha='center');text(a,41,36,'power-off protection',9,c=WARN,ha='center')
line(a,61,28,69,28,ls='--');resistor(a,74,28,label='R_V1: 110 kΩ');line(a,79,28,87,28);resistor(a,92,28,label='R_V2: 110 kΩ');line(a,97,28,111,28);dot(a,105,28);line(a,105,28,105,39);resistor(a,105,44,h=False,label='10 kΩ');gnd(a,105,49)
resistor(a,116,28,label='100 Ω');line(a,121,28,166,28);text(a,166,22,'AP_RA_DA_CHIA',10,ha='right');text(a,166,32,'→ J3.1',9,ha='right');dot(a,139,28);line(a,139,28,139,38);cap(a,139,43,'10 nF');gnd(a,139,48)
text(a,5,60,'Không có linh kiện thay thế khối nét đứt trong BOM hiện tại. Cần phần tử chịu điện áp pin và chặn cấp ngược đã xác minh.',9,c=WARN)
text(a,5,66,'Bộ chia phía sau khối bảo vệ: V_ADC = V_RA / 23. 58 V → 2,522 V; 70 V → 3,043 V.',11,weight='bold')
text(a,5,72,'R bộ chia 0,1%, 0805. Trở kháng nguồn ≈9,6 kΩ; ADC cần sampling time phù hợp. Không dùng bộ chia này đo 400 V.',9)
rows=[['Miền','Nguồn','Điểm tham chiếu','Cách ly'],['MCU / đo lường','3V3','GND_THU_CAP = V_RA−','Không nối với DC_AM'],['Khóa trên A','+12V_A','SW_A = source Q1','Nguồn nổi riêng'],['Khóa trên B','+12V_B','SW_B = source Q3','Nguồn nổi riêng'],['Hai khóa dưới','+12V_DUOI','DC_AM = source Q2/Q4','Cách ly GND_THU_CAP']]
tab=a.table(cellText=rows,cellLoc='left',colWidths=[.18,.15,.31,.31],bbox=[.03,.075,.94,.25]);tab.auto_set_font_size(False);tab.set_fontsize(9)
for (r,c),cell in tab.get_celld().items():
 cell.set_edgecolor('#adc0cd');cell.set_facecolor('#e5eff6' if r==0 else 'white')
 if r==0:cell.set_text_props(weight='bold')
text(a,5,114,'3 nguồn lái phải đáp ứng cách điện, CMTI, điện dung ký sinh và công suất nạp cổng; chưa chọn mã module.',9,c=WARN)

# D5 low-voltage temperature divider, added without claiming firmware diagnostics.
a=page('D5 — Ba kênh NTC cho tản nhiệt, biến áp và cuộn cảm','Ví dụ cảm biến NTC 10 kΩ tại 25 °C, B25/85 = 3950 K. Xác minh thông số của cảm biến thực tế trước hiệu chuẩn.')
for i,x in enumerate([28,83,138],1):
 text(a,x,21,f'KÊNH NHIỆT {i}',12,ha='center',weight='bold');text(a,x,28,'3V3',10,ha='center');line(a,x,30,x,35);resistor(a,x,40,h=False,label='10 kΩ, 1%');line(a,x,45,x,52);dot(a,x,52);line(a,x,52,x+19,52);text(a,x+19,48,f'NHIET_{i}_DA_DO',9,ha='right');text(a,x+19,56,f'→ J3.{i+3}',9,ha='right');line(a,x,52,x,62);resistor(a,x,67,h=False,label='NTC 10 kΩ');line(a,x-3,70,x+3,64);line(a,x,72,x,78);gnd(a,x,78)
text(a,5,92,'V_ADC = 3V3 × R_NTC / (10 kΩ + R_NTC). Tăng nhiệt độ → điện trở NTC giảm → điện áp ADC giảm.',11)
text(a,5,98,'Tại 25 °C: khoảng 1,65 V. Đứt dây NTC: gần 3,3 V; chập NTC: gần 0 V. Đây là chẩn đoán cần lập trình thêm.',10)
text(a,5,104,'Giắc J3 đã có RC 100 Ω / 1 nF trên bo MCU. Không nhân đôi các linh kiện này khi đọc hai sơ đồ.',10)
text(a,5,110,'Cảm biến / gá lắp phải cách điện với phần mang điện; ngưỡng nhiệt, lọc và xử lý lỗi chưa triển khai trong firmware.',10,c=WARN)

names=['D1_DRIVER_HAI_NHANH','D2_CONG_VA_KHOA_LAI','D3_DO_DONG','D4_DO_AP_MIEN_NGUON','D5_DO_NHIET_NTC']
with PdfPages(P/'SO_DO_DRIVER_VA_DO_LUONG.pdf') as pdf:
 for f,n in zip(figs,names):
  f.savefig(P/(n+'.svg'),bbox_inches='tight');f.savefig(P/(n+'.png'),dpi=160,bbox_inches='tight');pdf.savefig(f,bbox_inches='tight')
print('Created',len(figs),'pages')
