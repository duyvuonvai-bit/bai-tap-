#!/usr/bin/env python3
"""Render the agreed semantic LAD specification. This is not a TIA project export."""
from pathlib import Path
import json, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
from matplotlib.backends.backend_pdf import PdfPages

BASE=Path(__file__).resolve().parent.parent
OUT=BASE/'LAD_DE_XUAT'
SPEC=json.loads((BASE/'KIEM_THU/network_spec_26.json').read_text())
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
INK='#183b53'; BLUE='#1467a0'; GRAY='#5d6c79'; LIGHT='#eaf2f7'
W=2000; H=1320

def c(name,nc=False): return ('c',name,nc)
def cmp(name,op,value,typ='Int'): return ('cmp',name,op,str(value),typ)
def AND(*items): return ('and',list(items))
def OR(*items): return ('or',list(items))
def dims(n):
    if n is None: return (100,60)
    if n[0]=='c': return (max(175,len(n[1])*8+25),70)
    if n[0]=='cmp': return (280,105)
    ds=[dims(i) for i in n[1]]
    if n[0]=='and': return (sum(d[0] for d in ds)+15*(len(ds)-1),max(d[1] for d in ds))
    return (max(d[0] for d in ds)+90,sum(d[1] for d in ds)+15*(len(ds)-1))

class Page:
    def __init__(self,label,title,note=''):
        self.fig,self.ax=plt.subplots(figsize=(16.54,10.92),dpi=125)
        self.fig.subplots_adjust(0,0,1,1); self.ax.set_xlim(0,W); self.ax.set_ylim(H,0);self.ax.axis('off')
        self.ax.add_patch(Rectangle((0,0),W,110,facecolor=LIGHT,edgecolor='none'))
        self.text(55,39,label,size=12,color=BLUE,weight='bold')
        self.text(55,81,title,size=20,weight='bold')
        self.note=note
        self.text(55,H-66,'THIẾT KẾ LAD ĐỀ XUẤT • S7-1200 / TIA V16 • CHƯA COMPILE / CHƯA CHẠY PLCSIM',size=10,color=GRAY)
        self.text(55,H-37,'Alias trong hình: tra BANG_ALIAS.md. DB trạng thái: "daiphunnuoc". Thực hiện network theo đúng thứ tự.',size=9,color=GRAY)
        self.line(50,H-91,1950,H-91,color='#b9cad6',lw=1)
    def line(self,x1,y1,x2,y2,color=INK,lw=2): self.ax.plot([x1,x2],[y1,y2],color=color,lw=lw,solid_capstyle='butt')
    def text(self,x,y,s,size=11,color=INK,ha='left',va='center',weight=None):
        self.ax.text(x,y,s,fontsize=size,color=color,ha=ha,va=va,fontweight=weight)
    def contact(self,x,y,w,name,nc=False):
        mid=x+w/2; self.line(x,y,mid-13,y);self.line(mid+13,y,x+w,y)
        self.line(mid-13,y-20,mid-13,y+20);self.line(mid+13,y-20,mid+13,y+20)
        if nc:self.line(mid-20,y+28,mid+20,y-28,lw=2)
        self.text(mid,y-40,name,size=11,color=BLUE,ha='center')
    def compare(self,x,y,w,n):
        _,name,op,value,typ=n; boxw=min(250,w-20); bx=x+(w-boxw)/2
        self.line(x,y,bx,y);self.line(bx+boxw,y,x+w,y)
        self.ax.add_patch(Rectangle((bx,y-46),boxw,92,facecolor=LIGHT,edgecolor='#a9bdcc',lw=1.2))
        self.text(bx+boxw/2,y-25,f'{op}  {typ}',size=12,ha='center',weight='bold')
        self.text(bx+10,y+1,'IN1',size=8,color=GRAY);self.text(bx+50,y+1,name,size=9,color=BLUE)
        self.text(bx+10,y+25,'IN2',size=8,color=GRAY);self.text(bx+50,y+25,value,size=10,color=BLUE)
    def node(self,n,x,y,w):
        if n is None:self.line(x,y,x+w,y);return
        if n[0]=='c':self.contact(x,y,w,n[1],n[2]);return
        if n[0]=='cmp':self.compare(x,y,w,n);return
        if n[0]=='and':
            weights=[dims(i)[0] for i in n[1]]; total=sum(weights); cur=x
            for item,weight in zip(n[1],weights):
                iw=w*weight/total;self.node(item,cur,y,iw);cur+=iw
            return
        children=n[1]; heights=[dims(i)[1] for i in children]; total=sum(heights)+15*(len(children)-1)
        yy=y-total/2; centers=[]
        for child,hh in zip(children,heights):
            center=yy+hh/2;centers.append(center);self.node(child,x+35,center,w-70);yy+=hh+15
        self.line(x,y,x+20,y);self.line(x+w-20,y,x+w,y)
        self.line(x+20,centers[0],x+20,centers[-1]);self.line(x+w-20,centers[0],x+w-20,centers[-1])
        for center in centers:
            self.line(x+20,center,x+35,center);self.line(x+w-35,center,x+w-20,center)
    def coil(self,y,name,mode='',x=1780):
        self.ax.add_patch(Arc((x-5,y),34,56,theta1=90,theta2=270,color=INK,lw=2))
        self.ax.add_patch(Arc((x+25,y),34,56,theta1=-90,theta2=90,color=INK,lw=2))
        self.line(x+42,y,1900,y); self.text(x+12,y-44,name,size=12,color=BLUE,ha='center')
        if mode:self.text(x+12,y,mode,size=14,ha='center',weight='bold')
    def rung(self,y,n,out,mode=''):
        self.line(65,y-35,65,y+35,lw=3);self.node(n,65,y,1693);self.line(1758,y,1760,y);self.coil(y,out,mode)
    def move(self,y,n,value,out):
        self.line(65,y-35,65,y+35,lw=3);self.node(n,65,y,1335)
        bx=1400;by=y-60;bw=480;self.ax.add_patch(Rectangle((bx,by),bw,145,facecolor=LIGHT,edgecolor='#a9bdcc',lw=1.2))
        self.text(bx+bw/2,by+25,'MOVE',size=15,ha='center',weight='bold')
        self.text(bx+15,y,'EN',size=10);self.text(bx+bw-15,y,'ENO',size=10,ha='right');self.line(bx+bw,y,1910,y)
        self.text(bx+15,y+32,'IN',size=10);self.text(bx+105,y+32,str(value),size=12,color=BLUE)
        self.text(bx+15,y+61,'OUT1',size=10);self.text(bx+105,y+61,out,size=12,color=BLUE)
    def sr(self,y,name,s,r):
        bx=1480;by=y-80;bw=350;bh=210
        self.line(65,y-35,65,y+115,lw=3)
        self.node(s,65,y,bx-65);self.node(r,65,y+95,bx-65)
        self.ax.add_patch(Rectangle((bx,by),bw,bh,facecolor=LIGHT,edgecolor='#a9bdcc',lw=1.2))
        self.text(bx+bw/2,by+29,'SR  (R1 ưu tiên)',size=15,ha='center',weight='bold')
        self.text(bx+bw/2,by-27,name,size=12,color=BLUE,ha='center')
        self.text(bx+15,y,'S',size=12);self.text(bx+15,y+95,'R1',size=12)
        self.text(bx+bw-15,y+35,'Q',size=12,ha='right');self.line(bx+bw,y+35,1930,y+35)
    def note_at(self,y):
        for k,line in enumerate(textwrap.wrap(self.note,width=155)):
            self.text(65,y+k*28,line,size=10,color=GRAY)
    def finish(self): self.note_at(H-172)
    def save(self,path,pdf):
        self.finish();self.fig.savefig(path.with_suffix('.svg'));self.fig.savefig(path.with_suffix('.png'),dpi=135)
        pdf.savefig(self.fig);plt.close(self.fig)

def block_call(p,y,kind,instance,inputs,outputs):
    """Unconditional FB call: EN is a separate wired rail input."""
    bx=760;bw=570;top=y-50;bh=max(190,80+max(len(inputs),len(outputs))*60)
    p.line(65,y-35,65,y+35,lw=3);p.line(65,y,bx,y)
    p.ax.add_patch(Rectangle((bx,top),bw,bh,facecolor=LIGHT,edgecolor='#a9bdcc',lw=1.2))
    p.text(bx+bw/2,top+24,kind,size=16,weight='bold',ha='center')
    if instance:p.text(bx+bw/2,top-25,instance,size=12,color=BLUE,ha='center')
    p.text(bx+18,y,'EN',size=10);p.text(bx+bw-18,y,'ENO',size=10,ha='right')
    p.text(170,y-27,'GỌI MỖI VÒNG QUÉT',size=10,color=GRAY)
    for i,(pin,value) in enumerate(inputs):
        yy=y+55+i*55;p.text(bx+18,yy,pin,size=11);p.line(bx-120,yy,bx,yy);p.text(bx-135,yy,value,size=11,color=BLUE,ha='right')
    for i,(pin,value) in enumerate(outputs):
        yy=y+55+i*55;p.text(bx+bw-18,yy,pin,size=11,ha='right');p.line(bx+bw,yy,bx+bw+70,yy);p.text(bx+bw+85,yy,value,size=11,color=BLUE)

def timer(p,k):
    y=400;bx=1260;bw=420
    p.line(65,y-35,65,y+35,lw=3);p.node(AND(c('Run'),cmp('CurrentStep','==',k)),65,y,bx-65)
    p.ax.add_patch(Rectangle((bx,y-90),bw,250,facecolor=LIGHT,edgecolor='#a9bdcc',lw=1.2))
    p.text(bx+bw/2,y-130,f'Timer{k}  •  instance riêng',size=13,color=BLUE,ha='center')
    p.text(bx+bw/2,y-52,'TON',size=18,weight='bold',ha='center')
    p.text(bx+15,y,'IN',size=12);p.text(bx+bw-15,y,'Q',size=12,ha='right')
    p.line(bx+bw,y,bx+bw+70,y);p.text(bx+bw+85,y,f'Timer{k}.Q',size=12,color=BLUE)
    p.text(bx+15,y+75,'PT',size=12);p.line(bx-170,y+75,bx,y+75);p.text(bx-185,y+75,'T#10s',size=12,color=BLUE,ha='right')
    p.text(bx+bw-15,y+75,'ET',size=12,ha='right');p.text(bx+bw+30,y+75,'(không nối)',size=10,color=GRAY)
    p.text(70,210,'TON luôn được thực hiện tại network này; biểu thức bên trái chỉ cấp IN.',size=13,color=GRAY)
    p.text(70,247,'Khi IN = FALSE, timer reset ET/Q. Không đặt lệnh TON trong nhánh bỏ qua thực thi.',size=12,color=GRAY)
    p.move(790,AND(c('Run'),cmp('CurrentStep','==',k),c(f'Timer{k}.Q')),k%5+1,'NextStep')

def build(spec):
    n=spec['number'];p=Page(f'NETWORK {n:02d} / 26',spec['title_vi'],spec['notes_vi'])
    if n==1:
        p.rung(180,c('InitPending'),'FirstScan')
        for i,out in enumerate(['FaultLatched','StopLatched','OffSeen','AutoArmed']):p.rung(290+i*130,c('FirstScan'),out,'R')
        p.move(860,c('FirstScan'),'0','CurrentStep');p.move(1050,c('FirstScan'),'0','NextStep')
    elif n==2:block_call(p,450,'RD_LOC_T','',[],[('RET_VAL','RTC_Status'),('OUT','PLC_LocalTime')])
    elif n==3:p.rung(570,AND(OR(cmp('RTC_Status','==',0),cmp('RTC_Status','==',1)),cmp('PLC_LocalTime.HOUR','<=',23,'USInt'),cmp('PLC_LocalTime.MINUTE','<=',59,'USInt'),cmp('PLC_LocalTime.SECOND','<=',59,'USInt')),'RTC_OK')
    elif n==4:p.rung(570,AND(c('RTC_OK'),cmp('PLC_LocalTime.HOUR','>=',6,'USInt'),cmp('PLC_LocalTime.HOUR','<',8,'USInt')),'Morning')
    elif n==5:p.rung(570,AND(c('RTC_OK'),OR(AND(cmp('PLC_LocalTime.HOUR','>=',17,'USInt'),cmp('PLC_LocalTime.HOUR','<',20,'USInt')),AND(cmp('PLC_LocalTime.HOUR','==',20,'USInt'),cmp('PLC_LocalTime.MINUTE','<',30,'USInt')))),'Evening')
    elif n==6:p.rung(570,OR(c('Morning'),c('Evening')),'InSchedule')
    elif n==7:p.rung(570,AND(c('WaterOK'),c('EStopOK'),c('OverloadOK'),c('StopOK')),'Safe')
    elif n==8:
        p.rung(300,OR(cmp('CurrentStep','<',0),cmp('CurrentStep','>',5)),'BadStep')
        p.rung(800,OR(c('WaterOK',True),c('EStopOK',True),c('OverloadOK',True),AND(c('AutoSelected'),c('RTC_OK',True)),c('BadStep')),'FaultNow')
    elif n==9:
        block_call(p,250,'R_TRIG','ResetTrigger',[('CLK','ResetButton')],[('Q','ResetTrigger.Q')])
        p.rung(510,AND(c('ResetTrigger.Q'),c('FirstScan',True)),'ResetEdge')
        block_call(p,720,'R_TRIG','AutoTrigger',[('CLK','AutoSelected')],[('Q','AutoTrigger.Q')])
        p.rung(980,AND(c('AutoTrigger.Q'),c('FirstScan',True)),'AutoEdge')
    elif n==10:p.rung(570,AND(c('ResetEdge'),c('AutoSelected',True),c('Safe'),c('RTC_OK'),c('BadStep',True),c('FirstScan',True)),'Ack')
    elif n==11:p.sr(500,'FaultLatched',c('FaultNow'),c('Ack'))
    elif n==12:p.sr(500,'StopLatched',c('StopOK',True),c('Ack'))
    elif n==13:p.rung(570,c('AutoSelected',True),'OffSeen','S')
    elif n==14:
        p.rung(455,OR(c('AutoSelected',True),c('Safe',True),c('RTC_OK',True),c('FaultLatched'),c('StopLatched'),c('FirstScan')),'CancelAuto')
        p.sr(940,'AutoArmed',AND(c('AutoEdge'),c('OffSeen'),c('Safe'),c('RTC_OK'),c('FaultLatched',True),c('StopLatched',True),c('FirstScan',True)),c('CancelAuto'))
    elif n==15:p.rung(570,AND(c('AutoArmed'),c('AutoSelected'),c('InSchedule'),c('Safe'),c('FaultLatched',True),c('StopLatched',True),c('FirstScan',True)),'Run')
    elif n==16:
        p.move(310,None,'CurrentStep','NextStep');p.move(600,c('Run',True),'0','NextStep');p.move(890,AND(c('Run'),cmp('CurrentStep','==',0)),'1','NextStep')
    elif 17<=n<=21:timer(p,n-16)
    elif n==22:p.move(550,None,'NextStep','CurrentStep')
    elif n==23:p.rung(570,AND(c('Run'),cmp('CurrentStep','>=',1),cmp('CurrentStep','<=',5)),'OutputEnable')
    elif n==24:
        p.rung(210,c('OutputEnable'),'Pump / Q0.0')
        p.rung(410,AND(c('OutputEnable'),cmp('CurrentStep','<=',4)),'Valve1 / Q0.1')
        p.rung(610,AND(c('OutputEnable'),cmp('CurrentStep','>=',2)),'Valve2 / Q0.2')
        p.rung(810,AND(c('OutputEnable'),cmp('CurrentStep','>=',3),cmp('CurrentStep','<=',4)),'Valve3 / Q0.3')
        p.rung(1010,AND(c('OutputEnable'),cmp('CurrentStep','>=',4)),'Valve4 / Q0.4')
    elif n==25:p.rung(570,c('FaultLatched'),'Alarm / Q0.5')
    elif n==26:p.rung(570,None,'InitPending','R')
    return p

with PdfPages(OUT/'LAD_DE_XUAT_26_NETWORK_VA_OB100.pdf') as pdf:
    p=Page('STARTUP OB100','Đặt cờ khởi tạo khi CPU vào RUN','OB100 chỉ đặt InitPending. NW01 chụp FirstScan và khởi tạo; NW26 mới xóa InitPending. Không Retain các biến điều khiển và timer.')
    p.rung(570,None,'InitPending','S');p.save(OUT/'OB100_KHOI_TAO',pdf)
    for spec in SPEC['networks']:build(spec).save(OUT/f"Network_{spec['number']:02d}",pdf)
print('Generated 27 PNG, 27 SVG and 27-page PDF at',OUT)
