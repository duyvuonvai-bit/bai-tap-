from design_model import *
from itertools import product
import csv

rows=[]
for fi in (600.,800.,1000.,1200.,1400.,1600.,1800.):
    for fv in (40.,60.,80.,100.,120.,140.,160.,180.):
        if fi<10*fv:continue
        t,h,p=simulate(fi,fv,noise=True);m=metrics(t,h,p)
        # Transparent dimensionless score, fixed before the grid is evaluated.
        score=(m['CC_IAE_As']/.01 + (m['V_CV_overshoot_V']/.15)**2
               +m['CV_IAE_Vs']/.001 + .3*(m['duty_rms_delta']/.001)**2)
        feasible=(m['V_bat_peak_V']<58.30 and m['I_bat_peak_A']<35.2
                  and m['P_bat_peak_W']<2040.)
        rows.append(dict(fi_Hz=fi,fv_Hz=fv,score=score,feasible=feasible,**m))
best=min((r for r in rows if r['feasible']),key=lambda r:r['score'])
fi,fv=best['fi_Hz'],best['fv_Hz']
with (OUT/'BANG_TIM_KIEM_PI.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
nominal={};histories={}
for name,bw in [('ban_dau',(1000.,20.)),('da_chinh',(fi,fv))]:
    nominal[name]={}
    for profile in ('transition','cc','cv_step','saturation'):
        t,h,p=simulate(*bw,profile=profile)
        nominal[name][profile]=metrics(t,h,p,profile)
        histories[name+'_'+profile]=(t,h,p)
        if name=='da_chinh':
            data=np.column_stack([t,h])
            np.savetxt(OUT/f'DU_LIEU_{profile}.csv',data[::10],delimiter=',',
                header='t_s,i_L_A,v_bat_V,i_bat_A,i_ref_A,duty,E_V,Veq_V,Vref_V,Icap_A,duty_applied',comments='')
validation=[]
for lm,cm,rm in product((.8,1.2),(.7,1.3),(.5,1.5)):
    params={'L':BASE['L']*lm,'C':BASE['C']*cm,'R':BASE['R']*rm}
    t,h,p=simulate(fi,fv,changes=params,noise=True)
    m=metrics(t,h,p)
    passed=m['V_bat_peak_V']<BASE['Vmax'] and m['I_bat_peak_A']<35.2 and m['P_bat_peak_W']<2040
    validation.append(dict(L_factor=lm,C_factor=cm,R_factor=rm,passed=passed,**m))
summary=dict(parameters=BASE,baseline_bandwidth_Hz=[1000.,20.],
    selected_bandwidth_Hz=[fi,fv],baseline_gains=gains().tolist(),selected_gains=gains(fi,fv).tolist(),
    grid_count=len(rows),selected_grid_row=best,nominal=nominal,withheld_corners=validation,
    caveat='Averaged sampled model, prescribed E(t), no SOC or switching-loss model; MATLAB not executed here.')
(OUT/'KET_QUA_TINH_CHINH.json').write_text(json.dumps(summary,indent=2))
np.savez(OUT/'DU_LIEU_MO_PHONG.npz',**{k:np.column_stack([v[0],v[1]]) for k,v in histories.items()})
print(json.dumps({'grid_count':len(rows),'selected':best,'gains':gains(fi,fv).tolist(),
                  'corners_passed':sum(x['passed'] for x in validation),
                  'corners_total':len(validation),
                  'corner_max_voltage':max(x['V_bat_peak_V'] for x in validation),
                  'corner_max_power':max(x['P_bat_peak_W'] for x in validation),
                  'saturation':nominal['da_chinh']['saturation']},indent=2),flush=True)
