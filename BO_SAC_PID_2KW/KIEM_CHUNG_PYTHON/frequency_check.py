from design_model import *
from itertools import product

def matrices(p,fi,fv):
    Ts=p['Ts'];L,C,r,R=p['L'],p['C'],p['r'],p['R']
    A=np.array([[-r/L,-1/L],[1/C,-1/(R*C)]])
    B=np.array([[1/L],[0.]])
    z=np.zeros((3,3));z[:2,:2]=A;z[:2,2:]=B
    zz=expm(z*Ts);ap=zz[:2,:2];bp=zz[:2,2]
    ai=np.exp(-2*np.pi*p['fi_filter']*Ts);av=np.exp(-2*np.pi*p['fv_filter']*Ts)
    ci=np.array([1-ai,0,ai,0,0.]);cv=np.array([0,1-av,0,av,0.])
    a=np.zeros((5,5));b=np.zeros(5)
    a[:2,:2]=ap;a[:2,4]=bp;a[2,:]=ci;a[3,:]=cv;a[4,:]=cv;b[4]=1
    kpi,kii,kpv,kiv=gains(fi,fv)
    ac=np.zeros((6,6));bc=np.zeros(6)
    ac[:5,:5]=a;ac[4,:5]-=kpi*ci;ac[4,5]=1;bc[4]=kpi
    ac[5,:5]=-kii*Ts*ci;ac[5,5]=1;bc[5]=kii*Ts
    cc=np.r_[cv,0.]
    af=np.zeros((7,7));af[:6,:6]=ac-np.outer(bc,kpv*cc);af[:6,6]=bc
    af[6,:6]=-kiv*Ts*cc;af[6,6]=1
    return a,b,ci,ac,bc,cc,af

def response(a,b,c,z):
    return np.array([c@np.linalg.solve(zz*np.eye(a.shape[0])-a,b) for zz in z])

def margin(f,l):
    mag=20*np.log10(np.abs(l));phase=np.unwrap(np.angle(l))*180/np.pi
    cross=np.flatnonzero((mag[:-1]>=0)&(mag[1:]<0));pms=[]
    for k in cross:
        r=-mag[k]/(mag[k+1]-mag[k]);lf=np.log(f[k])+r*(np.log(f[k+1])-np.log(f[k]))
        ph=phase[k]+r*(phase[k+1]-phase[k]);pms.append((180+ph,np.exp(lf)))
    pc=np.flatnonzero((phase[:-1]>-180)&(phase[1:]<=-180));gms=[]
    for k in pc:
        r=(-180-phase[k])/(phase[k+1]-phase[k]);gms.append(-(mag[k]+r*(mag[k+1]-mag[k])))
    return dict(phase_margin_deg=float(min(x[0] for x in pms)),
                crossover_Hz=float(min(pms)[1]),gain_margin_dB=float(min(gms)) if len(gms) else None)

summary=json.loads((OUT/'KET_QUA_TINH_CHINH.json').read_text())
fi,fv=summary['selected_bandwidth_Hz'];p=BASE.copy();Ts=p['Ts']
a,b,c,ac,bc,cc,af=matrices(p,fi,fv)
f=np.logspace(-1,np.log10(.49/Ts),2500);z=np.exp(2j*np.pi*f*Ts)
kpi,kii,kpv,kiv=gains(fi,fv)
li=response(a,b,c,z)*(kpi+kii*Ts/(z-1))
lv=response(ac,bc,cc,z)*(kpv+kiv*Ts/(z-1))
corners=[]
for lm,cm,rm in product((.8,1.2),(.7,1.3),(.5,1.5)):
    q=BASE.copy();q.update(L=p['L']*lm,C=p['C']*cm,R=p['R']*rm)
    af1=matrices(q,fi,fv)[-1];rho=float(max(np.abs(np.linalg.eigvals(af1))))
    assert rho<1
    corners.append(dict(L_factor=lm,C_factor=cm,R_factor=rm,spectral_radius=rho))
r=dict(current=margin(f,li),voltage=margin(f,lv),
       nominal_spectral_radius=float(max(np.abs(np.linalg.eigvals(af)))),corners=corners,
       scope='Discrete small-signal, constant bus/E, CV unsaturated. Includes filters, ZOH, one sample delay and Euler PI; excludes switching, ESR and electrochemical dynamics.')
assert r['current']['phase_margin_deg']>45 and r['voltage']['phase_margin_deg']>45
(OUT/'KIEM_TRA_ON_DINH.json').write_text(json.dumps(r,indent=2))
np.savez(OUT/'DU_LIEU_BODE.npz',f=f,li=li,lv=lv)
print(json.dumps(r,indent=2))
