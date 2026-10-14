%% THIET KE BO SAC 2 kW: PI LONG NHAU, CC-CV, MO HINH TRUNG BINH
% MATLAB R2018b+; chi dung MATLAB co ban, khong can Control System Toolbox.
% Chay toan bo script. Du lieu, hinh PNG/FIG va MAT duoc ghi vao thu muc
% ket_qua_MATLAB cung vi tri voi script. Khong clear workspace/close all.
%
% DAY LA MO HINH TRUNG BINH QUY DOI BUCK CUA PSFB, KHONG PHAI MO HINH
% CHUYEN MACH, KHONG PHAI KIEM CHUNG PHAN CUNG HAY FILE SIMULINK.
% E(t) la suc dien dong gia lap de kich thich chuyen CC-CV trong 0.4 s;
% khong phai mo hinh SOC, khong du doan thoi gian sac pin 100 Ah.
% Bo dieu khien la PID voi Kd = 0 (PI); tin hieu ra PI dong co don vi V.

%% 1. Thong so danh dinh va cau hinh chay
p = struct();
p.P = 2000;                  % W, muc cong suat danh dinh
p.Vac = 220;                 % V rms, dau vao AC chi de mo ta kien truc
p.Vdc = 400;                 % V, bus PFC ly tuong (khong mo phong PFC)
p.n = 0.20;                 % ty so quy doi; Veq = n * Vdc = 80 V
p.Ns = 16;                  % 16S LiFePO4, gia thiet thiet ke
p.Q_Ah = 100;               % Ah, thong tin danh dinh; khong tinh SOC
p.Vmax = 58.4;              % V, gioi han pin; KHONG kep dien ap mo hinh
p.Vref = 58.0;              % V, dat CV co du tru so voi gioi han 58.4 V
p.Icc = p.P / p.Vref;       % A, 34.4827586207 A
p.L = 100e-6;              % H
p.C = 1000e-6;             % F
p.r = 0.01;                % ohm, dien tro noi tiep cuon cam
p.R = 0.08;                % ohm, dien tro noi pin tuong duong
p.Ts = 20e-6;              % s, tan so lay mau 50 kHz
p.dmax = 0.90;             % gioi han duty tuong duong, 0 <= d <= 0.9
p.ramp = 1000;             % A/s, chi gioi han toc do TANG Iref
p.fi_filter = 5000;        % Hz, loc do dong bac nhat
p.fv_filter = 1000;        % Hz, loc do dien ap bac nhat

duration = 0.40;           % s, cua so thu nghiem mo hinh gia lap
runSaturationStress = false; % true: them sut Veq = 55 V, 0.08--0.14 s
showFigures = true;        % false: van luu hinh, cua so khong hien thi

% He so thiet ke duoc chon NGOAI script nay tu luoi 35 cap (fi, fv);
% xem BANG_TIM_KIEM_PI.csv va KET_QUA_TINH_CHINH.json kem bao cao.
% Script nay khong tu toi uu.
% Su dung cung thong so L, r, C, R danh dinh de tinh gain trong moi ca.
controllers = struct([]);
controllers(1).label = 'Ban dau';
controllers(1).tag = 'ban_dau';
controllers(1).fi = 1000;
controllers(1).fv = 20;
controllers(2).label = 'Hieu chinh';
controllers(2).tag = 'hieu_chinh';
controllers(2).fi = 1200;   % Hz, cap duoc chon tu luoi gioi han
controllers(2).fv = 100;    % Hz, dong bo voi ket qua trong bao cao

scriptPath = mfilename('fullpath');
if isempty(scriptPath)
    baseDir = pwd;
else
    baseDir = fileparts(scriptPath);
end
resultDir = fullfile(baseDir, 'ket_qua_MATLAB');
if ~exist(resultDir, 'dir')
    mkdir(resultDir);
end

validateParameters(p, duration);
for j = 1:numel(controllers)
    controllers(j).gains = piGains(p, controllers(j).fi, controllers(j).fv);
end
scenarioNames = {'transition', 'cc', 'cv_step'};
if runSaturationStress
    scenarioNames{end+1} = 'saturation';
end

fprintf('Mo hinh trung binh PSFB quy doi buck; Ts = %.1f us.\n', p.Ts*1e6);
fprintf('CV = %.2f V; gioi han pin = %.2f V; Icc = %.6f A.\n', ...
    p.Vref, p.Vmax, p.Icc);
fprintf('Khong them nhieu: cho phep doi chieu voi Python noise=False.\n');
fprintf('E(t) la kich thich gia lap, khong phai qua trinh SOC/thoi gian sac.\n');
fprintf('Ket qua luu tai: %s\n\n', resultDir);

%% 2. Chay cac kich ban va luu ket qua
allResults = struct([]);
summary = struct([]);
gainTable = table({controllers.tag}', [controllers.fi]', [controllers.fv]', ...
    arrayfun(@(q) q.gains(1), controllers)', ...
    arrayfun(@(q) q.gains(2), controllers)', ...
    arrayfun(@(q) q.gains(3), controllers)', ...
    arrayfun(@(q) q.gains(4), controllers)', ...
    'VariableNames', {'Controller','fi_Hz','fv_Hz', ...
    'Kpi_V_per_A','Kii_V_per_As','Kpv_A_per_V','Kiv_A_per_Vs'});
writetable(gainTable, fullfile(resultDir, 'he_so_PI.csv'));

row = 0;
for s = 1:numel(scenarioNames)
    profile = scenarioNames{s};
    caseResults = struct([]);
    for j = 1:numel(controllers)
        [t, h] = runModel(p, controllers(j).gains, profile, duration);
        met = getMetrics(t, h, p, profile);
        dataTable = array2table([t, h], 'VariableNames', ...
            {'t_s','I_L_A','V_bat_V','I_bat_A','I_ref_A','d_command', ...
            'E_bat_V','V_eq_V','V_ref_V','I_limit_A','d_applied'});
        stem = [profile '_' controllers(j).tag];
        writetable(dataTable, fullfile(resultDir, [stem '.csv']));

        row = row + 1;
        summary(row).Scenario = profile;
        summary(row).Controller = controllers(j).tag;
        metricNames = fieldnames(met);
        for q = 1:numel(metricNames)
            summary(row).(metricNames{q}) = met.(metricNames{q});
        end
        caseResults(j).t = t;
        caseResults(j).h = h;
        caseResults(j).metrics = met;
        caseResults(j).controller = controllers(j);
        allResults(row).scenario = profile;
        allResults(row).result = caseResults(j);
        fprintf('%s / %s: Vpk %.6f V; Ibat,pk %.6f A; Ppk %.3f W\n', ...
            profile, controllers(j).tag, met.V_bat_peak_V, ...
            met.I_bat_peak_A, met.P_bat_peak_W);
    end
    drawScenario(caseResults, p, profile, resultDir, showFigures);
end
summaryTable = struct2table(summary);
writetable(summaryTable, fullfile(resultDir, 'chi_tieu.csv'));
save(fullfile(resultDir, 'ket_qua_day_du.mat'), 'p', 'controllers', ...
    'scenarioNames', 'duration', 'allResults', 'summaryTable', 'gainTable');
disp(gainTable);
disp(summaryTable);
fprintf('\nDa luu CSV, PNG, FIG va MAT. Can kiem chung chuyen mach/phan cung rieng.\n');

%% CAC HAM CUC BO (MATLAB R2018b+)
function validateParameters(p, duration)
    assert(p.L > 0 && p.C > 0 && p.r > 0 && p.R > 0, ...
        'L, C, r, R phai duong.');
    assert(p.Ts > 0 && duration >= 0.30 && p.P > 0 && p.Icc > 0, ...
        'Can Ts > 0, duration >= 0.30 s, P > 0 va Icc > 0.');
    assert(p.dmax > 0 && p.dmax <= 1 && p.ramp > 0, ...
        'Can 0 < dmax <= 1 va ramp > 0.');
    assert(p.Vref > 0 && p.Vref < p.Vmax && p.Vdc*p.n > p.Vref, ...
        'Can 0 < Vref < Vmax va Veq danh dinh > Vref.');
    assert(p.fi_filter > 0 && p.fi_filter < 0.5/p.Ts && ...
        p.fv_filter > 0 && p.fv_filter < 0.5/p.Ts, ...
        'Tan so loc phai duong va nho hon tan so Nyquist.');
end

function g = piGains(p, fi, fv)
    assert(fi > 0 && fv > 0 && fv < fi && fi < 0.5/p.Ts, ...
        'Can 0 < fv < fi < fs/2.');
    wi = 2*pi*fi;
    wv = 2*pi*fv;
    % Xap xi thiet ke lien tuc; ket qua cuoi duoc danh gia tren mo hinh
    % co lay mau, tre mot mau, loc, bao hoa va gioi han toc do Iref.
    g = [p.L*wi, p.r*wi, p.C*wv, wv/p.R];
end

function [t, h] = runModel(p, g, profile, duration)
    t = (0:round(duration/p.Ts))' * p.Ts;
    N = numel(t);
    E = 50 * ones(N, 1);
    vg = (p.Vdc*p.n) * ones(N, 1);
    lim = p.Icc * ones(N, 1);
    vr = p.Vref * ones(N, 1);
    switch profile
        case 'transition'
            E = 50 + 7.8 * min(max((t-0.10)/0.12, 0), 1);
            vg(t >= 0.27 & t < 0.32) = 72;
            vg(t >= 0.32) = 88;
            lim(t >= 0.05 & t < 0.07) = 20;
        case 'cc'
            % E = 50 V khong doi: dap ung khoi dong CC.
        case 'cv_step'
            E(:) = 56;
            vr(:) = 57.6;
            vr(t >= 0.10) = 58.0;
        case 'saturation'
            % Khong du headroom: bo dieu khien khong the giu Icc.
            vg(t >= 0.08 & t < 0.14) = 55;
        otherwise
            error('Kich ban khong hop le: %s', profile);
    end

    % x = [iL; vBat], u = [Veq*dApplied; E].
    % L*diL/dt = Veq*dApplied - vBat - r*iL;
    % C*dvBat/dt = iL - (vBat-E)/R.
    % Ma tran ZOH chinh xac voi dau vao giu nguyen trong moi chu ky Ts.
    A = [-p.r/p.L, -1/p.L; 1/p.C, -1/(p.R*p.C)];
    B = [1/p.L, 0; 0, 1/(p.R*p.C)];
    aug = zeros(4);
    aug(1:2, 1:2) = A;
    aug(1:2, 3:4) = B;
    z = expm(aug*p.Ts);
    Ad = z(1:2, 1:2);
    Bd = z(1:2, 3:4);
    ai = exp(-2*pi*p.fi_filter*p.Ts);
    av = exp(-2*pi*p.fv_filter*p.Ts);
    kpi = g(1); kii = g(2); kpv = g(3); kiv = g(4);

    i = 0; v = E(1); im = 0; vm = v;
    zi = 0; zv = 0; irefOld = 0;
    dprev = v/vg(1);         % gia tri duty truoc mau dau tien
    h = zeros(N, 10);
    for k = 1:N
        % Dung do luong khong nhieu de doi chieu so hoc voi Python.
        im = ai*im + (1-ai)*i;
        vm = av*vm + (1-av)*v;
        ev = vr(k)-vm;
        % Gioi han cong suat chi giam tran CC khi vm > Vref danh dinh.
        cap = min(lim(k), p.P/max(vm, p.Vref));
        uv = kpv*ev + zv;
        top = min(cap, irefOld+p.ramp*p.Ts);
        ir = min(max(uv, 0), top);
        % Clamping anti-windup tinh CA tran dong va gioi han tang Iref.
        % Khong cap nhat tich phan neu sai so day sau hon vao bao hoa.
        if (uv <= top || ev < 0) && (uv >= 0 || ev > 0)
            zv = zv + kiv*ev*p.Ts;
        end
        ei = ir-im;
        ui = kpi*ei + zi;    % V, khong phai truc tiep duty
        raw = (vm+ui)/vg(k); % feedforward dien ap pin
        d = min(max(raw, 0), p.dmax);
        if (raw <= p.dmax || ei < 0) && (raw >= 0 || ei > 0)
            zi = zi + kii*ei*p.Ts;
        end

        ib = (v-E(k))/p.R;
        h(k, :) = [i, v, ib, ir, d, E(k), vg(k), vr(k), lim(k), dprev];
        u = vg(k)*dprev;    % tre co cau chap hanh dung MOT mau Ts
        inew = Ad(1,1)*i + Ad(1,2)*v + Bd(1,1)*u + Bd(1,2)*E(k);
        vnew = Ad(2,1)*i + Ad(2,2)*v + Bd(2,1)*u + Bd(2,2)*E(k);
        % Xap xi diode/diode-emulation; khong phai mo hinh DCM chi tiet.
        i = max(0, inew);
        v = vnew;
        dprev = d;
        irefOld = ir;
    end
end

function m = getMetrics(t, h, p, profile)
    i = h(:,1); v = h(:,2); ib = h(:,3); ir = h(:,4);
    d = h(:,5); vr = h(:,8);
    cc = t >= 0.035 & t < 0.095;
    cv = t >= 0.25;
    m.I_bat_peak_A = max(ib);
    m.I_L_peak_A = max(i);
    m.V_bat_peak_V = max(v);
    m.P_bat_peak_W = max(v.*ib);
    m.V_CV_overshoot_V = max(0, max(v-vr));
    m.CC_IAE_As = trapz(t(cc), abs(ib(cc)-ir(cc)));
    m.CV_IAE_Vs = trapz(t(cv), abs(v(cv)-vr(cv)));
    m.CV_max_error_V = max(abs(v(cv)-vr(cv)));
    m.duty_rms_delta = sqrt(mean(diff(d).^2));
    m.duty_max = max(d);
    m.duty_min = min(d);
    m.final_I_bat_A = ib(end);
    m.final_V_bat_V = v(end);
    m.settling_2pct_s = NaN;
    m.step_settling_2pct_s = NaN;
    if strcmp(profile, 'cc')
        bad = find(abs(ib-p.Icc) > 0.02*p.Icc);
        if isempty(bad)
            m.settling_2pct_s = 0;
        elseif bad(end) < numel(t)
            m.settling_2pct_s = t(bad(end)+1);
        end
    elseif strcmp(profile, 'cv_step')
        % Tieu chuan 2%% cua BUOC 0.4 V = 8 mV, tinh tu t = 0.10 s.
        bad = find(t >= 0.10 & abs(v-vr) > 0.02*0.4);
        if ~isempty(bad) && bad(end) < numel(t)
            m.step_settling_2pct_s = t(bad(end)+1)-0.10;
        end
    end
end

function drawScenario(results, p, profile, resultDir, showFigures)
    if showFigures
        vis = 'on';
    else
        vis = 'off';
    end
    colors = [0.15 0.35 0.72; 0.85 0.30 0.12];
    labels = arrayfun(@(q) q.controller.label, results, 'UniformOutput', false);
    fig = figure('Name', ['Bo sac 2 kW - ' profile], ...
        'Color', 'w', 'Visible', vis, 'Position', [70 70 1200 850]);
    axesHandles = gobjects(6,1);
    for n = 1:6
        axesHandles(n) = subplot(3, 2, n, 'Parent', fig);
        hold(axesHandles(n), 'on');
        grid(axesHandles(n), 'on');
        xlabel(axesHandles(n), 'Thoi gian (s)');
    end
    for j = 1:numel(results)
        t = results(j).t; h = results(j).h;
        plot(axesHandles(1), t, h(:,3), 'Color', colors(j,:), 'LineWidth', 1.1);
        plot(axesHandles(2), t, h(:,2), 'Color', colors(j,:), 'LineWidth', 1.1);
        plot(axesHandles(3), t, h(:,4), 'Color', colors(j,:), 'LineWidth', 1.1);
        plot(axesHandles(4), t, h(:,5), 'Color', colors(j,:), 'LineWidth', 1.1);
        plot(axesHandles(5), t, h(:,2).*h(:,3), 'Color', colors(j,:), 'LineWidth', 1.1);
    end
    t = results(1).t; h = results(1).h;
    plot(axesHandles(1), t, h(:,9), 'k--', 'LineWidth', 0.9);
    plot(axesHandles(2), t, h(:,8), 'k--', 'LineWidth', 0.9);
    plot(axesHandles(2), t, p.Vmax*ones(size(t)), 'k:', 'LineWidth', 0.9);
    plot(axesHandles(5), t, p.P*ones(size(t)), 'k--', 'LineWidth', 0.9);
    plot(axesHandles(6), t, h(:,6), 'Color', [0.25 0.55 0.30], 'LineWidth', 1.1);
    plot(axesHandles(6), t, h(:,7), 'Color', [0.45 0.20 0.65], 'LineWidth', 1.1);
    ylabel(axesHandles(1), 'I pin (A)');
    ylabel(axesHandles(2), 'V pin (V)');
    ylabel(axesHandles(3), 'I tham chieu (A)');
    ylabel(axesHandles(4), 'Duty ra lenh');
    ylabel(axesHandles(5), 'P pin (W)');
    ylabel(axesHandles(6), 'Dien ap (V)');
    title(axesHandles(1), ['Dong sac - ' profile], 'Interpreter', 'none');
    title(axesHandles(2), 'Dien ap pin va gia tri dat');
    title(axesHandles(3), 'Tham chieu vong dong');
    title(axesHandles(4), 'Duty sau bao hoa (tre ap dung: 1 mau)');
    title(axesHandles(5), 'Cong suat dau ra pin');
    title(axesHandles(6), 'Kich thich gia lap, khong phai SOC');
    legend(axesHandles(1), [labels, {'Tran dong ngoai'}], 'Location', 'best');
    legend(axesHandles(2), [labels, {'V dat', 'Gioi han pin'}], 'Location', 'best');
    legend(axesHandles(3), labels, 'Location', 'best');
    legend(axesHandles(4), labels, 'Location', 'best');
    legend(axesHandles(5), [labels, {'Danh dinh 2 kW'}], 'Location', 'best');
    legend(axesHandles(6), {'E gia lap', 'Veq quy doi'}, 'Location', 'best');
    set(fig, 'PaperPositionMode', 'auto');
    print(fig, fullfile(resultDir, [profile '.png']), '-dpng', '-r160');
    savefig(fig, fullfile(resultDir, [profile '.fig']));
    % Khong close fig: moi kich ban co figure va axes handle doc lap.
end
