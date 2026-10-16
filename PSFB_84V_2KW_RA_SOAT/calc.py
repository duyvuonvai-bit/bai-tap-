#!/usr/bin/env python3
"""Reproducible preliminary calculations; no hardware qualification claimed."""
from pathlib import Path
import json, math
P = 2000.0
fs = 50_000.0  # illustrative full H-bridge cycle, NOT a selected design frequency
fr = 2*fs
n = 8/25
L = 33e-6
C = (220+220+680)*1e-6
Vf = .8  # illustrative per-diode forward drop
eta_dc = .95
eta_pfc = .97
PF = .99
Rsh = .0005

def point(vout, vbus, current):
    vs = n*vbus
    d = vout/vs
    ripple = vout*(1-d)/(L*fr)
    return dict(Vout_V=vout, Vbus_V=vbus, Vsecondary_pulse_V=vs,
                Iout_A=current, Pout_W=current*vout,
                D_ideal=d, D_with_2diode_drop=(vout+2*Vf)/vs,
                phase_ideal_deg=d*180, phase_with_drop_deg=(vout+2*Vf)/vs*180,
                delta_IL_pp_A=ripple, IL_peak_A=current+ripple/2,
                IL_valley_A=current-ripple/2,
                IL_rms_A=math.sqrt(current**2+ripple**2/12),
                Ic_rms_ideal_A=ripple/(2*math.sqrt(3)),
                delta_Vc_ideal_pp_V=ripple/(8*fr*C),
                P_shunt_DC_W=current**2*Rsh,
                V_shunt_DC_V=current*Rsh,
                P_diode_bridge_W=2*Vf*current,
                P_copper_per_1mohm_W=current**2*.001)

out = {
  'status': 'PRELIMINARY_PARAMETRIC_NOT_A_FABRICATION_DESIGN',
  'battery_selection': 'CONFIRMED: 20S lithium. Authorized design target 50Ah, 4.2V/cell, CV84V, BMS continuous charge>=30A. Actual cells/BMS not verified. Old58V appendix only',
  'assumptions': dict(Pout_max_W=P, Vbus_image_nominal_range_V=[390,400], Vbus_proposed_design_range_V=[380,420], Vbus_proposed_setpoint_V=400, Np=25,Ns=8,n=n,
      fs_bridge_Hz=fs, rectified_ripple_Hz=fr, L_H=L,C_F=C,
      diode_Vf_V=Vf, eta_dc=eta_dc,eta_pfc=eta_pfc,PF=PF,
      shunt_Ohm=Rsh, full_range_20S_V=[60,84],
      CC_current_20S_A=P/84, CC_current_old58V_A=P/58,
      caveat='frequency, losses and efficiencies illustrative; fixed 2kW at all battery voltages is not CC charging'),
  'points': [point(v,b,P/v) for v in (58,60,72,84) for b in (390,400)],
  'battery_design_target': dict(series_cells=20,capacity_Ah=50,CV_V=84,CC_A=P/84,charge_C_rate=(P/84)/50,BMS_continuous_charge_min_A=30,actual_product_verified=False),
  '20S_CC_points': [point(v,b,P/84) for v in (60,62.4,64,72,84) for b in (390,400)],
  'ripple_maximum_ideal': [], 'input': [], 'bulk': [], 'magnetics': [],
  'shunt_and_gain': [], 'NTC_example_B3950': []
}
for b in (390,400):
    vs=n*b; rip=vs/(4*L*fr); i=P/84
    out['ripple_maximum_ideal'].append(dict(Vbus_V=b,Vout_at_max_V=vs/2,
       delta_IL_pp_A=rip, peak_20S_CC_A=i+rip/2,
       Isat_with_25pct_design_margin_A=1.25*(i+rip/2),
       Ic_rms_A=rip/(2*math.sqrt(3)),
       cap_ripple_ideal_V=rip/(8*fr*C),
       cap_ripple_with_10mohm_ESR_V=rip/(8*fr*C)+rip*.01,
       cap_ripple_with_25mohm_ESR_V=rip/(8*fr*C)+rip*.025))
for vac in (198,220,242):
    pin=P/(eta_dc*eta_pfc)
    out['input'].append(dict(Vac_V=vac,Pin_W=pin,Iac_rms_A=pin/(vac*PF),
        sinusoidal_peak_approx_A=math.sqrt(2)*pin/(vac*PF),
        rectified_line_peak_V=math.sqrt(2)*vac))
pbus=P/eta_dc
for cb in (680e-6,1000e-6,1500e-6,2000e-6,2200e-6):
    out['bulk'].append(dict(C_uF=cb*1e6,Vbus_V=400,delta_V_100Hz_pp_V=pbus/(2*math.pi*50*cb*400),
       energy_at_400V_J=.5*cb*400**2,
       I_ripple_100Hz_rms_approx_A=pbus/(math.sqrt(2)*400)))
Cmin = pbus/(2*math.pi*50*395*10)
out['bus390to400_if_absolute_limits'] = dict(C_effective_min_uF=Cmin*1e6,
    C_nominal_min_with_minus20percent_tolerance_uF=Cmin/.8*1e6,
    caveat='Only 100Hz ripple; no hold-up, transient, control, tolerance or life qualification')
out['film_3x4p7uF'] = dict(C_total_uF=14.1,energy_at400V_J=.5*14.1e-6*400**2,
    time_from400to390_atPbus_us=(.5*14.1e-6*(400**2-390**2)/pbus)*1e6)
for ae in (250,350,400,500):
    for d in (.8,1.0):
        bpk=400*d/(4*fs*25*ae*1e-6)
        out['magnetics'].append(dict(Ae_mm2=ae,D_power_limit=d,Bpeak_T=bpk,
            Np_min_for_Bpeak_0p16T=400*d/(4*fs*ae*1e-6*.16)))
out['magnetics_operating_examples'] = [dict(Vout_V=v,Ae_mm2=ae,
    Bpeak_with_diode_drop_T=((v+2*Vf)/n)/(4*fs*25*ae*1e-6))
    for v in (58,84) for ae in (250,350,400,500)]
for v in (58,84):
    for gain in (10,20,50,100,200):
        out['shunt_and_gain'].append(dict(Vout_V=v,Iout_A=P/v,gain=gain,
           Vsignal_REF0_V=(P/v)*Rsh*gain,
           Vsignal_REF1p65_V=1.65+(P/v)*Rsh*gain,
           Itrip_at2p70_REF0_A=2.7/(gain*Rsh),
           Itrip_at2p70_REF1p65_A=(2.7-1.65)/(gain*Rsh)))
out['divider'] = dict(Rtop_Ohm=390000,Rbottom_Ohm=10000,ratio=1/40,
   Rthevenin_Ohm=9750,V_at58_V=58/40,V_at84_V=84/40,V_at100_V=100/40,
   V_trip_from2p7_V=2.7*40,
   ideal_12bit_ADC_output_resolution_V=3.3/4095*40,
   P_Rtop_at84_W=(84*39/40)**2/390000,
   time_constant_with_1kohm_and_101nF_s=(9750+1000)*101e-9,
   fc_with_1kohm_and_101nF_Hz=1/(2*math.pi*(9750+1000)*101e-9))
for temp in (25,60,80,100):
    ntc=100000*math.exp(3950*(1/(273.15+temp)-1/298.15))
    out['NTC_example_B3950'].append(dict(temp_C=temp,Rntc_Ohm=ntc,
       Vadc_with_10kohm_pullup_V=3.3*ntc/(10000+ntc)))
out['L_needed_for_20pct_ripple_worst_bus']=[dict(Vout_full_charge_V=v,
    I_CC_A=P/v,L_min_uH=(n*400)/(4*fr*(.2*P/v))*1e6) for v in (58,84)]
out['output_cap_energy_J']={str(v):.5*C*v*v for v in (58,84,100)}
out['constant_power_range20S_peak'] = point(60,400,P/60)
out['current_saturation_notes'] = dict(
    sat_margin_example=1.25,
    at58V_Ipeak_A=point(58,400,P/58)['IL_peak_A'],
    at58V_Isat_example_A=1.25*point(58,400,P/58)['IL_peak_A'],
    constant_power60V_Isat_example_A=1.25*point(60,400,P/60)['IL_peak_A'])
# Active design proposals: values to evaluate, not manufactured/verified parts.
out['active20S_recommended_Lout'] = []
for lh in (68e-6,100e-6):
    for tol in (1,.8):
        leff=lh*tol
        ripple=(n*420)/(4*leff*fr)
        current=P/84
        out['active20S_recommended_Lout'].append(dict(L_nom_uH=lh*1e6,L_effective_uH=leff*1e6,
          delta_IL_max_pp_A=ripple,ripple_fraction_CC=ripple/current,
          IL_peak_A=current+ripple/2,IL_rms_A=math.sqrt(current**2+ripple**2/12),
          Isat_example_25pct_margin_A=1.25*(current+ripple/2),
          cap_ripple_ideal_V=ripple/(8*fr*C),
          cap_current_rms_A=ripple/(2*math.sqrt(3))))
out['PFC_CCM_65kHz'] = []
for lp in (400e-6,500e-6,560e-6,600e-6):
  for tol in (1,.8):
    leff=lp*tol
    ripplemax=420/(4*leff*65000)
    for vac in (198,220,242):
      iin=P/(eta_dc*eta_pfc*PF*vac)
      vp=math.sqrt(2)*vac
      ripple_at_crest=vp*(1-vp/420)/(leff*65000)
      out['PFC_CCM_65kHz'].append(dict(Lnom_uH=lp*1e6,L_eff_uH=leff*1e6,
        Vac_V=vac,Iline_rms_A=iin,Iline_peak_A=math.sqrt(2)*iin,
        delta_I_max_pp_A=ripplemax,
        max_ripple_fraction_line_peak=ripplemax/(math.sqrt(2)*iin),
        delta_I_at_line_crest_pp_A=ripple_at_crest,
        IL_peak_at_line_crest_A=math.sqrt(2)*iin+ripple_at_crest/2,
        Isat_25pct_margin_A=1.25*(math.sqrt(2)*iin+ripple_at_crest/2)))
out['bulk_2x470uF'] = [dict(Vbus_V=vb,Cnom_uF=940,Ceff_uF=940*tol,
  ripple_pp_V=pbus/(2*math.pi*50*940e-6*tol*vb),
  Vmin_approx_V=vb-pbus/(4*math.pi*50*940e-6*tol*vb),
  Vmax_approx_V=vb+pbus/(4*math.pi*50*940e-6*tol*vb),
  I_100Hz_rms_A=pbus/(math.sqrt(2)*vb)) for vb in (390,400) for tol in (1,.8)]
out['power_semiconductor_current_illustration'] = dict(
  secondary_pulse_max_V=n*420,
  rectifier_reverse_V_preliminary_class=200,
  caveat='200V is candidate only; 250V class may be necessary after ringing; confirm high-temperature losses and transient margin',
  IL_peak_at_100uH_minus20pct_A=P/84+(n*420)/(4*80e-6*fr)/2,
  Ipri_reflected_peak_at_100uH_minus20pct_A=n*(P/84+(n*420)/(4*80e-6*fr)/2))
out['proposed_bus380to420_active_points'] = []
for vout in (60,67.2,84):
    for vbus in (380,420):
        vs=n*vbus; i=P/84; d=vout/vs
        out['proposed_bus380to420_active_points'].append(dict(Vout_V=vout,Vbus_V=vbus,
          I_CC_A=i,D_ideal=d,D_with_1p6V_drop=(vout+1.6)/vs,
          ripple_at_100uH_A=vout*(1-d)/(100e-6*fr),
          ripple_at_80uH_A=vout*(1-d)/(80e-6*fr)))
out['magnetics_proposed420V'] = [dict(Ae_mm2=ae,D_power_limit=d,
     Bpeak_T=420*d/(4*fs*25*ae*1e-6)) for ae in (250,350,400,420,500) for d in (.8,1.)]
Path(__file__).with_name('calcs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ('ripple_maximum_ideal','input','bulk','bus390to400_if_absolute_limits','divider','L_needed_for_20pct_ripple_worst_bus','current_saturation_notes')},ensure_ascii=False,indent=2))
