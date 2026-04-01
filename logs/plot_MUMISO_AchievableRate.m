%% Start
% This script is a scratch pad to plot data from MU-MISO_AchievableRate/
clear all; close all; delete(gcp('nocreate')); clc;

%% Figure 1-5, Load Data and Plot parameters
% Colours
% green = [27,158,119]./255;
% orange = [217,95,2]./255;
% purple = [117,112,179]./255;
% brown = [165,42,42]./255;
% blue = [51,51,255]./255;
% magenta = [255, 0, 255]./255;
% indigo = [75,0,130]./255;
% red = [255, 0, 0]./255;

% https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=6
colour_list = {...
    [27,158,119]./255, ...
    [217,95,2]./255, ...
    [117,112,179]./255, ...
    [231,41,138]./255, ...
    [102,166,30]./255, ...
    [230,171,2]./255 ...
};

linewidth = 1.5;

marker_list = {'p', '^', 'v', 'o', 's', '+'};

dir = "MU-MISO_AchievableRateExperiments/";
% results = zeros(6,11,7);
% opts = detectImportOptions(dir + trial + "/10PdBm/results.csv");
% NetNames = strrep(strrep(opts.VariableNames, 'R_', ''),'_',' ');

% % Single Trial - submitted results
% trial = "plot";
% results_10PdBm = readmatrix(dir + trial + "/10PdBm/results.csv");
% results_15PdBm = readmatrix(dir + trial + "/15PdBm/results.csv");
% results_20PdBm = readmatrix(dir + trial + "/20PdBm/results.csv");
% results_25PdBm = readmatrix(dir + trial + "/25PdBm/results.csv");
% results_30PdBm = readmatrix(dir + trial + "/30PdBm/results.csv");
% results_35PdBm = readmatrix(dir + trial + "/35PdBm/results.csv");
% results_40PdBm = readmatrix(dir + trial + "/40PdBm/results.csv");

% Multiple Trial - resubmitted results
% trials = "repeated_trial_00";
trials = "PerfectCSI/repeated_trial_02";
results_10PdBm00 = readmatrix(dir + trials + "/00/10PdBm/results.csv");
results_15PdBm00 = readmatrix(dir + trials + "/00/15PdBm/results.csv");
results_20PdBm00 = readmatrix(dir + trials + "/00/20PdBm/results.csv");
results_25PdBm00 = readmatrix(dir + trials + "/00/25PdBm/results.csv");
results_30PdBm00 = readmatrix(dir + trials + "/00/30PdBm/results.csv");
results_35PdBm00 = readmatrix(dir + trials + "/00/35PdBm/results.csv");
results_40PdBm00 = readmatrix(dir + trials + "/00/40PdBm/results.csv");
results_10PdBm01 = readmatrix(dir + trials + "/01/10PdBm/results.csv");
results_15PdBm01 = readmatrix(dir + trials + "/01/15PdBm/results.csv");
results_20PdBm01 = readmatrix(dir + trials + "/01/20PdBm/results.csv");
results_25PdBm01 = readmatrix(dir + trials + "/01/25PdBm/results.csv");
results_30PdBm01 = readmatrix(dir + trials + "/01/30PdBm/results.csv");
results_35PdBm01 = readmatrix(dir + trials + "/01/35PdBm/results.csv");
results_40PdBm01 = readmatrix(dir + trials + "/01/40PdBm/results.csv");
results_10PdBm02 = readmatrix(dir + trials + "/02/10PdBm/results.csv");
results_15PdBm02 = readmatrix(dir + trials + "/02/15PdBm/results.csv");
results_20PdBm02 = readmatrix(dir + trials + "/02/20PdBm/results.csv");
results_25PdBm02 = readmatrix(dir + trials + "/02/25PdBm/results.csv");
results_30PdBm02 = readmatrix(dir + trials + "/02/30PdBm/results.csv");
results_35PdBm02 = readmatrix(dir + trials + "/02/35PdBm/results.csv");
results_40PdBm02 = readmatrix(dir + trials + "/02/40PdBm/results.csv");
results_10PdBm03 = readmatrix(dir + trials + "/03/10PdBm/results.csv");
results_15PdBm03 = readmatrix(dir + trials + "/03/15PdBm/results.csv");
results_20PdBm03 = readmatrix(dir + trials + "/03/20PdBm/results.csv");
results_25PdBm03 = readmatrix(dir + trials + "/03/25PdBm/results.csv");
results_30PdBm03 = readmatrix(dir + trials + "/03/30PdBm/results.csv");
results_35PdBm03 = readmatrix(dir + trials + "/03/35PdBm/results.csv");
results_40PdBm03 = readmatrix(dir + trials + "/03/40PdBm/results.csv");
results_10PdBm04 = readmatrix(dir + trials + "/04/10PdBm/results.csv");
results_15PdBm04 = readmatrix(dir + trials + "/04/15PdBm/results.csv");
results_20PdBm04 = readmatrix(dir + trials + "/04/20PdBm/results.csv");
results_25PdBm04 = readmatrix(dir + trials + "/04/25PdBm/results.csv");
results_30PdBm04 = readmatrix(dir + trials + "/04/30PdBm/results.csv");
results_35PdBm04 = readmatrix(dir + trials + "/04/35PdBm/results.csv");
results_40PdBm04 = readmatrix(dir + trials + "/04/40PdBm/results.csv");

results_10PdBm_mean = (results_10PdBm00 + results_10PdBm01 + results_10PdBm02 + results_10PdBm03 + results_10PdBm04) / 5;
results_15PdBm_mean = (results_15PdBm00 + results_15PdBm01 + results_15PdBm02 + results_15PdBm03 + results_15PdBm04) / 5;
results_20PdBm_mean = (results_20PdBm00 + results_20PdBm01 + results_20PdBm02 + results_20PdBm03 + results_20PdBm04) / 5;
results_25PdBm_mean = (results_25PdBm00 + results_25PdBm01 + results_25PdBm02 + results_25PdBm03 + results_25PdBm04) / 5;
results_30PdBm_mean = (results_30PdBm00 + results_30PdBm01 + results_30PdBm02 + results_30PdBm03 + results_30PdBm04) / 5;
results_35PdBm_mean = (results_35PdBm00 + results_35PdBm01 + results_35PdBm02 + results_35PdBm03 + results_35PdBm04) / 5;
results_40PdBm_mean = (results_40PdBm00 + results_40PdBm01 + results_40PdBm02 + results_40PdBm03 + results_40PdBm04) / 5;

results_10PdBm_var = (results_10PdBm00.^2 + results_10PdBm01.^2 + results_10PdBm02.^2 + results_10PdBm03.^2 + results_10PdBm04.^2) / 5 - results_10PdBm_mean.^2;
results_15PdBm_var = (results_15PdBm00.^2 + results_15PdBm01.^2 + results_15PdBm02.^2 + results_15PdBm03.^2 + results_15PdBm04.^2) / 5 - results_15PdBm_mean.^2;
results_20PdBm_var = (results_20PdBm00.^2 + results_20PdBm01.^2 + results_20PdBm02.^2 + results_20PdBm03.^2 + results_20PdBm04.^2) / 5 - results_20PdBm_mean.^2;
results_25PdBm_var = (results_25PdBm00.^2 + results_25PdBm01.^2 + results_25PdBm02.^2 + results_25PdBm03.^2 + results_25PdBm04.^2) / 5 - results_25PdBm_mean.^2;
results_30PdBm_var = (results_30PdBm00.^2 + results_30PdBm01.^2 + results_30PdBm02.^2 + results_30PdBm03.^2 + results_30PdBm04.^2) / 5 - results_30PdBm_mean.^2;
results_35PdBm_var = (results_35PdBm00.^2 + results_35PdBm01.^2 + results_35PdBm02.^2 + results_35PdBm03.^2 + results_35PdBm04.^2) / 5 - results_35PdBm_mean.^2;
results_40PdBm_var = (results_40PdBm00.^2 + results_40PdBm01.^2 + results_40PdBm02.^2 + results_40PdBm03.^2 + results_40PdBm04.^2) / 5 - results_40PdBm_mean.^2;

results_10PdBm = results_10PdBm_mean;
results_15PdBm = results_15PdBm_mean;
results_20PdBm = results_20PdBm_mean;
results_25PdBm = results_25PdBm_mean;
results_30PdBm = results_30PdBm_mean;
results_35PdBm = results_35PdBm_mean;
results_40PdBm = results_40PdBm_mean;

NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
results = cat(3,results_10PdBm, results_15PdBm, results_20PdBm, ...
    results_25PdBm, results_30PdBm, results_35PdBm, results_40PdBm);


PdBm = [10, 15, 20, 25, 30, 35, 40];
sz = size(results);
ftsz = 20;

%% Figure 1 - Rate vs Tx, 100 control bits
b = 10;
c = 1;
m = 1;
l = 1;
qw = {};
figure(1);
for net = [2,3,4,5,7,6]
    qw{l} = plot(PdBm, squeeze(results(b,net,:)), '-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net}, 'LineWidth', linewidth);
    c = c+1;
    m = m+1;
    l = l+1;
    hold on;
end
c = 1;
m = 1;
for net = [8,9,10,11,13,12]
    plot(PdBm, squeeze(results(b,net,:)), '--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net}, 'LineWidth', linewidth)
    c = c+1;
    m = m+1;
end
hold off;
grid on;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('Achievable Sum Rate (bps/Hz)')
% legend('NumColumns', 2, 'location', 'best')
hold on;
qw{7} = plot(nan, 'k--', 'LineWidth', linewidth);
hold off;
legend([qw{:}], {'Upper Bound','AQE-WMMSE','AQE','ACFNet','linQ','DQNN','random'}, 'location', 'best')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 2 - Rate vs Tx, 10 & 40 control bits
% figure(2);
% b1 = 4; b2 = 1;
% m = 2;
% c = 2;
% qw = {};
% qw{1} = plot(PdBm, squeeze(results(b1,2,:)), '-', 'Color', colour_list{1}, 'Marker', marker_list{1}, 'DisplayName', strcat(NetNames{2}), 'LineWidth', linewidth);
% hold on;
% for net = [3,4,5,7]
%     plot(PdBm, squeeze(results(b1,net,:)), 'o-', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', strcat(NetNames{net}, " ", int2str(results(b1,1,1)), " bits"))
%     plot(PdBm, squeeze(results(b2,net,:)), '*--', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', strcat(NetNames{net}, " ", int2str(results(b2,1,1)), " bits"))
%     c = c+1;
%     m = m+1;
% end
% % b2 = 1;
% % c = 2;
% % m = 2;
% % for net = [3,4,5,7]
% %     plot(PdBm, squeeze(results(b,net,:)), '*--', 'Color', colour_list{c}, ...
% %         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
% %         'DisplayName', strcat(NetNames{net}, " (", int2str(results(b,1,1)), " bits)"))
% %     c = c+1;
% %     m = m+1;
% % end
% hold off;
% grid on;
% % title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
% xlabel('Transmit Power (dBm)')
% ylabel('Achievable Sum Rate (bps/Hz)')
% % legend('NumColumns', 1, 'location', 'northwest')
% hold on;
% qw{2} = plot(nan, 'k-', 'LineWidth', linewidth);
% qw{3} = plot(nan, 'k--', 'LineWidth', linewidth);
% hold off;
% legend([qw{:}], {'Upper Bound', '40 bits','10 bits'}, 'location', 'best')
% % legend([qw{:}], {'40 bits','10 bits'}, 'location', 'best')
% ylim([0, 16])
% fontsize(gca,ftsz,"pixels")

figure(2);
tiledlayout(2,2)
for b = 2:2:8
    nexttile
    m = 2;
    c = 2;
    qw = {};
    % qw{1} = plot(PdBm, squeeze(results(b1,2,:)), '-', 'Color', colour_list{1}, 'Marker', marker_list{1}, 'DisplayName', strcat(NetNames{2}), 'LineWidth', linewidth);
    hold on;
    for net = [3,4,5,7]
        plot(PdBm, squeeze(results(b,net,:)), '-', 'Color', colour_list{c}, ...
            'Marker', marker_list{m}, 'LineWidth', linewidth, ...
            'DisplayName', strcat(NetNames{net}, " ", int2str(results(b,1,1)), " bits"))
        c = c+1;
        m = m+1;
    end    
    hold off;
    grid on;
    xlabel('Transmit Power (dBm)')
    ylabel('ASR (bps/Hz)')
    hold on;
    qw{1} = plot(nan, 'k-', 'LineWidth', linewidth);
    hold off;
    legend([qw{:}], {strcat(int2str(b*10), ' bits')}, 'location', 'best')
    ylim([0, 16])
    yticks(0:3:16)
    fontsize(gca,ftsz,"pixels")
end

%% Figure 3 - Rate vs Bits, 40 & 15 Tx dBm
% bits = 1:10;
% mark = {'o-', '', '', '', '', '', '*-'};
% figure(3);
% p = 6; % 35 PdBm
% % p = 5; % 30 PdBm
% c = 2;
% m = 2;
% % for net = [2,3,4,5,7]
% for net = [3,4,5,7]
%     plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', strcat(NetNames{net}, " ", int2str(PdBm(p)), " dBm"))
%     c = c+1;
%     m = m+1;
%     hold on;
% end
% p = 2; % 15 PdBm
% c = 2;
% m = 2;
% % for net = [2,3,4,5,7]
% for net = [3,4,5,7]
%     plot(results(bits,1,1), squeeze(results(bits,net,p)), '*--', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', strcat(NetNames{net}, " ", int2str(PdBm(p)), " dBm"))
%     c = c+1;
%     m = m+1;
%     hold on;
% end
% hold off;
% set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
% % title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
% xlabel('Number of control bits')
% ylabel('Achievable Sum Rate (bps/Hz)')
% % legend('NumColumns', 2, 'location', 'best')
% hold on;
% qw = {};
% qw{1} = plot(nan, 'k-', 'LineWidth', linewidth);
% qw{2} = plot(nan, 'k--', 'LineWidth', linewidth);
% hold off;
% legend([qw{:}], {'35 PdBm','15 PdBm'}, 'location', 'best')
% axis tight
% ylim([0, 12])
% % set (gca, 'Xscale', 'log');
% % set(gca,'XTick', results(bits,1,1));
% fontsize(gca,ftsz,"pixels")
% xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

bits = 1:10;
figure(3);
% p = 6; % 35 PdBm
powers_list = ["10 PdBm", "15 PdBm", "20 PdBm", "25 PdBm", "30 PdBm", "35 PdBm", "40 PdBm"];

tiledlayout(2,2)
for p = 1:2:7
    nexttile
    c = 2;
    m = 2;
    % for net = [2,3,4,5,7]
    for net = [3,4,5,7]
        plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'Color', colour_list{c}, ...
            'Marker', marker_list{m}, 'LineWidth', linewidth, ...
            'DisplayName', strcat(NetNames{net}, " ", int2str(PdBm(p)), " dBm"))
        c = c+1;
        m = m+1;
        hold on;
    end
    hold off;
    set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
    xlabel('Number of control bits')
    ylabel('ASR (bps/Hz)')
%     hold on;
%     qw = {};
%     qw{1} = plot(nan, 'k-', 'LineWidth', linewidth);
%     hold off;
%     legend([qw{:}], {powers_list(p)}, 'location', 'south')
    title(powers_list(p))
    axis tight
%     ylim([0, inf])
    yl = ylim;
    fontsize(gca,ftsz,"pixels")
    xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    yticks(yl(1):(yl(2)-yl(1))/3:yl(2))
    ytickformat('%.1f')
end

%% Figure 4 - Train/Val Loss Setup 1
figure(4);

% trial for loss curves
trial = "PerfectCSI/repeated_trial_02/";
linewidth = 3;
% ftsz = 15;

loss = '3'; % 40 bits
% loss = '7'; % 80 bits
% loss = '9'; % 100 bits
PdBm = '20PdBm';
t = 4; % trial

AQEWMMSE_loss = zeros(1000,2);
AQE_loss = zeros(1000,2);
ACF_loss = zeros(1000,2);
linQ_loss = zeros(1000,2);
DQNN_loss = zeros(1000,2);
AQEWMMSE_loss = AQEWMMSE_loss + readmatrix(dir + trial + "/0" + int2str(t) + "/" + PdBm + "/AQE_loss" + loss + ".csv");
AQE_loss = AQE_loss + readmatrix(dir + trial + "/0" + int2str(t) + "/" + PdBm + "/AQEnoW_loss" + loss + ".csv");
ACF_loss = ACF_loss + readmatrix(dir + trial + "/0" + int2str(t) + "/" + PdBm + "/ACF_loss" + loss + ".csv");
linQ_loss = linQ_loss + readmatrix(dir + trial + "/0" + int2str(t) + "/" + PdBm + "/linQ_loss" + loss + ".csv");
if loss == '9'
    DQNN_loss = DQNN_loss + readmatrix(dir + trial + "/0" + int2str(t) + "/" + PdBm + "/DQNN_loss" + loss + ".csv");
end
% train_num = 64000;
% val_num = 16000;
train_num = 1;
val_num = 1;

plot(train_num*AQEWMMSE_loss(:,1), '--', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE train', 'LineWidth', linewidth)
hold on;
plot(train_num*AQE_loss(:,1), '--', 'Color', colour_list{3}, 'DisplayName', 'AQE train', 'LineWidth', linewidth)
plot(train_num*ACF_loss(:,1), '--', 'Color', colour_list{4}, 'DisplayName', 'ACF train', 'LineWidth', linewidth)
plot(train_num*linQ_loss(:,1), '--', 'Color', colour_list{5}, 'DisplayName', 'linQ train', 'LineWidth', linewidth)
if loss == '9'
    plot(train_num*DQNN_loss(:,1), '--', 'Color', colour_list{6}, 'DisplayName', 'DQNN train', 'LineWidth', linewidth)
end
plot(val_num*AQEWMMSE_loss(:,2), '-', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE val', 'LineWidth', linewidth)
plot(val_num*AQE_loss(:,2), '-', 'Color', colour_list{3}, 'DisplayName', 'AQE val', 'LineWidth', linewidth)
plot(val_num*ACF_loss(:,2), '-', 'Color', colour_list{4}, 'DisplayName', 'ACF val', 'LineWidth', linewidth)
plot(val_num*linQ_loss(:,2), '-', 'Color', colour_list{5}, 'DisplayName', 'linQ val', 'LineWidth', linewidth)
if loss == '9'
    plot(val_num*DQNN_loss(:,2), '-', 'Color', colour_list{6}, 'DisplayName', 'DQNN val', 'LineWidth', linewidth)
end
hold off;

xlabel('Epoch')
ylabel('Normalized Loss')
% legend('NumColumns', 1, 'location', 'bestoutside')
hold on;
qw = {};
qw{1} = plot(nan, '-', 'Color', colour_list{2}, 'LineWidth', linewidth);
qw{2} = plot(nan, '-', 'Color', colour_list{3}, 'LineWidth', linewidth);
qw{3} = plot(nan, '-', 'Color', colour_list{4}, 'LineWidth', linewidth);
qw{4} = plot(nan, '-', 'Color', colour_list{5}, 'LineWidth', linewidth);
if loss == '9'
    qw{5} = plot(nan, '-', 'Color', colour_list{6}, 'LineWidth', linewidth);
    qw{6} = plot(nan, 'k--', 'LineWidth', linewidth);
    qw{7} = plot(nan, 'k-', 'LineWidth', linewidth);
else
    qw{5} = plot(nan, 'k--', 'LineWidth', linewidth);
    qw{6} = plot(nan, 'k-', 'LineWidth', linewidth);
end
hold off;
if loss == '9'
    legend([qw{:}], {'AQE-WMMSE', 'AQE', 'ACF', 'linQ', 'DQNN', 'train', 'validation'}, 'location', 'best', 'NumColumns', 3)
else
    legend([qw{:}], {'AQE-WMMSE', 'AQE', 'ACF', 'linQ', 'train', 'validation'}, 'location', 'best', 'NumColumns', 2)
end
% ylim([-0.22, inf])
% xticks([1, 10, 100, 1000])
axis tight
fontsize(gca,ftsz,"pixels")
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')

%% Figure 5 - Imperfect CSI Rate vs Bits, 40 Tx dBm
figure(5); hold on;
linewidth = 1.5;
% ftsz = 20;
trials = "CSIerr35PdBm/repeated_trial_01";
% Load
results_n20dB00_CSIerr = readmatrix(dir + trials + "/00/n20dB/results.csv");
results_n25dB00_CSIerr = readmatrix(dir + trials + "/00/n25dB/results.csv");
results_n30dB00_CSIerr = readmatrix(dir + trials + "/00/n30dB/results.csv");
results_n35dB00_CSIerr = readmatrix(dir + trials + "/00/n35dB/results.csv");
results_n40dB00_CSIerr = readmatrix(dir + trials + "/00/n40dB/results.csv");
results_n45dB00_CSIerr = readmatrix(dir + trials + "/00/n45dB/results.csv");
results_n20dB01_CSIerr = readmatrix(dir + trials + "/01/n20dB/results.csv");
results_n25dB01_CSIerr = readmatrix(dir + trials + "/01/n25dB/results.csv");
results_n30dB01_CSIerr = readmatrix(dir + trials + "/01/n30dB/results.csv");
results_n35dB01_CSIerr = readmatrix(dir + trials + "/01/n35dB/results.csv");
results_n40dB01_CSIerr = readmatrix(dir + trials + "/01/n40dB/results.csv");
results_n45dB01_CSIerr = readmatrix(dir + trials + "/01/n45dB/results.csv");
results_n20dB02_CSIerr = readmatrix(dir + trials + "/02/n20dB/results.csv");
results_n25dB02_CSIerr = readmatrix(dir + trials + "/02/n25dB/results.csv");
results_n30dB02_CSIerr = readmatrix(dir + trials + "/02/n30dB/results.csv");
results_n35dB02_CSIerr = readmatrix(dir + trials + "/02/n35dB/results.csv");
results_n40dB02_CSIerr = readmatrix(dir + trials + "/02/n40dB/results.csv");
results_n45dB02_CSIerr = readmatrix(dir + trials + "/02/n45dB/results.csv");
results_n20dB03_CSIerr = readmatrix(dir + trials + "/03/n20dB/results.csv");
results_n25dB03_CSIerr = readmatrix(dir + trials + "/03/n25dB/results.csv");
results_n30dB03_CSIerr = readmatrix(dir + trials + "/03/n30dB/results.csv");
results_n35dB03_CSIerr = readmatrix(dir + trials + "/03/n35dB/results.csv");
results_n40dB03_CSIerr = readmatrix(dir + trials + "/03/n40dB/results.csv");
results_n45dB03_CSIerr = readmatrix(dir + trials + "/03/n45dB/results.csv");
results_n20dB04_CSIerr = readmatrix(dir + trials + "/04/n20dB/results.csv");
results_n25dB04_CSIerr = readmatrix(dir + trials + "/04/n25dB/results.csv");
results_n30dB04_CSIerr = readmatrix(dir + trials + "/04/n30dB/results.csv");
results_n35dB04_CSIerr = readmatrix(dir + trials + "/04/n35dB/results.csv");
results_n40dB04_CSIerr = readmatrix(dir + trials + "/04/n40dB/results.csv");
results_n45dB04_CSIerr = readmatrix(dir + trials + "/04/n45dB/results.csv");

results_n20dB_mean_CSIerr = (results_n20dB00_CSIerr + results_n20dB01_CSIerr + results_n20dB02_CSIerr + results_n20dB03_CSIerr + results_n20dB04_CSIerr) / 5;
results_n25dB_mean_CSIerr = (results_n25dB00_CSIerr + results_n25dB01_CSIerr + results_n25dB02_CSIerr + results_n25dB03_CSIerr + results_n25dB04_CSIerr) / 5;
results_n30dB_mean_CSIerr = (results_n30dB00_CSIerr + results_n30dB01_CSIerr + results_n30dB02_CSIerr + results_n30dB03_CSIerr + results_n30dB04_CSIerr) / 5;
results_n35dB_mean_CSIerr = (results_n35dB00_CSIerr + results_n35dB01_CSIerr + results_n35dB02_CSIerr + results_n35dB03_CSIerr + results_n35dB04_CSIerr) / 5;
results_n40dB_mean_CSIerr = (results_n40dB00_CSIerr + results_n40dB01_CSIerr + results_n40dB02_CSIerr + results_n40dB03_CSIerr + results_n40dB04_CSIerr) / 5;
results_n45dB_mean_CSIerr = (results_n45dB00_CSIerr + results_n45dB01_CSIerr + results_n45dB02_CSIerr + results_n45dB03_CSIerr + results_n45dB04_CSIerr) / 5;

results_n20dB_var_CSIerr = (results_n20dB00_CSIerr.^2 + results_n20dB01_CSIerr.^2 + results_n20dB02_CSIerr.^2 + results_n20dB03_CSIerr.^2 + results_n20dB04_CSIerr.^2) / 5 - results_n20dB_mean_CSIerr.^2;
results_n25dB_var_CSIerr = (results_n25dB00_CSIerr.^2 + results_n25dB01_CSIerr.^2 + results_n25dB02_CSIerr.^2 + results_n25dB03_CSIerr.^2 + results_n25dB04_CSIerr.^2) / 5 - results_n25dB_mean_CSIerr.^2;
results_n30dB_var_CSIerr = (results_n30dB00_CSIerr.^2 + results_n30dB01_CSIerr.^2 + results_n30dB02_CSIerr.^2 + results_n30dB03_CSIerr.^2 + results_n30dB04_CSIerr.^2) / 5 - results_n30dB_mean_CSIerr.^2;
results_n35dB_var_CSIerr = (results_n35dB00_CSIerr.^2 + results_n35dB01_CSIerr.^2 + results_n35dB02_CSIerr.^2 + results_n35dB03_CSIerr.^2 + results_n35dB04_CSIerr.^2) / 5 - results_n35dB_mean_CSIerr.^2;
results_n40dB_var_CSIerr = (results_n40dB00_CSIerr.^2 + results_n40dB01_CSIerr.^2 + results_n40dB02_CSIerr.^2 + results_n40dB03_CSIerr.^2 + results_n40dB04_CSIerr.^2) / 5 - results_n40dB_mean_CSIerr.^2;
results_n45dB_var_CSIerr = (results_n45dB00_CSIerr.^2 + results_n45dB01_CSIerr.^2 + results_n45dB02_CSIerr.^2 + results_n45dB03_CSIerr.^2 + results_n45dB04_CSIerr.^2) / 5 - results_n45dB_mean_CSIerr.^2;

results_n20dB_CSIerr = results_n20dB_mean_CSIerr;
results_n25dB_CSIerr = results_n25dB_mean_CSIerr;
results_n30dB_CSIerr = results_n30dB_mean_CSIerr;
results_n35dB_CSIerr = results_n35dB_mean_CSIerr;
results_n40dB_CSIerr = results_n40dB_mean_CSIerr;
results_n45dB_CSIerr = results_n45dB_mean_CSIerr;

NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
results_CSIerr = cat(3,results_n20dB_CSIerr, results_n25dB_CSIerr, results_n30dB_CSIerr, ...
    results_n35dB_CSIerr, results_n40dB_CSIerr, results_n45dB_CSIerr);

err = ["n20dB", "n25dB", "n30dB", "n35dB", "n40dB", "n45dB"];
for i = 1:length(err)
    trainparams = readmatrix(strcat(dir, trials, "/00/", err(i), "/trainparams.csv"));
    nmse_Hau = trainparams(1,19); nmse_Har = trainparams(1,20); nmse_Hru = trainparams(1,21);
    fprintf(err(i)); fprintf(': nmse_Hau = %e, nmse_Har = %e, nmse_Hru %e\n', nmse_Hau, nmse_Har, nmse_Hru)
end

% Plot
errdBm = [-20, -25, -30, -35, -40, -45];
b1 = 1;
m = 2;
c = 2;
qw = {};
qw{1} = plot(errdBm, squeeze(results_CSIerr(b1,2,:)), '-', 'Color', colour_list{1}, ...
    'Marker', marker_list{1}, 'LineWidth', linewidth, ...
    'DisplayName', 'WMMSE-PI');
l = 2;
for net = [3,4,5,7]
    qw{l} = plot(errdBm, squeeze(results_CSIerr(b1,net,:)), '-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', NetNames{net});
    c = c+1;
    m = m+1;
    l = l+1;
    hold on;
end
plot(errdBm, squeeze(results_CSIerr(b1,8,:)), '--', 'Color', colour_list{1}, ...
    'Marker', marker_list{1}, 'LineWidth', linewidth, ...
    'DisplayName', 'WMMSE-PI random')
c = 2;
m = 2;
for net = [9,10,11,13]
    plot(errdBm, squeeze(results_CSIerr(b1,net,:)), '--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', NetNames{net})
    c = c+1;
    m = m+1;
end
hold off;

grid on;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('CSI error \sigma_E^2 (dB)')
ylabel('Achievable Sum Rate (bps/Hz)')
% legend('NumColumns', 2, 'location', 'northwest')
hold on;
qw{7} = plot(nan, 'k--', 'LineWidth', linewidth);
hold off;
legend([qw{:}], {'WMMSE-PI','AQE-WMMSE','AQE','ACFNet','linQ','random'}, 'location', 'best', 'NumColumns', 2)
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

% % Create smaller axes for values between -30dB and -35dB
% results_n31dB00_CSIerr = readmatrix(dir + trials + "/00/n31dB/results.csv");
% results_n32dB00_CSIerr = readmatrix(dir + trials + "/00/n32dB/results.csv");
% results_n33dB00_CSIerr = readmatrix(dir + trials + "/00/n33dB/results.csv");
% results_n34dB00_CSIerr = readmatrix(dir + trials + "/00/n34dB/results.csv");
% results_n31dB01_CSIerr = readmatrix(dir + trials + "/01/n31dB/results.csv");
% results_n32dB01_CSIerr = readmatrix(dir + trials + "/01/n32dB/results.csv");
% results_n33dB01_CSIerr = readmatrix(dir + trials + "/01/n33dB/results.csv");
% results_n34dB01_CSIerr = readmatrix(dir + trials + "/01/n34dB/results.csv");
% results_n31dB02_CSIerr = readmatrix(dir + trials + "/02/n31dB/results.csv");
% results_n32dB02_CSIerr = readmatrix(dir + trials + "/02/n32dB/results.csv");
% results_n33dB02_CSIerr = readmatrix(dir + trials + "/02/n33dB/results.csv");
% results_n34dB02_CSIerr = readmatrix(dir + trials + "/02/n34dB/results.csv");
% results_n31dB03_CSIerr = readmatrix(dir + trials + "/03/n31dB/results.csv");
% results_n32dB03_CSIerr = readmatrix(dir + trials + "/03/n32dB/results.csv");
% results_n33dB03_CSIerr = readmatrix(dir + trials + "/03/n33dB/results.csv");
% results_n34dB03_CSIerr = readmatrix(dir + trials + "/03/n34dB/results.csv");
% results_n31dB04_CSIerr = readmatrix(dir + trials + "/04/n31dB/results.csv");
% results_n32dB04_CSIerr = readmatrix(dir + trials + "/04/n32dB/results.csv");
% results_n33dB04_CSIerr = readmatrix(dir + trials + "/04/n33dB/results.csv");
% results_n34dB04_CSIerr = readmatrix(dir + trials + "/04/n34dB/results.csv");
% 
% results_n31dB_mean_CSIerr = (results_n31dB00_CSIerr + results_n31dB01_CSIerr + results_n31dB02_CSIerr + results_n31dB03_CSIerr + results_n31dB04_CSIerr) / 5;
% results_n32dB_mean_CSIerr = (results_n32dB00_CSIerr + results_n32dB01_CSIerr + results_n32dB02_CSIerr + results_n32dB03_CSIerr + results_n32dB04_CSIerr) / 5;
% results_n33dB_mean_CSIerr = (results_n33dB00_CSIerr + results_n33dB01_CSIerr + results_n33dB02_CSIerr + results_n33dB03_CSIerr + results_n33dB04_CSIerr) / 5;
% results_n34dB_mean_CSIerr = (results_n34dB00_CSIerr + results_n34dB01_CSIerr + results_n34dB02_CSIerr + results_n34dB03_CSIerr + results_n34dB04_CSIerr) / 5;
% 
% results_n31dB_var_CSIerr = (results_n31dB00_CSIerr.^2 + results_n31dB01_CSIerr.^2 + results_n31dB02_CSIerr.^2 + results_n31dB03_CSIerr.^2 + results_n31dB04_CSIerr.^2) / 5 - results_n31dB_mean_CSIerr.^2;
% results_n32dB_var_CSIerr = (results_n32dB00_CSIerr.^2 + results_n32dB01_CSIerr.^2 + results_n32dB02_CSIerr.^2 + results_n32dB03_CSIerr.^2 + results_n32dB04_CSIerr.^2) / 5 - results_n32dB_mean_CSIerr.^2;
% results_n33dB_var_CSIerr = (results_n33dB00_CSIerr.^2 + results_n33dB01_CSIerr.^2 + results_n33dB02_CSIerr.^2 + results_n33dB03_CSIerr.^2 + results_n33dB04_CSIerr.^2) / 5 - results_n33dB_mean_CSIerr.^2;
% results_n34dB_var_CSIerr = (results_n34dB00_CSIerr.^2 + results_n34dB01_CSIerr.^2 + results_n34dB02_CSIerr.^2 + results_n34dB03_CSIerr.^2 + results_n34dB04_CSIerr.^2) / 5 - results_n34dB_mean_CSIerr.^2;
% 
% results_n31dB_CSIerr = results_n31dB_mean_CSIerr;
% results_n32dB_CSIerr = results_n32dB_mean_CSIerr;
% results_n33dB_CSIerr = results_n33dB_mean_CSIerr;
% results_n34dB_CSIerr = results_n34dB_mean_CSIerr;
% 
% results_CSIerr_zoom = cat(3,results_n35dB_CSIerr, results_n34dB_CSIerr, results_n33dB_CSIerr, results_n32dB_CSIerr, results_n31dB_CSIerr, results_n30dB_CSIerr);
% errdBm_zoom = [-35, -34, -33, -32, -31, -30];
% linewidth_zoom = 1;
% 
% axes('Position',[.7 .7 .2 .2])
% box on
% m = 2;
% c = 2;
% plot(errdBm_zoom, squeeze(results_CSIerr_zoom(b1,2,:)), '-', 'Color', colour_list{1}, ...
%     'Marker', marker_list{1}, 'LineWidth', linewidth_zoom, ...
%     'DisplayName', 'WMMSE-PI')
% hold on;
% for net = [3,4,5,7]
%     plot(errdBm_zoom, squeeze(results_CSIerr_zoom(b1,net,:)), '-', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth_zoom, ...
%         'DisplayName', NetNames{net})
%     c = c+1;
%     m = m+1;
% end
% plot(errdBm_zoom, squeeze(results_CSIerr_zoom(b1,8,:)), '--', 'Color', colour_list{1}, ...
%     'Marker', marker_list{1}, 'LineWidth', linewidth_zoom, ...
%     'DisplayName', 'WMMSE-PI random')
% c = 2;
% m = 2;
% for net = [9,10,11,13]
%     plot(errdBm_zoom, squeeze(results_CSIerr_zoom(b1,net,:)), '--', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth_zoom, ...
%         'DisplayName', NetNames{net})
%     c = c+1;
%     m = m+1;
% end
% hold off;
% axis tight
% grid on
% xticks(errdBm_zoom)
% % xticklabels({'x = 0','x = 5','x = 10'})

% x2 = linspace(3/4,1);
% y2 = sin(2*pi*x2);
% plot(x2,y2)

% %% Figure 6 - Imperfect CSI Rate vs Bits, 40 Tx dBm
% figure(6); hold on;
% linewidth = 1.5;
% % ftsz = 20;
% for trials = ["CSIerr0/repeated_trial_01", "CSIerr1/repeated_trial_01"]
%     % Load
%     results_10PdBm00_CSIerr = readmatrix(dir + trials + "/00/10PdBm/results.csv");
%     results_15PdBm00_CSIerr = readmatrix(dir + trials + "/00/15PdBm/results.csv");
%     results_20PdBm00_CSIerr = readmatrix(dir + trials + "/00/20PdBm/results.csv");
%     results_25PdBm00_CSIerr = readmatrix(dir + trials + "/00/25PdBm/results.csv");
%     results_30PdBm00_CSIerr = readmatrix(dir + trials + "/00/30PdBm/results.csv");
%     results_35PdBm00_CSIerr = readmatrix(dir + trials + "/00/35PdBm/results.csv");
%     results_40PdBm00_CSIerr = readmatrix(dir + trials + "/00/40PdBm/results.csv");
%     results_10PdBm01_CSIerr = readmatrix(dir + trials + "/01/10PdBm/results.csv");
%     results_15PdBm01_CSIerr = readmatrix(dir + trials + "/01/15PdBm/results.csv");
%     results_20PdBm01_CSIerr = readmatrix(dir + trials + "/01/20PdBm/results.csv");
%     results_25PdBm01_CSIerr = readmatrix(dir + trials + "/01/25PdBm/results.csv");
%     results_30PdBm01_CSIerr = readmatrix(dir + trials + "/01/30PdBm/results.csv");
%     results_35PdBm01_CSIerr = readmatrix(dir + trials + "/01/35PdBm/results.csv");
%     results_40PdBm01_CSIerr = readmatrix(dir + trials + "/01/40PdBm/results.csv");
%     results_10PdBm02_CSIerr = readmatrix(dir + trials + "/02/10PdBm/results.csv");
%     results_15PdBm02_CSIerr = readmatrix(dir + trials + "/02/15PdBm/results.csv");
%     results_20PdBm02_CSIerr = readmatrix(dir + trials + "/02/20PdBm/results.csv");
%     results_25PdBm02_CSIerr = readmatrix(dir + trials + "/02/25PdBm/results.csv");
%     results_30PdBm02_CSIerr = readmatrix(dir + trials + "/02/30PdBm/results.csv");
%     results_35PdBm02_CSIerr = readmatrix(dir + trials + "/02/35PdBm/results.csv");
%     results_40PdBm02_CSIerr = readmatrix(dir + trials + "/02/40PdBm/results.csv");
%     results_10PdBm03_CSIerr = readmatrix(dir + trials + "/03/10PdBm/results.csv");
%     results_15PdBm03_CSIerr = readmatrix(dir + trials + "/03/15PdBm/results.csv");
%     results_20PdBm03_CSIerr = readmatrix(dir + trials + "/03/20PdBm/results.csv");
%     results_25PdBm03_CSIerr = readmatrix(dir + trials + "/03/25PdBm/results.csv");
%     results_30PdBm03_CSIerr = readmatrix(dir + trials + "/03/30PdBm/results.csv");
%     results_35PdBm03_CSIerr = readmatrix(dir + trials + "/03/35PdBm/results.csv");
%     results_40PdBm03_CSIerr = readmatrix(dir + trials + "/03/40PdBm/results.csv");
%     results_10PdBm04_CSIerr = readmatrix(dir + trials + "/04/10PdBm/results.csv");
%     results_15PdBm04_CSIerr = readmatrix(dir + trials + "/04/15PdBm/results.csv");
%     results_20PdBm04_CSIerr = readmatrix(dir + trials + "/04/20PdBm/results.csv");
%     results_25PdBm04_CSIerr = readmatrix(dir + trials + "/04/25PdBm/results.csv");
%     results_30PdBm04_CSIerr = readmatrix(dir + trials + "/04/30PdBm/results.csv");
%     results_35PdBm04_CSIerr = readmatrix(dir + trials + "/04/35PdBm/results.csv");
%     results_40PdBm04_CSIerr = readmatrix(dir + trials + "/04/40PdBm/results.csv");
%     
%     results_10PdBm_mean_CSIerr = (results_10PdBm00_CSIerr + results_10PdBm01_CSIerr + results_10PdBm02_CSIerr + results_10PdBm03_CSIerr + results_10PdBm04_CSIerr) / 5;
%     results_15PdBm_mean_CSIerr = (results_15PdBm00_CSIerr + results_15PdBm01_CSIerr + results_15PdBm02_CSIerr + results_15PdBm03_CSIerr + results_15PdBm04_CSIerr) / 5;
%     results_20PdBm_mean_CSIerr = (results_20PdBm00_CSIerr + results_20PdBm01_CSIerr + results_20PdBm02_CSIerr + results_20PdBm03_CSIerr + results_20PdBm04_CSIerr) / 5;
%     results_25PdBm_mean_CSIerr = (results_25PdBm00_CSIerr + results_25PdBm01_CSIerr + results_25PdBm02_CSIerr + results_25PdBm03_CSIerr + results_25PdBm04_CSIerr) / 5;
%     results_30PdBm_mean_CSIerr = (results_30PdBm00_CSIerr + results_30PdBm01_CSIerr + results_30PdBm02_CSIerr + results_30PdBm03_CSIerr + results_30PdBm04_CSIerr) / 5;
%     results_35PdBm_mean_CSIerr = (results_35PdBm00_CSIerr + results_35PdBm01_CSIerr + results_35PdBm02_CSIerr + results_35PdBm03_CSIerr + results_35PdBm04_CSIerr) / 5;
%     results_40PdBm_mean_CSIerr = (results_40PdBm00_CSIerr + results_40PdBm01_CSIerr + results_40PdBm02_CSIerr + results_40PdBm03_CSIerr + results_40PdBm04_CSIerr) / 5;
%     
%     results_10PdBm_var_CSIerr = (results_10PdBm00_CSIerr.^2 + results_10PdBm01_CSIerr.^2 + results_10PdBm02_CSIerr.^2 + results_10PdBm03_CSIerr.^2 + results_10PdBm04_CSIerr.^2) / 5 - results_10PdBm_mean_CSIerr.^2;
%     results_15PdBm_var_CSIerr = (results_15PdBm00_CSIerr.^2 + results_15PdBm01_CSIerr.^2 + results_15PdBm02_CSIerr.^2 + results_15PdBm03_CSIerr.^2 + results_15PdBm04_CSIerr.^2) / 5 - results_15PdBm_mean_CSIerr.^2;
%     results_20PdBm_var_CSIerr = (results_20PdBm00_CSIerr.^2 + results_20PdBm01_CSIerr.^2 + results_20PdBm02_CSIerr.^2 + results_20PdBm03_CSIerr.^2 + results_20PdBm04_CSIerr.^2) / 5 - results_20PdBm_mean_CSIerr.^2;
%     results_25PdBm_var_CSIerr = (results_25PdBm00_CSIerr.^2 + results_25PdBm01_CSIerr.^2 + results_25PdBm02_CSIerr.^2 + results_25PdBm03_CSIerr.^2 + results_25PdBm04_CSIerr.^2) / 5 - results_25PdBm_mean_CSIerr.^2;
%     results_30PdBm_var_CSIerr = (results_30PdBm00_CSIerr.^2 + results_30PdBm01_CSIerr.^2 + results_30PdBm02_CSIerr.^2 + results_30PdBm03_CSIerr.^2 + results_30PdBm04_CSIerr.^2) / 5 - results_30PdBm_mean_CSIerr.^2;
%     results_35PdBm_var_CSIerr = (results_35PdBm00_CSIerr.^2 + results_35PdBm01_CSIerr.^2 + results_35PdBm02_CSIerr.^2 + results_35PdBm03_CSIerr.^2 + results_35PdBm04_CSIerr.^2) / 5 - results_35PdBm_mean_CSIerr.^2;
%     results_40PdBm_var_CSIerr = (results_40PdBm00_CSIerr.^2 + results_40PdBm01_CSIerr.^2 + results_40PdBm02_CSIerr.^2 + results_40PdBm03_CSIerr.^2 + results_40PdBm04_CSIerr.^2) / 5 - results_40PdBm_mean_CSIerr.^2;
%     
%     results_10PdBm_CSIerr = results_10PdBm_mean_CSIerr;
%     results_15PdBm_CSIerr = results_15PdBm_mean_CSIerr;
%     results_20PdBm_CSIerr = results_20PdBm_mean_CSIerr;
%     results_25PdBm_CSIerr = results_25PdBm_mean_CSIerr;
%     results_30PdBm_CSIerr = results_30PdBm_mean_CSIerr;
%     results_35PdBm_CSIerr = results_35PdBm_mean_CSIerr;
%     results_40PdBm_CSIerr = results_40PdBm_mean_CSIerr;
% 
%     NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
%     results_CSIerr = cat(3,results_10PdBm_CSIerr, results_15PdBm_CSIerr, results_20PdBm_CSIerr, ...
%         results_25PdBm_CSIerr, results_30PdBm_CSIerr, results_35PdBm_CSIerr, results_40PdBm_CSIerr);
%     
%     trainparams = readmatrix(dir + trials + "/00/40PdBm/trainparams.csv");
%     nmse_Hau = trainparams(1,19);
%     nmse_Har = trainparams(1,20);
%     nmse_Hru = trainparams(1,21);
%     fprintf('nmse_Hau = %e, nmse_Har = %e, nmse_Hru %e\n', nmse_Hau, nmse_Har, nmse_Hru)
% 
%     % Plot
%     b1 = 1;
%     m = 2;
%     c = 2;
%     accCSI = "Perfect CSI";
%     linemark = 'o-';
%     if strcmp(trials, "CSIerr0/repeated_trial_01")
%         accCSI = "high";
%         linemark = '-';
%     elseif strcmp(trials, "CSIerr1/repeated_trial_01")
%         accCSI = "low";
%         linemark = '--';
%     end
% 
% %     plot(PdBm, squeeze(results_CSIerr(b1,2,:)), '+-', 'Color', colour_list{1}, 'Marker',...
% %         marker_list{1}, 'DisplayName', strcat(NetNames{2}, " (", accCSI, ")"), 'LineWidth', linewidth)
%     for net = [3,4,5,7]
% %     for net = [3,4]
%         plot(PdBm, squeeze(results_CSIerr(b1,net,:)), linemark, 'Color', colour_list{c}, ...
%             'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%             'DisplayName', strcat(NetNames{net}, " ", accCSI, ""))
%         c = c+1;
%         m = m+1;
%     end
% 
% end
% 
% hold off;
% grid on;
% % title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
% xlabel('Transmit Power (dBm)')
% ylabel('Achievable Sum Rate (bps/Hz)')
% legend('NumColumns', 1, 'location', 'northwest')
% ylim([0, 25])
% fontsize(gca,ftsz,"pixels")

%% Figure 6 - Perfect CSI Rate vs N, 35 Tx dBm
ax = figure(6);
linewidth = 1.5;
% ftsz = 20;
trials = "VaryNPerfectCSI/repeated_trial_02";
% Load
results_Nwh5_00 = readmatrix(dir + trials + "/00/Nwh5/results.csv");
results_Nwh6_00 = readmatrix(dir + trials + "/00/Nwh6/results.csv");
results_Nwh7_00 = readmatrix(dir + trials + "/00/Nwh7/results.csv");
results_Nwh8_00 = readmatrix(dir + trials + "/00/Nwh8/results.csv");
results_Nwh9_00 = readmatrix(dir + trials + "/00/Nwh9/results.csv");
results_Nwh10_00 = readmatrix(dir + trials + "/00/Nwh10/results.csv");
results_Nwh5_01 = readmatrix(dir + trials + "/01/Nwh5/results.csv");
results_Nwh6_01 = readmatrix(dir + trials + "/01/Nwh6/results.csv");
results_Nwh7_01 = readmatrix(dir + trials + "/01/Nwh7/results.csv");
results_Nwh8_01 = readmatrix(dir + trials + "/01/Nwh8/results.csv");
results_Nwh9_01 = readmatrix(dir + trials + "/01/Nwh9/results.csv");
results_Nwh10_01 = readmatrix(dir + trials + "/01/Nwh10/results.csv");
results_Nwh5_02 = readmatrix(dir + trials + "/02/Nwh5/results.csv");
results_Nwh6_02 = readmatrix(dir + trials + "/02/Nwh6/results.csv");
results_Nwh7_02 = readmatrix(dir + trials + "/02/Nwh7/results.csv");
results_Nwh8_02 = readmatrix(dir + trials + "/02/Nwh8/results.csv");
results_Nwh9_02 = readmatrix(dir + trials + "/02/Nwh9/results.csv");
results_Nwh10_02 = readmatrix(dir + trials + "/02/Nwh10/results.csv");
results_Nwh5_03 = readmatrix(dir + trials + "/03/Nwh5/results.csv");
results_Nwh6_03 = readmatrix(dir + trials + "/03/Nwh6/results.csv");
results_Nwh7_03 = readmatrix(dir + trials + "/03/Nwh7/results.csv");
results_Nwh8_03 = readmatrix(dir + trials + "/03/Nwh8/results.csv");
results_Nwh9_03 = readmatrix(dir + trials + "/03/Nwh9/results.csv");
results_Nwh10_03 = readmatrix(dir + trials + "/03/Nwh10/results.csv");
results_Nwh5_04 = readmatrix(dir + trials + "/04/Nwh5/results.csv");
results_Nwh6_04 = readmatrix(dir + trials + "/04/Nwh6/results.csv");
results_Nwh7_04 = readmatrix(dir + trials + "/04/Nwh7/results.csv");
results_Nwh8_04 = readmatrix(dir + trials + "/04/Nwh8/results.csv");
results_Nwh9_04 = readmatrix(dir + trials + "/04/Nwh9/results.csv");
results_Nwh10_04 = readmatrix(dir + trials + "/04/Nwh10/results.csv");

results_Nwh5_mean = (results_Nwh5_00 + results_Nwh5_01 + results_Nwh5_02 + results_Nwh5_03 + results_Nwh5_04) / 5;
results_Nwh6_mean = (results_Nwh6_00 + results_Nwh6_01 + results_Nwh6_02 + results_Nwh6_03 + results_Nwh6_04) / 5;
results_Nwh7_mean = (results_Nwh7_00 + results_Nwh7_01 + results_Nwh7_02 + results_Nwh7_03 + results_Nwh7_04) / 5;
results_Nwh8_mean = (results_Nwh8_00 + results_Nwh8_01 + results_Nwh8_02 + results_Nwh8_03 + results_Nwh8_04) / 5;
results_Nwh9_mean = (results_Nwh9_00 + results_Nwh9_01 + results_Nwh9_02 + results_Nwh9_03 + results_Nwh9_04) / 5;
results_Nwh10_mean = (results_Nwh10_00 + results_Nwh10_01 + results_Nwh10_02 + results_Nwh10_03 + results_Nwh10_04) / 5;

results_Nwh5_var = (results_Nwh5_00.^2 + results_Nwh5_01.^2 + results_Nwh5_02.^2 + results_Nwh5_03.^2 + results_Nwh5_04.^2) / 5 - results_Nwh5_mean.^2;
results_Nwh6_var = (results_Nwh6_00.^2 + results_Nwh6_01.^2 + results_Nwh6_02.^2 + results_Nwh6_03.^2 + results_Nwh6_04.^2) / 5 - results_Nwh6_mean.^2;
results_Nwh7_var = (results_Nwh7_00.^2 + results_Nwh7_01.^2 + results_Nwh7_02.^2 + results_Nwh7_03.^2 + results_Nwh7_04.^2) / 5 - results_Nwh7_mean.^2;
results_Nwh8_var = (results_Nwh8_00.^2 + results_Nwh8_01.^2 + results_Nwh8_02.^2 + results_Nwh8_03.^2 + results_Nwh8_04.^2) / 5 - results_Nwh8_mean.^2;
results_Nwh9_var = (results_Nwh9_00.^2 + results_Nwh9_01.^2 + results_Nwh9_02.^2 + results_Nwh9_03.^2 + results_Nwh9_04.^2) / 5 - results_Nwh9_mean.^2;
results_Nwh10_var = (results_Nwh10_00.^2 + results_Nwh10_01.^2 + results_Nwh10_02.^2 + results_Nwh10_03.^2 + results_Nwh10_04.^2) / 5 - results_Nwh10_mean.^2;

results_Nwh5 = results_Nwh5_mean;
results_Nwh6 = results_Nwh6_mean;
results_Nwh7 = results_Nwh7_mean;
results_Nwh8 = results_Nwh8_mean;
results_Nwh9 = results_Nwh9_mean;
results_Nwh10 = results_Nwh10_mean;

NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
results_VaryN = cat(3,results_Nwh5, results_Nwh6, results_Nwh7, ...
    results_Nwh8, results_Nwh9, results_Nwh10);

Nh_RIS_list = [5, 6, 7, 8, 9, 10];
N_RIS_list = power(Nh_RIS_list, 2);
B_RIS_list = floor(0.4.*N_RIS_list);
% x_list = ["N=25, B=10", "N=36, B=14", "N=49, B=19", "N=64, B=25", "N=81, B=32", "N=100, B=40"];
X = categorical({'N=25, B=10', 'N=36, B=14', 'N=49, B=19', 'N=64, B=25', 'N=81, B=32', 'N=100, B=40'});
X = reordercats(X,{'N=25, B=10', 'N=36, B=14', 'N=49, B=19', 'N=64, B=25', 'N=81, B=32', 'N=100, B=40'});

% Plot
b1 = 1;
m = 1;
c = 1;

% hold on;
% for net = [2,3,4,5,7]
%     plot(N_RIS_list, squeeze(results_VaryN(b1,net,:)), '-', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', NetNames{net})
%     c = c+1;
%     m = m+1;
%     hold on;
% end
% c = 1;
% m = 1;
% for net = [8,9,10,11,13]
%     plot(N_RIS_list, squeeze(results_VaryN(b1,net,:)), '--', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'DisplayName', NetNames{net}, 'LineWidth', linewidth)
%     c = c+1;
%     m = m+1;
% end
% hold off;

VaryN_data = zeros(6,4);
i = 1;
for net = [3,4,5,7]
    VaryN_data(:,i) = squeeze(results_VaryN(b1,net,:));
    i = i+1;
end

for p = 1:6
    bh = bar(X(p), VaryN_data(p,:));
    for c = 2:5
        bh(c-1).FaceColor = colour_list{c};
        bh(c-1).EdgeColor = 'none';
    end
    grid off;
    ylim([0, 15])
    hold on;
end
hold off;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('N RIS elements, B control bits')
ylabel('Achievable Sum Rate (bps/Hz)')
legend('AQE-WMMSE','AQE','ACFNet','linQ', 'Location', 'best', 'NumColumns', 2)
% axis tight

% heatmap(["AQE-WMMSE","AQE","ACFNet","linQ"], x_list, VaryN_data);
% % heatmap(x_list, ["AQE-WMMSE","AQE","ACFNet","linQ"], VaryN_data');
% for c = 2:5
% %     bh(c-1).FaceColor = colour_list{c};
% %     bh(c-1).EdgeColor = 'none';
% end
% colormap default
% title("Achievable Sum Rate (bps/Hz)");

fontsize(gca,ftsz,"pixels")