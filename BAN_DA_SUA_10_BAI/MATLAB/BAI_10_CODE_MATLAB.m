%% BAI 10: CODE MATLAB CHAY DOC LAP - NHAN RUN (DA RA SOAT)
clear; clc; close all;
baiCanGiai = 10;
% ================================================================
% GIAI BAI TAP CHUONG 2 - THIET KE VA CHINH DINH PI/PID
% Theo trinh tu Huong dan HW_W2: mo hinh > Pade > on dinh > step >
% IAE/ISE/ITAE > Ms/Mt > GM/PM > Bode/Nyquist > servo/regulator.
%
% MO FILE NAY TRONG MATLAB VA BAM RUN. KHONG CAN FILE .M KHAC.
% Hay GIAI NEN ZIP truoc khi mo file; khong chay truc tiep trong ZIP.
% Ket qua duoc luu vao thu muc KET_QUA_MATLAB ben canh file .m.
%
% Can Control System Toolbox, MATLAB R2018b tro len.
% Toan bo ket qua la mo phong tren mo hinh Pade bac 6.
% Haalman FOPDT cho PI; neu viet dang PID thi Td=0, trung cung bo PI.
% Hai tai lieu mau KHONG cho quy tac Haalman PID doc lap.
% Vi vay co 7 bo KHAC NHAU; khong tu dat them tham so bo thu 8.
% Doi chieu voi giang vien neu yeu cau mot bien the Haalman PID rieng.
% CHR chon Servo 0% overshoot (de bai khong chi ro bien the).
% "0%" la ten bang chinh dinh, KHONG bao dam Mp do duoc bang 0.
% ZN, CHR, CC dung bang cong thuc bo sung; hai file mau chu yeu day
% cach DANH GIA, khong cung cap day du bang thiet ke bon phuong phap.
% PID LY TUONG + Pade huu ti co duong truyen truc tiep va co the tao
% y(0+) khac 0 / dao dong som. Day la dac tinh cua xap xi, khong phai
% dap ung chinh xac cua tre thuan. Khong tu y them loc vi phan vao de.
% Ket qua so can chay kiem chung tren MATLAB + Control System Toolbox.
% ================================================================

if ~isnumeric(baiCanGiai) || any(~ismember(baiCanGiai,1:10))
    error('Sai so bai: phai la so nguyen tu 1 den 10.');
end

assert(exist('tf','file') == 2 && license('test','Control_Toolbox'), ...
    'Can MATLAB va Control System Toolbox.');
PadeBac = 6;
VeDoThi = true;
HienThiDoThi = (numel(baiCanGiai) == 1);
SoMauThoiGian = 100001;
SoMauTanSo = 50000;

% Du lieu lay tu "Bai tap chuong 2.pdf"
K_danhSach = [1.8, 0.75, 12, 2.4, 0.42, 0.065, 0.28, -1.15, 0.032, 3.2];
T_danhSach = [450, 180, 2.8, 320, 18, 35, 600, 520, 1.6, 240];
L_danhSach = [55, 25, 0.18, 48, 2.5, 4, 90, 70, 0.12, 32];
TenDoiTuong = {'Lo gia nhiet','Muc chat long','Toc do dong co', ...
    'Trao doi nhiet','Luu luong duong ong','Ap suat khi nen', ...
    'Nong do be khuay','Do am buong say','Toc do bang tai','Sao che'};
DonViVao = {'kW','L/min','V','kg/min','%','%','L/min','kW','Hz','kW'};
DonViRa = {'do C','cm','rad/s','do C','m^3/h','bar','%','%RH','m/s','do C'};

% 7 BO DIEU KHIEN KHAC NHAU (Haalman FOPDT chi xac dinh PI)
TenBoDK = {'ZN_PI','ZN_PID','Haalman_PI','CHR_PI','CHR_PID','CC_PI','CC_PID'};

ThuMucGoc = fullfile(fileparts(mfilename('fullpath')),'KET_QUA_MATLAB');
if ~exist(ThuMucGoc,'dir'), mkdir(ThuMucGoc); end
KetQuaTatCa = table();

for bai = baiCanGiai(:)'
    K = K_danhSach(bai);
    T = T_danhSach(bai);
    Ltre = L_danhSach(bai);
    ThuMucBai = fullfile(ThuMucGoc,sprintf('BAI_%02d',bai));
    if ~exist(ThuMucBai,'dir'), mkdir(ThuMucBai); end
    TepLog = fullfile(ThuMucBai,sprintf('Ket_qua_Bai_%02d.txt',bai));
    if exist(TepLog,'file'), delete(TepLog); end % chi log sinh boi script
    diary(TepLog); diary on;

    fprintf('\n============================================================\n');
    fprintf('BAI %d - %s\n',bai,TenDoiTuong{bai});
    fprintf('I. KHAI BAO: G(s) = K/(T*s+1)*exp(-L*s)\n');
    fprintf('K = %.8g; T = %.8g s; L = %.8g s\n',K,T,Ltre);
    fprintf('u(t): %s; y(t): %s; Don vi K: (%s)/(%s)\n',...
        DonViVao{bai},DonViRa{bai},DonViRa{bai},DonViVao{bai});
    fprintf('A = T/(abs(K)*L) = %.9g; rho = L/T = %.9g\n',...
        T/(abs(K)*Ltre), Ltre/T);
    if K < 0
        fprintf('CHU Y: K < 0. Kp phai AM de tao phan hoi am thuc su.\n');
    end

    %% 1 - Ham truyen doi tuong, Pade bac 6
    s = tf('s');
    G0 = K/(T*s+1);
    [numD,denD] = pade(Ltre,PadeBac);
    D = tf(numD,denD);
    % ZPK giup tranh nhan he so da thuc co thang do rat khac nhau.
    % Dat nguong triet tieu nho theo thang tan so; giu cuc/zero cham
    % gan nhau nhung KHONG trung nhau (dac biet CHR-PID).
    tolMinreal = 1e-10/max(T,Ltre);
    G = minreal(zpk(G0)*zpk(D),tolMinreal);
    fprintf('\n1. DOI TUONG KHONG TRE G0(s):\n'); disp(G0);
    fprintf('XAP XI TRE PADE BAC %d, D(s):\n',PadeBac); disp(D);

    % Lua chon cua so mo phong theo thang thoi gian cua tung bai
    tEnd = max(35*T,100*Ltre);
    t = linspace(0,tEnd,SoMauThoiGian)';
    % Luoi logarit co thay doi theo T,L cua he nhanh/cham
    w = logspace(log10(1e-6/Ltre),log10(1e3/Ltre),SoMauTanSo);
    wLow = logspace(log10(1/(1e5*T)),log10(1/(10*T)),2000);

    BangBai = table();
    if VeDoThi
        hTong = figure('Color','w','Visible',chonHienThi(HienThiDoThi),...
            'Name',sprintf('Bai %d - Tat ca Step',bai));
        hold on; grid on; plot(t,ones(size(t)),'k--','LineWidth',1.1,...
            'DisplayName','Gia tri dat r(t)=1');
    end

    for ib = 1:numel(TenBoDK)
        Ten = TenBoDK{ib};
        [Kp,Ti,Td] = chinhDinh(K,T,Ltre,Ten);
        fprintf('\n------------------------------------------------------------\n');
        fprintf('BO %d/%d: %s\n',ib,numel(TenBoDK),Ten);
        fprintf('Kp = %.9g; Ti = %.9g s; Td = %.9g s\n',Kp,Ti,Td);
        if Td == 0
            fprintf('C_PI(s) = %.9g * (1 + 1/(%.9g*s))\n',Kp,Ti);
        else
            fprintf('C_PID(s) = %.9g * (1 + 1/(%.9g*s) + %.9g*s)\n',Kp,Ti,Td);
        end

        % Giong Huong dan HW_W2: L0, Tcl, S
        C = Kp*(1 + 1/(Ti*s) + Td*s);
        L0 = minreal(zpk(C)*G,tolMinreal);
        Tcl = minreal(feedback(L0,1),tolMinreal);
        S = minreal(feedback(1,L0),tolMinreal);
        % feedback(G,C) = G/(1+GC) = G*S, nhu Huong dan.
        % Lap truc tiep de tranh nhan lai cac cuc/zero Pade trung lap.
        Gd2y = minreal(feedback(G,zpk(C)),tolMinreal);

        %% 2 - Kiem tra cuc he kin
        pCL = pole(Tcl);
        pAll = [pCL; pole(S); pole(Gd2y)];
        OnDinh = all(real(pAll) < 0); % kiem tra cac kenh can mo phong
        maxRealPole = max(real(pCL));
        maxRealPoleAll = max(real(pAll));
        fprintf('\nII. KIEM TRA CUC HE KIN\n'); disp(pCL);
        fprintf('He kin on dinh danh dinh = %d\n',OnDinh);
        fprintf('max Re pole(Tcl)=%.9g; max Re pole(cac kenh)=%.9g\n', ...
            maxRealPole,maxRealPoleAll);

        %% 3 - Chi tieu mien thoi gian
        Mp = NaN; tr = NaN; ts = NaN; ess = NaN;
        IAE = NaN; ISE = NaN; ITAE = NaN;
        yMax = NaN; yCuoi = NaN; yss = NaN; essLyThuyet = NaN;
        ydPeak = NaN; ydCuoi = NaN; IAE_d = NaN; ISE_d = NaN; ITAE_d = NaN;
        servoGood = false; regulatorGood = false; robustGood = false;
        robustAcceptable = false; NhanXet = 'Khong on dinh';
        designOrientation = 'KHONG DANH GIA';
        controlObjective = 'KHONG DANH GIA';
        performanceScore = NaN; robustnessScore = NaN;
        if OnDinh
            % Dam bao it nhat 20 hang so thoi gian cua mode cham nhat.
            tEndModel = max(tEnd,20/min(-real(pAll)));
            if tEndModel == tEnd
                nTime = SoMauThoiGian;
            else
                nTime = max(SoMauThoiGian,ceil(tEndModel/(t(2)-t(1)))+1);
            end
            tModel = linspace(0,tEndModel,nTime)';
            [y,tt] = step(Tcl,tModel); y = squeeze(y); y = y(:);
            tt = tt(:); r = ones(size(tt)); e = r-y;
            info = stepinfo(y,tt,1,'RiseTimeLimits',[0.1 0.9],...
                'SettlingTimeThreshold',0.02);
            yMax = max(y); yCuoi = y(end);
            yss = dcgain(Tcl); essLyThuyet = 1-yss;
            assert(abs(essLyThuyet) < 1e-7, ...
                'He co tich phan nhung dcgain(Tcl) khac 1; can kiem tra mo hinh.');
            Mp = max(0,(yMax-1)*100);
            tr = info.RiseTime; ts = info.SettlingTime;
            ess = e(end);
            IAE = trapz(tt,abs(e));
            ISE = trapz(tt,e.^2);
            ITAE = trapz(tt,tt.*abs(e));
            [yd,td] = step(Gd2y,tModel); yd = squeeze(yd); yd = yd(:);
            td = td(:);
            ydPeak = max(abs(yd)); ydCuoi = yd(end);
            IAE_d = trapz(td,abs(yd)); ISE_d = trapz(td,yd.^2);
            ITAE_d = trapz(td,td.*abs(yd));
            fprintf('\nIII. CHI TIEU MIEN THOI GIAN (STEP r=1)\n');
            fprintf('y_ss = %.9g; y(end) = %.9g; y_max = %.9g\n',yss,yCuoi,yMax);
            fprintf('Cua so mo phong [0, %.9g] s; so mau = %d\n',tt(end),numel(tt));
            fprintf('Mp = %.6f %%; tr = %.6g s; ts 2%% = %.6g s\n',Mp,tr,ts);
            fprintf('ess cuoi cua so = %.9g; ess ly thuyet = %.9g\n',ess,essLyThuyet);
            fprintf('IAE = %.9g; ISE = %.9g; ITAE = %.9g\n',IAE,ISE,ITAE);
            disp(info);
        else
            fprintf('He khong on dinh: bo qua chi tieu Step/tr/ts/IAE/ISE/ITAE.\n');
        end

        %% 4 - Chi tieu mien tan so
        Sw = squeeze(freqresp(S,w)); Sw = Sw(:)';
        Tw = squeeze(freqresp(Tcl,w)); Tw = Tw(:)';
        % Cuc dai tren luoi log; them gioi han w=0 va w->Inf.
        % Nho vay Mt=1 tai DC khong bi gan sai thanh wMin cua luoi.
        [Ms,iMs] = max(abs(Sw)); [Mt,iMt] = max(abs(Tw));
        wMs = w(iMs); wMt = w(iMt);
        [numL,denL] = tfdata(tf(L0),'v');
        if numel(numL)==numel(denL), Linf=numL(1)/denL(1);
        else, Linf=0; end
        Sdc = abs(dcgain(S)); Tdc = abs(dcgain(Tcl));
        Sinf = abs(1/(1+Linf)); Tinf = abs(Linf/(1+Linf));
        if Sdc > Ms, Ms=Sdc; wMs=0; end
        if Sinf > Ms, Ms=Sinf; wMs=Inf; end
        if Tdc >= Mt, Mt=Tdc; wMt=0; end
        if Tinf > Mt, Mt=Tinf; wMt=Inf; end
        % Neu cuc dai noi tai co the chua duoc lay mau, tang SoMauTanSo.
        % Luoi hien tai co 50000 diem va duoc chuan hoa theo T,L.
        lambda = 1/Ms;
        Ms_dB = 20*log10(Ms); Mt_dB = 20*log10(Mt);
        [GM,PM,wPi,wC] = margin(L0);
        if isinf(GM), GMdB=Inf; else, GMdB=20*log10(GM); end
        AM = allmargin(L0);
        Slow = squeeze(abs(freqresp(S,wLow)));
        S0 = max(Slow); % S0_max trong huong dan: max TOAN DAI TAN SO THAP
        fprintf('\nIV. CHI TIEU MIEN TAN SO / DU TRU ON DINH\n');
        fprintf('Ms = %.8f (%.5f dB), omegaMs = %.9g rad/s\n',Ms,Ms_dB,wMs);
        fprintf('Mt = %.8f (%.5f dB), omegaMt = %.9g rad/s\n',Mt,Mt_dB,wMt);
        fprintf('lambda = 1/Ms = %.8f\n',lambda);
        fprintf('GM = %.8f (= %.5f dB); PM = %.5f deg\n',GM,GMdB,PM);
        fprintf('omegaPi = %.9g rad/s; omegaC = %.9g rad/s\n',wPi,wC);
        fprintf('Bang tat ca cac du tru [allmargin]:\n'); disp(AM);

        %% 5 - Tam/ban kinh vong Ms/Mt tren mat phang L0
        Cs = -1; Rs = 1/Ms;
        MtLaDuongThang = (wMt == 0 && abs(Mt-1) <= 1e-10);
        if MtLaDuongThang
            Ct = NaN; Rt = Inf;
        else
            Ct = Mt^2/(1-Mt^2);
            Rt = Mt/abs(1-Mt^2);
        end
        fprintf('\nV. HINH HOC NYQUIST\n');
        fprintf('Vong Ms: tam (%.4f,0), ban kinh %.8f\n',Cs,Rs);
        if MtLaDuongThang
            fprintf('Mt xap xi 1: duong thang Re(L0)=-0.5 (khong phai vong tron huu han).\n');
        else
            fprintf('Vong Mt: tam (%.8g,0), ban kinh %.8g\n',Ct,Rt);
        end

        %% 6 - Servo / Regulator / Robustness theo chuong V Huong dan
        fprintf('\nVI. NHAN XET SERVO / REGULATOR / ROBUSTNESS\n');
        if OnDinh
            fprintf('Servo: ess = %.5g; Mp = %.3f%%; tr = %.4g; ts = %.4g.\n',...
                ess,Mp,tr,ts);
            fprintf('Regulator (nhieu truoc G): |yd|peak = %.7g; yd(end) = %.7g; max|S(jwLow)|=%.5g\n',...
                ydPeak,ydCuoi,S0);
            if Ms <= 1.4, MsNhanXet = 'tot';
            elseif Ms <= 2, MsNhanXet = 'chap nhan';
            else, MsNhanXet = 'yeu'; end
            fprintf('Nhieu: IAE_d=%.7g; ISE_d=%.7g; ITAE_d=%.7g\n',IAE_d,ISE_d,ITAE_d);
            fprintf('Dai tan so thap: [%.5g, %.5g] rad/s; S0_max=%.7g\n', ...
                wLow(1),wLow(end),S0);
            % Nguong tham khao chuong V cua Huong dan; khong phai rang
            % buoc vat ly bat buoc, dac biet voi cac dau ra khac don vi.
            servoGood = abs(ess)<=1e-3 && Mp<=10;
            regulatorGood = abs(ydCuoi)<=1e-3 && S0<=1;
            robustGood = Ms<=2 && Mt<=1.25 && PM>=45 && GMdB>=6;
            robustAcceptable = Ms<=2 && PM>=30 && GMdB>=6;
            if robustGood
                NhanXet = 'Do ben vung tot theo nguong tham khao';
            elseif robustAcceptable
                NhanXet = 'Do ben vung chap nhan duoc theo nguong tham khao';
            else
                NhanXet = 'Can cai thien do ben vung / du tru on dinh';
            end
            fprintf('M_s: %s. Ket luan: %s.\n',MsNhanXet,NhanXet);
            fprintf('Servo dat nguong tham khao: %d; Regulator dat: %d.\n', ...
                servoGood,regulatorGood);
            % Diem phan loai dung nhu huong dan; chi la heuristic.
            performanceScore = 2*(abs(ess)<=1e-3) + (Mp<=10) + (IAE<=0.1*tEndModel);
            robustnessScore = (Ms<=2) + (Ms<=1.6) + (Mt<=1.25) + ...
                0.5*(PM>=30) + 0.5*(PM>=45) + 0.5*(GMdB>=6) + 0.5*(GMdB>=10);
            if performanceScore >= robustnessScore+2
                designOrientation = 'THIEN VE PERFORMANCE';
            elseif robustnessScore >= performanceScore+2
                designOrientation = 'THIEN VE ROBUSTNESS';
            else
                designOrientation = 'CAN BANG PERFORMANCE - ROBUSTNESS';
            end
            fprintf('Phan loai theo diem tham khao: %s (P=%.1f; R=%.1f).\n', ...
                designOrientation,performanceScore,robustnessScore);
            fprintf('Phan loai tren KHONG bao dam he dat ca hai tieu chuan.\n');
            if servoGood && regulatorGood
                controlObjective = 'SERVO - REGULATOR KET HOP';
            elseif servoGood
                controlObjective = 'CHU YEU LA SERVO';
            elseif regulatorGood
                controlObjective = 'CHU YEU LA REGULATOR';
            else
                controlObjective = 'CHUA DAT NGUONG SERVO HOAC REGULATOR';
            end
            fprintf('Phan loai muc tieu theo huong dan: %s.\n',controlObjective);
            fprintf('Muc tieu thu nghiem chinh: SERVO (dap ung buoc gia tri dat).\n');
        else
            fprintf('Khong ket luan hieu suat/ben vung khi he kin khong on dinh.\n');
        end

        %% 7 - Luu ket qua bang (1 hang cho moi bo PI/PID)
        row = table({Ten},Kp,Ti,Td,OnDinh,yCuoi,yMax,Mp,tr,ts,ess,...
            IAE,ISE,ITAE,Ms,wMs,Mt,wMt,lambda,GM,GMdB,PM,wPi,wC,...
            Cs,Rs,Ct,Rt,MtLaDuongThang,ydPeak,ydCuoi,S0,...
            yss,essLyThuyet,maxRealPole,maxRealPoleAll,IAE_d,ISE_d,ITAE_d,...
            servoGood,regulatorGood,robustGood,robustAcceptable,{NhanXet},{designOrientation},performanceScore,robustnessScore,{controlObjective},...
            'VariableNames',{'BoDieuKhien','Kp','Ti_s','Td_s','OnDinh',...
            'y_end','y_max','Mp_pct','tr_s','ts_s','ess','IAE','ISE','ITAE',...
            'Ms','omega_Ms','Mt','omega_Mt','lambda','GM','GM_dB','PM_deg',...
            'omega_pi','omega_c','TamMs','BanKinhMs','TamMt','BanKinhMt',...
            'MtLaDuongThang','yd_Peak','yd_Cuoi','S_low_max',...
            'y_ss_theory','ess_theory','max_Re_pole_Tcl','max_Re_pole_all_channels','IAE_d','ISE_d','ITAE_d',...
            'ServoGood','RegulatorGood','RobustGood','RobustAcceptable','Robustness','Orientation','PerformanceScore','RobustnessScore','ControlObjective'});
        if isempty(BangBai), BangBai = row;
        else, BangBai = [BangBai; row]; end %#ok<AGROW>

        %% 8 - Ve tuong tu huong dan (Step, Bode, Nyquist, |S|/|T|)
        if VeDoThi && OnDinh
            figure(hTong); plot(tt,y,'LineWidth',1.2,'DisplayName',Ten);
            hienThi = chonHienThi(HienThiDoThi);

            h1 = figure('Color','w','Visible',hienThi,'Position',[50 50 900 650]);
            subplot(2,1,1);
            plot(tt,r,'k--',tt,y,'b','LineWidth',1.4); grid on;
            xlabel('t [s]'); ylabel('y(t)');
            title(sprintf('Bai %d %s - Step',bai,Ten),'Interpreter','none');
            legend('r(t)=1','y(t)','Location','best');
            subplot(2,1,2); plot(tt,e,'r','LineWidth',1.3); grid on;
            xlabel('t [s]'); ylabel('e(t)=r(t)-y(t)'); title('Sai lech dieu khien');
            luuHinh(h1,ThuMucBai,[Ten '_01_Step_va_SaiSo.png'],HienThiDoThi);

            h2 = figure('Color','w','Visible',hienThi,'Position',[60 60 900 650]);
            margin(L0); grid on;
            title(sprintf('Bai %d %s - Bode / du tru GM PM',bai,Ten),'Interpreter','none');
            luuHinh(h2,ThuMucBai,[Ten '_02_Bode_GM_PM.png'],HienThiDoThi);

            h3 = figure('Color','w','Visible',hienThi,'Position',[70 70 1300 760]);
            Ljw = squeeze(freqresp(L0,w)); Ljw=Ljw(:)';
            phi = linspace(0,2*pi,1600);
            for iz=1:2
                subplot(1,2,iz); hold on; grid on; box on;
                plot(real(Ljw),imag(Ljw),'b','LineWidth',1.3,'DisplayName','Nyquist: w>0');
                plot(real(Ljw),-imag(Ljw),'b:','LineWidth',1.0,'DisplayName','Nyquist: w<0');
                plot(-1,0,'rx','MarkerSize',10,'LineWidth',2,'DisplayName','Diem toi han (-1,0)');
                plot(Cs+Rs*cos(phi),Rs*sin(phi),'m--','LineWidth',1.5,'DisplayName','Vong Ms');
                if MtLaDuongThang
                    xline(-0.5,'g--','DisplayName','Mt xap xi 1: Re(L0)=-0.5');
                else
                    % Tang mat do mau gan goc 0 khi vong Mt co ban kinh lon.
                    phiMt = unique([phi,linspace(-min(pi,5/Rt),min(pi,5/Rt),1600)]);
                    plot(Ct+Rt*cos(phiMt),Rt*sin(phiMt),'g--','LineWidth',1.2,'DisplayName','Vong Mt');
                end
                if isfinite(wMs) && wMs>0
                    pMs=squeeze(freqresp(L0,wMs));
                    plot(real(pMs),imag(pMs),'mo','MarkerFaceColor','m','DisplayName','L0(j omegaMs)');
                end
                if isfinite(wMt) && wMt>0
                    pMt=squeeze(freqresp(L0,wMt));
                    plot(real(pMt),imag(pMt),'gs','MarkerFaceColor','g','DisplayName','L0(j omegaMt)');
                elseif wMt==0
                    % Vong ho co tich phan: L0(j0) o vo cuc, khong co diem huu han.
                    text(0.02,0.96,'Mt tai DC: L0(j0) o vo cuc', ...
                        'Units','normalized','Interpreter','none','FontSize',9);
                end
                if isfinite(wPi) && wPi>0
                    pGM=squeeze(freqresp(L0,wPi));
                    plot(real(pGM),imag(pGM),'kd','MarkerFaceColor','y','DisplayName',sprintf('omegaPi: GM=%.3g (%.2f dB)',GM,GMdB));
                    plot([-1 real(pGM)],[0 imag(pGM)],'k-.','HandleVisibility','off');
                end
                if isfinite(wC) && wC>0
                    pPM=squeeze(freqresp(L0,wC));
                    plot(cos(phi),sin(phi),'Color',[0.7 0.7 0.7],'LineStyle',':', ...
                        'DisplayName','Vong don vi');
                    plot(real(pPM),imag(pPM),'k^','MarkerFaceColor','c','DisplayName','omegaC: |L0|=1');
                    plot([0 real(pPM)],[0 imag(pPM)],'c-.','HandleVisibility','off');
                    phaCung=linspace(-pi,-pi+PM*pi/180,120);
                    plot(0.7*cos(phaCung),0.7*sin(phaCung),'c','LineWidth',2, ...
                        'DisplayName',sprintf('Cung PM=%.2f deg',PM));
                end
                axis equal;
                if iz==2
                    lim = max(2.0,3*Rs);
                    xlim([-1-lim -1+lim]); ylim([-lim lim]);
                    title('Phong to: diem toi han (-1,0)');
                else
                    title('Toan canh (nhanh tan so thap co the rat lon)');
                end
                xlabel('Re L0(jw)');ylabel('Im L0(jw)');
                if iz==2, legend('Location','southoutside','Interpreter','none','FontSize',8); end
            end
            luuHinh(h3,ThuMucBai,[Ten '_03_Nyquist_Ms_Mt.png'],HienThiDoThi);

            h4 = figure('Color','w','Visible',hienThi,'Position',[80 80 900 650]);
            subplot(2,1,1);
            semilogx(w,20*log10(max(abs(Sw),1e-12)),'m','LineWidth',1.4);
            grid on; xlabel('omega [rad/s]'); ylabel('20log10|S| [dB]');
            yline(Ms_dB,'k--');
            if isfinite(wMs)&&wMs>0, xline(wMs,'k:'); end
            title(sprintf('S: Ms=%.4f, omegaMs=%.4g',Ms,wMs));
            subplot(2,1,2);
            semilogx(w,20*log10(max(abs(Tw),1e-12)),'g','LineWidth',1.4);
            grid on; xlabel('omega [rad/s]'); ylabel('20log10|T| [dB]');
            yline(Mt_dB,'k--');
            if isfinite(wMt)&&wMt>0, xline(wMt,'k:'); end
            title(sprintf('T: Mt=%.4f, omegaMt=%.4g (0=DC)',Mt,wMt));
            luuHinh(h4,ThuMucBai,[Ten '_04_DoNhay_S_T.png'],HienThiDoThi);

            h5 = figure('Color','w','Visible',hienThi,'Position',[90 90 800 450]);
            plot(td,yd,'LineWidth',1.4); grid on;
            xlabel('t [s]'); ylabel('y_d(t)');
            title(sprintf('Bai %d %s - Nhieu buoc o dau vao G',bai,Ten),'Interpreter','none');
            luuHinh(h5,ThuMucBai,[Ten '_05_Regulator_NhieuTai.png'],HienThiDoThi);
        end
    end

    if VeDoThi
        figure(hTong);
        xlabel('t [s]');ylabel('y(t)');title(sprintf('Bai %d - so sanh PI/PID',bai));
        legend('Location','best','Interpreter','none');
        luuHinh(hTong,ThuMucBai,'00_So_Sanh_Step.png',HienThiDoThi);
    end
    fprintf('\nVII. BANG TONG HOP RIENG BAI %d\n',bai);
    disp(BangBai);
    % So sanh dinh luong: khong ket luan mot phuong phap luon tot nhat.
    idxStable = find(BangBai.OnDinh);
    if ~isempty(idxStable)
        [~,j]=min(BangBai.tr_s(idxStable)); ii=idxStable(j);
        fprintf('tr nho nhat: %s (%.7g s).\n',BangBai.BoDieuKhien{ii},BangBai.tr_s(ii));
        [~,j]=min(BangBai.ts_s(idxStable)); ii=idxStable(j);
        fprintf('ts nho nhat: %s (%.7g s).\n',BangBai.BoDieuKhien{ii},BangBai.ts_s(ii));
        [~,j]=min(BangBai.Mp_pct(idxStable)); ii=idxStable(j);
        fprintf('Mp nho nhat: %s (%.7g %%).\n',BangBai.BoDieuKhien{ii},BangBai.Mp_pct(ii));
        [~,j]=min(BangBai.Ms(idxStable)); ii=idxStable(j);
        fprintf('Ms nho nhat / lambda lon nhat: %s (Ms=%.7g; lambda=%.7g).\n', ...
            BangBai.BoDieuKhien{ii},BangBai.Ms(ii),BangBai.lambda(ii));
    end
    fprintf('Doi chieu dong thoi tr, ts, Mp, IAE, Ms, Mt, GM, PM; khong chi chon Kp lon.\n');
    fprintf('Quy uoc de bai: Haalman_PID_Td0 = Haalman_PI (Kp, Ti va moi chi tieu trung nhau).\n');
    fprintf('Chi 7 thiet ke doc lap; Haalman PID suy bien khong tao them mot dong so sanh.\n');
    writetable(BangBai,fullfile(ThuMucBai,sprintf('Bang_Ket_Qua_Bai_%02d.csv',bai)));
    save(fullfile(ThuMucBai,sprintf('Ket_Qua_Bai_%02d.mat',bai)),...
        'BangBai','K','T','Ltre','PadeBac');
    if isempty(KetQuaTatCa)
        BangBai.Bai = repmat(bai,height(BangBai),1);
        KetQuaTatCa = BangBai;
    else
        BangBai.Bai = repmat(bai,height(BangBai),1);
        KetQuaTatCa = [KetQuaTatCa; BangBai]; %#ok<AGROW>
    end
    diary off;
end

% Moi file co ten tong hop rieng, tranh ghi de bang khi chay bai khac.
writetable(KetQuaTatCa,fullfile(ThuMucGoc,sprintf('Tong_Hop_Lan_Chay_Bai_%02d.csv',baiCanGiai(1))));
fprintf('\nHOAN THANH. Thu muc ket qua: %s\n',ThuMucGoc);
% ================= CAC HAM PHU DANG TREN CUNG FILE ===============
function [Kp,Ti,Td] = chinhDinh(K,T,Ltre,Ten)
    A = T/(K*Ltre); % Giu dau K: bai 8 co K AM thi Kp cung AM
    rho = Ltre/T;
    switch Ten
        case 'ZN_PI'
            Kp=0.9*A; Ti=3.33*Ltre; Td=0;
        case 'ZN_PID'
            Kp=1.2*A; Ti=2*Ltre; Td=0.5*Ltre;
        case 'Haalman_PI'
            Kp=(2/3)*A; Ti=T; Td=0;
        case 'CHR_PI'
            Kp=0.35*A; Ti=1.2*T; Td=0;
        case 'CHR_PID'
            Kp=0.6*A; Ti=T; Td=0.5*Ltre;
        case 'CC_PI'
            Kp=A*(0.9+rho/12);
            Ti=Ltre*(30+3*rho)/(9+20*rho); Td=0;
        case 'CC_PID'
            Kp=A*(4/3+rho/4);
            Ti=Ltre*(32+6*rho)/(13+8*rho);
            Td=4*Ltre/(11+2*rho);
        otherwise
            error('Ten bo dieu khien khong hop le: %s',Ten);
    end
end

function v = chonHienThi(coHienThi)
    if coHienThi, v='on'; else, v='off'; end
end

function luuHinh(h,thuMuc,tenFile,coHienThi)
    saveas(h,fullfile(thuMuc,tenFile));
    if ~coHienThi, close(h); end
end
