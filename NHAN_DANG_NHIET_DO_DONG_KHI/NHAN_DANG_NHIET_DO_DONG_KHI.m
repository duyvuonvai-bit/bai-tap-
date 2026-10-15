%% NHẬN DẠNG HỆ THỐNG ỔN ĐỊNH NHIỆT ĐỘ DÒNG KHÍ
% MATLAB R2018b trở lên; chạy độc lập bằng nút Run.
% Không bắt buộc Control System Toolbox hoặc Optimization Toolbox.
% Mô hình bậc nhất có trễ: G(s) = K*exp(-L*s)/(tau*s + 1).
% Đầu vào của G là BIẾN THIÊN PWM; đầu ra là BIẾN THIÊN nhiệt độ.
% Giả thiết: thời gian tính bằng giây; bước PWM đặt tại t = 0 s.
% Delta PWM = 55 ĐIỂM PHẦN TRĂM, không phải 55% của một giá trị PWM khác.
% T0 = 29.2 độ C; T xác lập = 44.3 độ C là thông số người dùng cung cấp.
% Không thay số đo cuối bằng 44.3 và không làm trơn dữ liệu để nhận dạng.
%
% Người dùng đã xác nhận các điểm t = 290, 360, 370, 380, 430, 460,
% 470, 590, 870, 950 s. Một số nét ở 20, 150, 260, 340, 350 s còn
% khó đọc; mảng dưới giữ bản phiên âm hiện tại để có thể sửa và chạy lại.
% Độ trễ nhận dạng từ mô hình không có độ chính xác thực nghiệm 0.001 s:
% chu kỳ lấy mẫu của bộ số liệu là 10 s.
%
% Hai hình PNG/PDF, bảng CSV và kết quả TXT được ghi vào thư mục
% KET_QUA_MATLAB nằm cạnh file .m này. Các cửa sổ hình đang mở được giữ lại.
% Script đã được kiểm tra cú pháp; cần chạy thực tế trong MATLAB để xác nhận.

clearvars;
clc;

%% 1. SỐ LIỆU GỐC: [thời gian (s), nhiệt độ (độ C)]
du_lieu = [ ...
      0 29.2;   10 29.2;   20 29.6;   30 29.4;   40 30.3;   50 30.6;
     60 30.7;   70 31.7;   80 32.3;   90 32.8;  100 33.6;  110 33.5;
    120 34.6;  130 35.0;  140 35.3;  150 36.6;  160 36.0;  170 37.0;
    180 37.5;  190 37.3;  200 38.0;  210 38.3;  220 38.6;  230 39.3;
    240 39.3;  250 39.8;  260 39.9;  270 39.3;  280 40.3;  290 41.1;
    300 40.9;  310 41.0;  320 41.0;  330 41.5;  340 41.9;  350 41.4;
    360 42.0;  370 42.9;  380 42.9;  390 42.6;  400 42.2;  410 42.6;
    420 42.0;  430 42.9;  440 42.3;  450 42.3;  460 42.0;  470 41.8;
    480 42.3;  490 42.2;  500 42.3;  510 42.7;  520 42.9;  530 43.0;
    540 42.5;  550 42.4;  560 43.3;  570 43.4;  580 43.1;  590 42.5;
    600 43.3;  610 42.6;  620 43.5;  630 42.9;  640 43.0;  650 42.3;
    660 43.4;  670 43.5;  680 43.5;  690 43.2;  700 43.8;  710 43.7;
    720 43.5;  730 44.0;  740 44.2;  750 43.8;  760 44.3;  770 44.1;
    780 44.2;  790 44.3;  800 43.8;  810 44.1;  820 44.2;  830 43.8;
    840 44.0;  850 43.7;  860 44.0;  870 43.7;  880 43.6;  890 43.2;
    900 43.6;  910 44.7;  920 44.0;  930 44.0;  940 44.5;  950 42.5];

thoi_gian = du_lieu(:, 1);
nhiet_do_thuc_nghiem = du_lieu(:, 2);
so_mau = numel(thoi_gian);
assert(so_mau == 96, 'Bộ số liệu phải có đủ 96 mẫu.');
assert(all(diff(thoi_gian) == 10), 'Chu kỳ lấy mẫu phải bằng 10 s.');

nhiet_do_ban_dau = 29.2;
nhiet_do_xac_lap = 44.3;
do_tang_nhiet_do = nhiet_do_xac_lap - nhiet_do_ban_dau;
bien_thien_pwm_phan_tram = 55;
bien_thien_pwm_chuan_hoa = bien_thien_pwm_phan_tram / 100;
he_so_khuech_dai = do_tang_nhiet_do / bien_thien_pwm_phan_tram;
he_so_khuech_dai_chuan_hoa = do_tang_nhiet_do / bien_thien_pwm_chuan_hoa;

%% 2. BÌNH PHƯƠNG TỐI THIỂU VỚI K VÀ HAI NHIỆT ĐỘ CỐ ĐỊNH
% T_m(t) = T0 + (T_xac_lap - T0)*(1 - exp(-max(t-L,0)/tau)).
% Không thay đổi K trong quá trình tìm tau và L.
% fminsearch dùng [log(tau), L]; kiểm tra miền để tau > 0, L >= 0.
% Giới hạn số rộng: 0.001 <= tau <= 100*950 s; 0 <= L < 950 s.
% Nhiều điểm khởi tạo giảm phụ thuộc giá trị đoán ban đầu.
% Kiểm tra riêng nghiệm biên L = 0 bằng fminbnd trên log(tau).

gioi_han_tau = [0.001, 100 * thoi_gian(end)];
gioi_han_tre = thoi_gian(end);
tuy_chon = optimset('Display', 'off', 'TolX', 1e-10, ...
    'TolFun', 1e-10, 'MaxFunEvals', 12000, 'MaxIter', 6000);

ham_sai_so = @(tham_so) tinh_tong_sai_so(tham_so, thoi_gian, ...
    nhiet_do_thuc_nghiem, nhiet_do_ban_dau, do_tang_nhiet_do, ...
    gioi_han_tau, gioi_han_tre);

[log_tau_khong_tre, tong_sai_so_tot_nhat] = fminbnd( ...
    @(log_tau) ham_sai_so([log_tau, 0]), ...
    log(gioi_han_tau(1)), log(gioi_han_tau(2)), tuy_chon);
tham_so_tot_nhat = [log_tau_khong_tre, 0];
so_lan_hoi_tu = 0;

for tau_ban_dau = [60, 200, 600, 1500]
    for tre_ban_dau = [0, 10, 30, 60, 120]
        [tham_so_thu, tong_sai_so_thu, ma_ket_thuc] = fminsearch( ...
            ham_sai_so, [log(tau_ban_dau), tre_ban_dau], tuy_chon);
        if ma_ket_thuc > 0
            so_lan_hoi_tu = so_lan_hoi_tu + 1;
        end
        if isfinite(tong_sai_so_thu) && ...
                tong_sai_so_thu < tong_sai_so_tot_nhat
            tham_so_tot_nhat = tham_so_thu;
            tong_sai_so_tot_nhat = tong_sai_so_thu;
        end
    end
end

hang_so_thoi_gian = exp(tham_so_tot_nhat(1));
thoi_gian_tre = tham_so_tot_nhat(2);
assert(hang_so_thoi_gian > 0 && thoi_gian_tre >= 0, ...
    'Tham số nhận dạng nằm ngoài miền vật lý.');
nhiet_do_mo_hinh = tinh_dap_ung(thoi_gian, nhiet_do_ban_dau, ...
    do_tang_nhiet_do, hang_so_thoi_gian, thoi_gian_tre);
sai_so = nhiet_do_thuc_nghiem - nhiet_do_mo_hinh;
sai_so_rmse = sqrt(mean(sai_so .^ 2));
sai_so_trung_binh_tuyet_doi = mean(abs(sai_so));

fprintf('\nNHẬN DẠNG NHIỆT ĐỘ DÒNG KHÍ - %d MẪU\n', so_mau);
fprintf('Delta T = %.4f độ C; Delta PWM = %.4f điểm phần trăm.\n', ...
    do_tang_nhiet_do, bien_thien_pwm_phan_tram);
fprintf('K = %.9f độ C/(điểm phần trăm PWM).\n', he_so_khuech_dai);
fprintf('tau = %.6f s; L = %.6f s.\n', hang_so_thoi_gian, thoi_gian_tre);
fprintf('G(s) = %.9f * exp(-%.6f*s) / (%.6f*s + 1).\n', ...
    he_so_khuech_dai, thoi_gian_tre, hang_so_thoi_gian);
fprintf('Nếu PWM dùng thang 0..1: K = %.9f độ C.\n', ...
    he_so_khuech_dai_chuan_hoa);
fprintf('RMSE = %.7f độ C, tính trên toàn bộ %d số đo.\n', sai_so_rmse, so_mau);
fprintf('Số lần fminsearch báo hội tụ: %d/20.\n', so_lan_hoi_tu);

%% 3. THƯ MỤC XUẤT KẾT QUẢ
thu_muc_ma = fileparts(mfilename('fullpath'));
if isempty(thu_muc_ma)
    thu_muc_ma = pwd;
end
thu_muc_ket_qua = fullfile(thu_muc_ma, 'KET_QUA_MATLAB');
if ~exist(thu_muc_ket_qua, 'dir')
    mkdir(thu_muc_ket_qua);
end

%% 4. HÌNH 1: ĐẶC TÍNH THỰC NGHIỆM
hinh_thuc_nghiem = figure('Name', 'Đặc tính thực nghiệm', ...
    'Color', 'w', 'Position', [80, 100, 1050, 620]);
truc_thuc_nghiem = axes('Parent', hinh_thuc_nghiem);
plot(truc_thuc_nghiem, thoi_gian, nhiet_do_thuc_nghiem, '-o', ...
    'Color', [0.1, 0.25, 0.50], 'LineWidth', 1.35, 'MarkerSize', 3.5, ...
    'MarkerFaceColor', [0.1, 0.25, 0.50]);
grid(truc_thuc_nghiem, 'on');
box(truc_thuc_nghiem, 'on');
set(truc_thuc_nghiem, 'FontName', 'Arial', 'FontSize', 11);
xlim(truc_thuc_nghiem, [0, 950]);
ylim(truc_thuc_nghiem, [28, 46]);
xlabel(truc_thuc_nghiem, 'Thời gian (s)');
ylabel(truc_thuc_nghiem, 'Nhiệt độ (°C)');
title(truc_thuc_nghiem, ...
    {'Đặc tính thực nghiệm của hệ thống ổn định nhiệt độ dòng khí'; ...
     '96 mẫu; chu kỳ lấy mẫu 10 s; bước PWM = 55 điểm phần trăm'});
set(hinh_thuc_nghiem, 'PaperPositionMode', 'auto');
print(hinh_thuc_nghiem, fullfile(thu_muc_ket_qua, ...
    '01_DAC_TINH_THUC_NGHIEM.png'), '-dpng', '-r200');
print(hinh_thuc_nghiem, fullfile(thu_muc_ket_qua, ...
    '01_DAC_TINH_THUC_NGHIEM.pdf'), '-dpdf', '-bestfit');

%% 5. HÌNH 2: SO SÁNH SỐ ĐO VÀ ĐÁP ỨNG MÔ HÌNH
thoi_gian_ve = (0:1:thoi_gian(end))';
nhiet_do_mo_hinh_ve = tinh_dap_ung(thoi_gian_ve, nhiet_do_ban_dau, ...
    do_tang_nhiet_do, hang_so_thoi_gian, thoi_gian_tre);
hinh_so_sanh = figure('Name', 'So sánh thực nghiệm và mô hình FOPDT', ...
    'Color', 'w', 'Position', [120, 140, 1050, 620]);
truc_so_sanh = axes('Parent', hinh_so_sanh);
duong_thuc_nghiem = plot(truc_so_sanh, thoi_gian, nhiet_do_thuc_nghiem, ...
    '-o', 'Color', [0.1, 0.25, 0.50], 'LineWidth', 1.25, ...
    'MarkerSize', 3, 'MarkerFaceColor', [0.1, 0.25, 0.50]);
hold(truc_so_sanh, 'on');
duong_mo_hinh = plot(truc_so_sanh, thoi_gian_ve, nhiet_do_mo_hinh_ve, ...
    '--', 'Color', [0.85, 0.25, 0.10], 'LineWidth', 2.0);
grid(truc_so_sanh, 'on');
box(truc_so_sanh, 'on');
set(truc_so_sanh, 'FontName', 'Arial', 'FontSize', 11);
xlim(truc_so_sanh, [0, 950]);
ylim(truc_so_sanh, [28, 46]);
xlabel(truc_so_sanh, 'Thời gian (s)');
ylabel(truc_so_sanh, 'Nhiệt độ (°C)');
title(truc_so_sanh, 'So sánh đáp ứng thực nghiệm và mô hình FOPDT');
legend(truc_so_sanh, [duong_thuc_nghiem, duong_mo_hinh], ...
    {'Dữ liệu thực nghiệm', 'Đáp ứng mô hình FOPDT'}, 'Location', 'southeast');
text(truc_so_sanh, 0.55, 0.25, sprintf( ...
    'RMSE = %.4f °C\nK = %.6f °C/(điểm %% PWM)\ntau = %.3f s; L = %.3f s', ...
    sai_so_rmse, he_so_khuech_dai, hang_so_thoi_gian, thoi_gian_tre), ...
    'Units', 'normalized', 'BackgroundColor', 'w', 'EdgeColor', [0.5 0.5 0.5], ...
    'Margin', 8, 'FontName', 'Arial', 'FontSize', 11);
hold(truc_so_sanh, 'off');
set(hinh_so_sanh, 'PaperPositionMode', 'auto');
print(hinh_so_sanh, fullfile(thu_muc_ket_qua, ...
    '02_SO_SANH_THUC_NGHIEM_MO_HINH.png'), '-dpng', '-r200');
print(hinh_so_sanh, fullfile(thu_muc_ket_qua, ...
    '02_SO_SANH_THUC_NGHIEM_MO_HINH.pdf'), '-dpdf', '-bestfit');

%% 6. XUẤT BẢNG DỮ LIỆU VÀ KẾT QUẢ BẰNG VĂN BẢN
bang_ket_qua = table(thoi_gian, nhiet_do_thuc_nghiem, nhiet_do_mo_hinh, ...
    sai_so, 'VariableNames', {'Thoi_gian_s', 'Nhiet_do_thuc_nghiem_C', ...
    'Nhiet_do_mo_hinh_C', 'Sai_so_C'});
writetable(bang_ket_qua, fullfile(thu_muc_ket_qua, 'DU_LIEU_VA_DAP_UNG.csv'));
ghi_ket_qua(fullfile(thu_muc_ket_qua, 'KET_QUA_NHAN_DANG.txt'), ...
    he_so_khuech_dai, he_so_khuech_dai_chuan_hoa, hang_so_thoi_gian, ...
    thoi_gian_tre, sai_so_rmse, sai_so_trung_binh_tuyet_doi, ...
    so_mau, nhiet_do_ban_dau, nhiet_do_xac_lap, bien_thien_pwm_phan_tram);

%% 7. TÙY CHỌN: TẠO ĐỐI TƯỢNG HÀM TRUYỀN KHI CÓ TOOLBOX
% Hình ở trên dùng công thức chính xác, không dùng xấp xỉ Pade.
% step(ham_truyen) chỉ là bước PWM 1 điểm phần trăm và cho Delta T.
% Muốn nhiệt độ tuyệt đối cho bước 55 điểm phần trăm phải cộng T0:
% nhiet_do_ban_dau + step(bien_thien_pwm_phan_tram*ham_truyen, thoi_gian).
if exist('tf', 'file') == 2 && license('test', 'Control_Toolbox')
    try
        ham_truyen = tf(he_so_khuech_dai, [hang_so_thoi_gian, 1], ...
            'InputDelay', thoi_gian_tre, 'TimeUnit', 'seconds');
        disp(ham_truyen);
    catch loi_ham_truyen
        fprintf('Không tạo đối tượng tf: %s\n', loi_ham_truyen.message);
    end
end
fprintf('\nĐã ghi kết quả vào: %s\n', thu_muc_ket_qua);
fprintf('Hai đồ thị giữ nguyên nhiễu và số đo 42.5 độ C tại 950 s.\n');

%% HÀM CỤC BỘ - ĐẶT CUỐI SCRIPT ĐỂ TƯƠNG THÍCH MATLAB R2018b
function nhiet_do = tinh_dap_ung(thoi_gian, nhiet_do_dau, ...
        do_tang_nhiet, hang_so_thoi_gian, thoi_gian_tre)
    thoi_gian_hieu_dung = max(thoi_gian - thoi_gian_tre, 0);
    nhiet_do = nhiet_do_dau + do_tang_nhiet .* ...
        (1 - exp(-thoi_gian_hieu_dung ./ hang_so_thoi_gian));
end

function tong_sai_so = tinh_tong_sai_so(tham_so, thoi_gian, ...
        nhiet_do_do, nhiet_do_dau, do_tang_nhiet, gioi_han_tau, gioi_han_tre)
    if any(~isfinite(tham_so))
        tong_sai_so = 1e100;
        return;
    end
    khoang_vi_pham = max(log(gioi_han_tau(1)) - tham_so(1), 0) + ...
        max(tham_so(1) - log(gioi_han_tau(2)), 0) + ...
        max(-tham_so(2), 0) + max(tham_so(2) - gioi_han_tre, 0);
    if khoang_vi_pham > 0 || tham_so(2) >= gioi_han_tre
        tong_sai_so = 1e9 + 1e6 * khoang_vi_pham .^ 2;
        return;
    end
    nhiet_do_uoc_luong = tinh_dap_ung(thoi_gian, nhiet_do_dau, ...
        do_tang_nhiet, exp(tham_so(1)), tham_so(2));
    tong_sai_so = sum((nhiet_do_do - nhiet_do_uoc_luong) .^ 2);
end

function ghi_ket_qua(duong_dan, he_so_khuech_dai, he_so_chuan_hoa, ...
        hang_so_thoi_gian, thoi_gian_tre, sai_so_rmse, sai_so_tuyet_doi, ...
        so_mau, nhiet_do_dau, nhiet_do_cuoi, bien_thien_pwm)
    tep = fopen(duong_dan, 'w', 'n', 'UTF-8');
    if tep < 0
        error('Không tạo được tệp kết quả: %s', duong_dan);
    end
    don_dep_tep = onCleanup(@() fclose(tep)); %#ok<NASGU>
    fprintf(tep, 'NHẬN DẠNG HỆ THỐNG ỔN ĐỊNH NHIỆT ĐỘ DÒNG KHÍ\n\n');
    fprintf(tep, 'Số mẫu: %d; thời gian 0..950 s; chu kỳ lấy mẫu 10 s.\n', so_mau);
    fprintf(tep, 'T0 = %.4f độ C; T xác lập cho trước = %.4f độ C.\n', ...
        nhiet_do_dau, nhiet_do_cuoi);
    fprintf(tep, 'Giả thiết bước PWM = %.4f điểm phần trăm đặt tại t = 0 s.\n', ...
        bien_thien_pwm);
    fprintf(tep, 'G(s) = %.9f*exp(-%.6f*s)/(%.6f*s + 1).\n', ...
        he_so_khuech_dai, thoi_gian_tre, hang_so_thoi_gian);
    fprintf(tep, 'G: Delta PWM (điểm phần trăm) -> Delta T (độ C).\n');
    fprintf(tep, 'Nếu PWM dùng thang 0..1 thì K = %.9f độ C.\n', he_so_chuan_hoa);
    fprintf(tep, 'T_m(t) = %.4f + %.4f*(1-exp(-max(t-%.6f,0)/%.6f)).\n', ...
        nhiet_do_dau, nhiet_do_cuoi - nhiet_do_dau, thoi_gian_tre, hang_so_thoi_gian);
    fprintf(tep, 'RMSE trên toàn bộ %d số đo = %.9f độ C.\n', so_mau, sai_so_rmse);
    fprintf(tep, 'Sai số tuyệt đối trung bình = %.9f độ C.\n', sai_so_tuyet_doi);
    fprintf(tep, '\nK cố định; tau và L tìm bằng bình phương tối thiểu nhiều khởi tạo.\n');
    fprintf(tep, 'Không làm trơn; giữ số đo 42.5 độ C tại 950 s.\n');
    fprintf(tep, 'RMSE là sai số khớp trên bộ dữ liệu nhận dạng, chưa phải kiểm chứng độc lập.\n');
    fprintf(tep, 'Các nét ảnh tại 20, 150, 260, 340, 350 s còn khó đọc.\n');
    fprintf(tep, 'Các chữ số thập phân của tau, L không thể hiện độ chính xác đo.\n');
end
