"""Averaged, sampled-data CC-CV charger model. No switching or SOC claim."""
from pathlib import Path
import json
import numpy as np
from scipy.linalg import expm

OUT=Path(__file__).resolve().parent / 'ket_qua_chay_lai'
OUT.mkdir(exist_ok=True)
BASE=dict(P=2000., Vref=58.0, Vmax=58.4, Icc=2000/58.0,
          L=100e-6, C=1000e-6, r=.01, R=.08, Ts=20e-6,
          dmax=.90, ramp=1000., fi_filter=5000., fv_filter=1000.)

def gains(fi=1000.,fv=20.):
    wi,wv=2*np.pi*fi,2*np.pi*fv
    return np.array([BASE['L']*wi,BASE['r']*wi,BASE['C']*wv,wv/BASE['R']])

def simulate(fi=1000.,fv=20., changes=None, profile='transition', noise=False, duration=.40):
    p=BASE.copy();p.update(changes or {})
    Ts=p['Ts'];t=np.arange(round(duration/Ts)+1)*Ts;N=len(t)
    E=np.full(N,50.);vg=np.full(N,80.);lim=np.full(N,p['Icc']);vr=np.full(N,p['Vref'])
    if profile=='transition':
        E=50.+7.8*np.clip((t-.10)/.12,0,1)
        vg[(t>=.27)&(t<.32)]=72.;vg[t>=.32]=88.
        lim[(t>=.05)&(t<.07)]=20.
    elif profile=='cv_step':
        E[:]=56.0;vr[:]=57.6;vr[t>=.10]=58.0
    elif profile=='saturation':
        vg[(t>=.08)&(t<.14)]=55.
    elif profile!='cc':raise ValueError(profile)
    # Independent plant inputs are switched equivalent voltage and battery EMF.
    A=np.array([[-p['r']/p['L'],-1/p['L']],[1/p['C'],-1/(p['R']*p['C'])]])
    B=np.array([[1/p['L'],0],[0,1/(p['R']*p['C'])]])
    aug=np.zeros((4,4));aug[:2,:2]=A;aug[:2,2:]=B
    z=expm(aug*Ts);ad=z[:2,:2];bd=z[:2,2:]
    a00,a01,a10,a11=ad.ravel();b00,b01,b10,b11=bd.ravel()
    kpi,kii,kpv,kiv=gains(fi,fv)
    ai=np.exp(-2*np.pi*p['fi_filter']*Ts);av=np.exp(-2*np.pi*p['fv_filter']*Ts)
    rng=np.random.default_rng(20261012)
    ni=rng.normal(0,.03,N) if noise else np.zeros(N)
    nv=rng.normal(0,.003,N) if noise else np.zeros(N)
    v=E[0];i=0.;im=0.;vm=v;zi=0.;zv=0.;iref_old=0.;dprev=v/vg[0]
    h=np.zeros((N,10))
    for k in range(N):
        im=ai*im+(1-ai)*(i+ni[k]);vm=av*vm+(1-av)*(v+nv[k])
        ev=vr[k]-vm
        # Power limit only reduces the CC cap above nominal voltage.
        cap=min(lim[k],p['P']/max(vm,p['Vref']))
        uv=kpv*ev+zv
        top=min(cap,iref_old+p['ramp']*Ts)
        ir=min(max(uv,0.),top)
        # Clamping anti-windup includes the current cap and upward slew limit.
        if (uv<=top or ev<0) and (uv>=0 or ev>0):zv+=kiv*ev*Ts
        ei=ir-im;ui=kpi*ei+zi
        raw=(vm+ui)/vg[k]
        d=min(max(raw,0.),p['dmax'])
        if (raw<=p['dmax'] or ei<0) and (raw>=0 or ei>0):zi+=kii*ei*Ts
        ib=(v-E[k])/p['R']
        h[k]=[i,v,ib,ir,d,E[k],vg[k],vr[k],lim[k],dprev]
        u=vg[k]*dprev
        inew=a00*i+a01*v+b00*u+b01*E[k]
        vnew=a10*i+a11*v+b10*u+b11*E[k]
        # Ideal rectifier/diode-emulation clamp near zero; DCM is approximate.
        i=max(0.,inew);v=vnew;dprev=d;iref_old=ir
    return t,h,p

def metrics(t,h,p,profile='transition'):
    i,v,ib,ir,d,E,vg,vr,lim,applied=h.T
    cc=(t>=.035)&(t<.095)
    cv=t>=.25
    result={
        'I_bat_peak_A':float(np.max(ib)), 'I_L_peak_A':float(np.max(i)),
        'V_bat_peak_V':float(np.max(v)), 'P_bat_peak_W':float(np.max(v*ib)),
        'V_CV_overshoot_V':float(max(0.,np.max(v-vr))),
        'CC_IAE_As':float(np.trapezoid(np.abs(ib[cc]-ir[cc]),t[cc])),
        'CV_IAE_Vs':float(np.trapezoid(np.abs(v[cv]-vr[cv]),t[cv])),
        'CV_max_error_V':float(np.max(np.abs(v[cv]-vr[cv]))),
        'duty_rms_delta':float(np.sqrt(np.mean(np.diff(d)**2))),
        'duty_max':float(np.max(d)), 'duty_min':float(np.min(d)),
        'final_I_bat_A':float(ib[-1]), 'final_V_bat_V':float(v[-1]),
    }
    if profile=='cc':
        err=np.abs(ib-p['Icc']);bad=np.flatnonzero(err>.02*p['Icc'])
        result['settling_2pct_s']=float(t[bad[-1]+1]) if len(bad) and bad[-1]+1<len(t) else (0. if not len(bad) else None)
    if profile=='cv_step':
        mask=t>=.1;bad=np.flatnonzero(mask&(np.abs(v-vr)>.02*.4))
        result['step_settling_2pct_s']=float(t[bad[-1]+1]-.1) if len(bad) and bad[-1]+1<len(t) else None
    return result

if __name__=='__main__':
    t,h,p=simulate()
    print(json.dumps({'baseline_gains':gains().tolist(),'metrics':metrics(t,h,p)},indent=2))
