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
trials = "PerfectCSI/repeated_trial_01";
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

% trial for loss curves
trial = "PerfectCSI/repeated_trial_01/02";

NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
results = cat(3,results_10PdBm, results_15PdBm, results_20PdBm, ...
    results_25PdBm, results_30PdBm, results_35PdBm, results_40PdBm);


PdBm = [10, 15, 20, 25, 30, 35, 40];
sz = size(results);
ftsz = 17;

%% Figure 1 - Rate vs Tx, 100 control bits
b = 10;
c = 1;
m = 1;
figure(1);
for net = [2,3,4,5,7,6]
    plot(PdBm, squeeze(results(b,net,:)), '-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net}, 'LineWidth', linewidth)
    c = c+1;
    m = m+1;
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
legend('NumColumns', 2, 'location', 'best')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 2 - Rate vs Tx, 10 & 40 control bits
b1 = 4; b2 = 1;
m = 2;
figure(2);
c = 2;
plot(PdBm, squeeze(results(b1,2,:)), '+-', 'Color', colour_list{1}, 'Marker', marker_list{1}, 'DisplayName', strcat(NetNames{2}), 'LineWidth', linewidth)
hold on;
for net = [3,4,5,7]
    plot(PdBm, squeeze(results(b1,net,:)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " ", int2str(results(b1,1,1)), " bits"))
    plot(PdBm, squeeze(results(b2,net,:)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " ", int2str(results(b2,1,1)), " bits"))
    c = c+1;
    m = m+1;
end
% b2 = 1;
% c = 2;
% m = 2;
% for net = [3,4,5,7]
%     plot(PdBm, squeeze(results(b,net,:)), '*--', 'Color', colour_list{c}, ...
%         'Marker', marker_list{m}, 'LineWidth', linewidth, ...
%         'DisplayName', strcat(NetNames{net}, " (", int2str(results(b,1,1)), " bits)"))
%     c = c+1;
%     m = m+1;
% end
hold off;
grid on;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('Achievable Sum Rate (bps/Hz)')
legend('NumColumns', 1, 'location', 'northwest')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 3 - Rate vs Bits, 40 & 15 Tx dBm
bits = 1:10;
mark = {'o-', '', '', '', '', '', '*-'};
figure(3);
p = 6; % 35 PdBm
% p = 5; % 30 PdBm
c = 1;
m = 1;
for net = [2,3,4,5,7]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " ", int2str(PdBm(p)), " dBm"))
    c = c+1;
    m = m+1;
    hold on;
end
p = 2; % 15 PdBm
c = 1;
m = 1;
for net = [2,3,4,5,7]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " ", int2str(PdBm(p)), " dBm"))
    c = c+1;
    m = m+1;
    hold on;
end
hold off;
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
% title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
xlabel('Number of control bits')
ylabel('Achievable Sum Rate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
% legend('location', 'eastoutside')
axis tight
ylim([0, 25])
% set (gca, 'Xscale', 'log');
% set(gca,'XTick', results(bits,1,1));
fontsize(gca,ftsz,"pixels")
xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

%% Figure 4 - Train/Val Loss Setup 1
% linewidth = 2;
% ftsz = 20;
linewidth = 2;
figure(4);
loss = '3'; % 40 bits
% loss = '2'; % 30 bits
AQEWMMSE_loss = readmatrix(dir + trial + "/35PdBm/AQE_loss" + loss + ".csv");
AQE_loss = readmatrix(dir + trial + "/35PdBm/AQEnoW_loss" + loss + ".csv");
ACF_loss = readmatrix(dir + trial + "/35PdBm/ACF_loss" + loss + ".csv");
linQ_loss = readmatrix(dir + trial + "/35PdBm/linQ_loss" + loss + ".csv");

% train_num = 64000;
% val_num = 16000;
train_num = 1;
val_num = 1;

semilogx(train_num*AQEWMMSE_loss(:,1), '-', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE train', 'LineWidth', linewidth)
hold on;
semilogx(val_num*AQEWMMSE_loss(:,2), '--', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE val', 'LineWidth', linewidth/2)
semilogx(train_num*AQE_loss(:,1), '-', 'Color', colour_list{3}, 'DisplayName', 'AQE train', 'LineWidth', linewidth)
semilogx(val_num*AQE_loss(:,2), '--', 'Color', colour_list{3}, 'DisplayName', 'AQE val', 'LineWidth', linewidth/2)
semilogx(train_num*ACF_loss(:,1), '-', 'Color', colour_list{4}, 'DisplayName', 'ACF train', 'LineWidth', linewidth)
semilogx(val_num*ACF_loss(:,2), '--', 'Color', colour_list{4}, 'DisplayName', 'ACF val', 'LineWidth', linewidth/2)
semilogx(train_num*linQ_loss(:,1), '-', 'Color', colour_list{5}, 'DisplayName', 'linQ train', 'LineWidth', linewidth)
semilogx(val_num*linQ_loss(:,2), '--', 'Color', colour_list{5}, 'DisplayName', 'linQ val', 'LineWidth', linewidth/2)
hold off;

xlabel('Epoch')
ylabel('Normalized Loss')
legend('NumColumns', 2, 'location', 'best')
% ylim([-2700, -900])
fontsize(gca,ftsz,"pixels")
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')


%% Figure 5 - Train/Val Loss Setup 2
% linewidth = 2;
figure(5);
AQEWMMSE_loss = readmatrix(dir + trial + "/15PdBm/AQE_loss" + loss + ".csv");
AQE_loss = readmatrix(dir + trial + "/15PdBm/AQEnoW_loss" + loss + ".csv");
ACF_loss = readmatrix(dir + trial + "/15PdBm/ACF_loss" + loss + ".csv");
linQ_loss = readmatrix(dir + trial + "/15PdBm/linQ_loss" + loss + ".csv");

semilogx(train_num*AQEWMMSE_loss(:,1), '-', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE train', 'LineWidth', linewidth)
hold on;
semilogx(val_num*AQEWMMSE_loss(:,2), '--', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE val', 'LineWidth', linewidth/2)
semilogx(train_num*AQE_loss(:,1), '-', 'Color', colour_list{3}, 'DisplayName', 'AQE train', 'LineWidth', linewidth)
semilogx(val_num*AQE_loss(:,2), '--', 'Color', colour_list{3}, 'DisplayName', 'AQE val', 'LineWidth', linewidth/2)
semilogx(train_num*ACF_loss(:,1), '-', 'Color', colour_list{4}, 'DisplayName', 'ACF train', 'LineWidth', linewidth)
semilogx(val_num*ACF_loss(:,2), '--', 'Color', colour_list{4}, 'DisplayName', 'ACF val', 'LineWidth', linewidth/2)
semilogx(train_num*linQ_loss(:,1), '-', 'Color', colour_list{5}, 'DisplayName', 'linQ train', 'LineWidth', linewidth)
semilogx(val_num*linQ_loss(:,2), '--', 'Color', colour_list{5}, 'DisplayName', 'linQ val', 'LineWidth', linewidth/2)
hold off;

xlabel('Epoch')
ylabel('Normalized Loss')
legend('NumColumns', 2, 'location', 'best')
% ylim([-2700, -900])
fontsize(gca,ftsz,"pixels")
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')

%% Figure 6 - Imperfect CSI Rate vs Bits, 40 Tx dBm
figure(6); hold on;
linewidth = 1.5;
% ftsz = 20;
for trials = ["CSIerr0", "CSIerr1"]
    % Load
    results_10PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/10PdBm/results.csv");
    results_15PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/15PdBm/results.csv");
    results_20PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/20PdBm/results.csv");
    results_25PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/25PdBm/results.csv");
    results_30PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/30PdBm/results.csv");
    results_35PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/35PdBm/results.csv");
    results_40PdBm00_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/00/40PdBm/results.csv");
    results_10PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/10PdBm/results.csv");
    results_15PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/15PdBm/results.csv");
    results_20PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/20PdBm/results.csv");
    results_25PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/25PdBm/results.csv");
    results_30PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/30PdBm/results.csv");
    results_35PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/35PdBm/results.csv");
    results_40PdBm01_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/01/40PdBm/results.csv");
    results_10PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/10PdBm/results.csv");
    results_15PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/15PdBm/results.csv");
    results_20PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/20PdBm/results.csv");
    results_25PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/25PdBm/results.csv");
    results_30PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/30PdBm/results.csv");
    results_35PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/35PdBm/results.csv");
    results_40PdBm02_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/02/40PdBm/results.csv");
    results_10PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/10PdBm/results.csv");
    results_15PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/15PdBm/results.csv");
    results_20PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/20PdBm/results.csv");
    results_25PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/25PdBm/results.csv");
    results_30PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/30PdBm/results.csv");
    results_35PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/35PdBm/results.csv");
    results_40PdBm03_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/03/40PdBm/results.csv");
    results_10PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/10PdBm/results.csv");
    results_15PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/15PdBm/results.csv");
    results_20PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/20PdBm/results.csv");
    results_25PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/25PdBm/results.csv");
    results_30PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/30PdBm/results.csv");
    results_35PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/35PdBm/results.csv");
    results_40PdBm04_CSIerr = readmatrix(dir + trials + "/repeated_trial_01/04/40PdBm/results.csv");
    
    results_10PdBm_mean_CSIerr = (results_10PdBm00_CSIerr + results_10PdBm01_CSIerr + results_10PdBm02_CSIerr + results_10PdBm03_CSIerr + results_10PdBm04_CSIerr) / 5;
    results_15PdBm_mean_CSIerr = (results_15PdBm00_CSIerr + results_15PdBm01_CSIerr + results_15PdBm02_CSIerr + results_15PdBm03_CSIerr + results_15PdBm04_CSIerr) / 5;
    results_20PdBm_mean_CSIerr = (results_20PdBm00_CSIerr + results_20PdBm01_CSIerr + results_20PdBm02_CSIerr + results_20PdBm03_CSIerr + results_20PdBm04_CSIerr) / 5;
    results_25PdBm_mean_CSIerr = (results_25PdBm00_CSIerr + results_25PdBm01_CSIerr + results_25PdBm02_CSIerr + results_25PdBm03_CSIerr + results_25PdBm04_CSIerr) / 5;
    results_30PdBm_mean_CSIerr = (results_30PdBm00_CSIerr + results_30PdBm01_CSIerr + results_30PdBm02_CSIerr + results_30PdBm03_CSIerr + results_30PdBm04_CSIerr) / 5;
    results_35PdBm_mean_CSIerr = (results_35PdBm00_CSIerr + results_35PdBm01_CSIerr + results_35PdBm02_CSIerr + results_35PdBm03_CSIerr + results_35PdBm04_CSIerr) / 5;
    results_40PdBm_mean_CSIerr = (results_40PdBm00_CSIerr + results_40PdBm01_CSIerr + results_40PdBm02_CSIerr + results_40PdBm03_CSIerr + results_40PdBm04_CSIerr) / 5;
    
    results_10PdBm_var_CSIerr = (results_10PdBm00_CSIerr.^2 + results_10PdBm01_CSIerr.^2 + results_10PdBm02_CSIerr.^2 + results_10PdBm03_CSIerr.^2 + results_10PdBm04_CSIerr.^2) / 5 - results_10PdBm_mean_CSIerr.^2;
    results_15PdBm_var_CSIerr = (results_15PdBm00_CSIerr.^2 + results_15PdBm01_CSIerr.^2 + results_15PdBm02_CSIerr.^2 + results_15PdBm03_CSIerr.^2 + results_15PdBm04_CSIerr.^2) / 5 - results_15PdBm_mean_CSIerr.^2;
    results_20PdBm_var_CSIerr = (results_20PdBm00_CSIerr.^2 + results_20PdBm01_CSIerr.^2 + results_20PdBm02_CSIerr.^2 + results_20PdBm03_CSIerr.^2 + results_20PdBm04_CSIerr.^2) / 5 - results_20PdBm_mean_CSIerr.^2;
    results_25PdBm_var_CSIerr = (results_25PdBm00_CSIerr.^2 + results_25PdBm01_CSIerr.^2 + results_25PdBm02_CSIerr.^2 + results_25PdBm03_CSIerr.^2 + results_25PdBm04_CSIerr.^2) / 5 - results_25PdBm_mean_CSIerr.^2;
    results_30PdBm_var_CSIerr = (results_30PdBm00_CSIerr.^2 + results_30PdBm01_CSIerr.^2 + results_30PdBm02_CSIerr.^2 + results_30PdBm03_CSIerr.^2 + results_30PdBm04_CSIerr.^2) / 5 - results_30PdBm_mean_CSIerr.^2;
    results_35PdBm_var_CSIerr = (results_35PdBm00_CSIerr.^2 + results_35PdBm01_CSIerr.^2 + results_35PdBm02_CSIerr.^2 + results_35PdBm03_CSIerr.^2 + results_35PdBm04_CSIerr.^2) / 5 - results_35PdBm_mean_CSIerr.^2;
    results_40PdBm_var_CSIerr = (results_40PdBm00_CSIerr.^2 + results_40PdBm01_CSIerr.^2 + results_40PdBm02_CSIerr.^2 + results_40PdBm03_CSIerr.^2 + results_40PdBm04_CSIerr.^2) / 5 - results_40PdBm_mean_CSIerr.^2;
    
    results_10PdBm_CSIerr = results_10PdBm_mean_CSIerr;
    results_15PdBm_CSIerr = results_15PdBm_mean_CSIerr;
    results_20PdBm_CSIerr = results_20PdBm_mean_CSIerr;
    results_25PdBm_CSIerr = results_25PdBm_mean_CSIerr;
    results_30PdBm_CSIerr = results_30PdBm_mean_CSIerr;
    results_35PdBm_CSIerr = results_35PdBm_mean_CSIerr;
    results_40PdBm_CSIerr = results_40PdBm_mean_CSIerr;

    NetNames = {'Nc','Upper Bound','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','Upper Bound random','AQE-WMMSE random','AQE random','ACFNet random','DQNN random','linQ random'};
    results_CSIerr = cat(3,results_10PdBm_CSIerr, results_15PdBm_CSIerr, results_20PdBm_CSIerr, ...
        results_25PdBm_CSIerr, results_30PdBm_CSIerr, results_35PdBm_CSIerr, results_40PdBm_CSIerr);
    
    trainparams = readmatrix(dir + trials + "/repeated_trial_01/00/40PdBm/trainparams.csv");
    nmse_Hau = trainparams(1,19);
    nmse_Har = trainparams(1,20);
    nmse_Hru = trainparams(1,21);
    fprintf('nmse_Hau = %e, nmse_Har = %e, nmse_Hru %e\n', nmse_Hau, nmse_Har, nmse_Hru)

    % Plot
    b1 = 1;
    m = 2;
    c = 2;
    accCSI = "Perfect CSI";
    linemark = 'o-';
    if strcmp(trials, "CSIerr0")
        accCSI = "high";
        linemark = '-';
    elseif strcmp(trials, "CSIerr1")
        accCSI = "low";
        linemark = '--';
    end

%     plot(PdBm, squeeze(results_CSIerr(b1,2,:)), '+-', 'Color', colour_list{1}, 'Marker',...
%         marker_list{1}, 'DisplayName', strcat(NetNames{2}, " (", accCSI, ")"), 'LineWidth', linewidth)
    for net = [3,4,5,7]
%     for net = [3,4]
        plot(PdBm, squeeze(results_CSIerr(b1,net,:)), linemark, 'Color', colour_list{c}, ...
            'Marker', marker_list{m}, 'LineWidth', linewidth, ...
            'DisplayName', strcat(NetNames{net}, " ", accCSI, ""))
        c = c+1;
        m = m+1;
    end

end

hold off;
grid on;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('Achievable Sum Rate (bps/Hz)')
legend('NumColumns', 1, 'location', 'northwest')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 7 - Perfect CSI Rate vs N, 35 Tx dBm
figure(7); hold on;
linewidth = 1.5;
% ftsz = 20;
trials = "VaryNPerfectCSI";
% Load
results_Nwh5_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh5/results.csv");
results_Nwh6_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh6/results.csv");
results_Nwh7_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh7/results.csv");
results_Nwh8_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh8/results.csv");
results_Nwh9_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh9/results.csv");
results_Nwh10_00 = readmatrix(dir + trials + "/repeated_trial_01/00/Nwh10/results.csv");
results_Nwh5_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh5/results.csv");
results_Nwh6_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh6/results.csv");
results_Nwh7_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh7/results.csv");
results_Nwh8_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh8/results.csv");
results_Nwh9_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh9/results.csv");
results_Nwh10_01 = readmatrix(dir + trials + "/repeated_trial_01/01/Nwh10/results.csv");
results_Nwh5_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh5/results.csv");
results_Nwh6_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh6/results.csv");
results_Nwh7_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh7/results.csv");
results_Nwh8_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh8/results.csv");
results_Nwh9_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh9/results.csv");
results_Nwh10_02 = readmatrix(dir + trials + "/repeated_trial_01/02/Nwh10/results.csv");
results_Nwh5_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh5/results.csv");
results_Nwh6_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh6/results.csv");
results_Nwh7_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh7/results.csv");
results_Nwh8_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh8/results.csv");
results_Nwh9_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh9/results.csv");
results_Nwh10_03 = readmatrix(dir + trials + "/repeated_trial_01/03/Nwh10/results.csv");
results_Nwh5_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh5/results.csv");
results_Nwh6_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh6/results.csv");
results_Nwh7_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh7/results.csv");
results_Nwh8_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh8/results.csv");
results_Nwh9_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh9/results.csv");
results_Nwh10_04 = readmatrix(dir + trials + "/repeated_trial_01/04/Nwh10/results.csv");

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

N_RIS_list = [5^2, 6^2, 7^2, 8^2, 9^2, 10^2];

% Plot
b1 = 1;
m = 1;
c = 1;

%     plot(PdBm, squeeze(results_VaryN(b1,2,:)), '+-', 'Color', colour_list{1}, 'Marker',...
%         marker_list{1}, 'DisplayName', strcat(NetNames{2}, " (", accCSI, ")"), 'LineWidth', linewidth)
for net = [2,3,4,5,7]
%     for net = [3,4]
    plot(N_RIS_list, squeeze(results_VaryN(b1,net,:)), '-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', NetNames{net})
    c = c+1;
    m = m+1;
    hold on;
end
c = 1;
m = 1;
for net = [8,9,10,11,13]
    plot(N_RIS_list, squeeze(results_VaryN(b1,net,:)), '--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net}, 'LineWidth', linewidth)
    c = c+1;
    m = m+1;
end
hold off;


hold off;
grid on;
% title("Number of control bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Number of RIS elements')
ylabel('Achievable Sum Rate (bps/Hz)')
legend('NumColumns', 2, 'location', 'northwest')
% axis tight
ylim([0, 45])
fontsize(gca,ftsz,"pixels")