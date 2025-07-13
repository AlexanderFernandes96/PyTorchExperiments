%% Start
% This script is a scratch pad to plot data from MU-MISO_AchievableRate/
% clear all; close all; delete(gcp('nocreate')); clc;

%% Figure 1-3, Load Data and Plot parameters
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
results = zeros(6,11,7);
trial = "plot";
opts = detectImportOptions(dir + trial + "/10PdBm/results.csv");
% NetNames = strrep(strrep(opts.VariableNames, 'R_', ''),'_',' ');
NetNames = {'Nc','opt','AQE-WMMSE','AQE','ACFNet','DQNN','linQ','opt rand','AQE-WMMSE rand','AQE rand','ACFNet rand','DQNN rand','linQ rand'};
results_10PdBm = readmatrix(dir + trial + "/10PdBm/results.csv");
results_15PdBm = readmatrix(dir + trial + "/15PdBm/results.csv");
results_20PdBm = readmatrix(dir + trial + "/20PdBm/results.csv");
results_25PdBm = readmatrix(dir + trial + "/25PdBm/results.csv");
results_30PdBm = readmatrix(dir + trial + "/30PdBm/results.csv");
results_35PdBm = readmatrix(dir + trial + "/35PdBm/results.csv");
results_40PdBm = readmatrix(dir + trial + "/40PdBm/results.csv");

results = cat(3,results_10PdBm, results_15PdBm, results_20PdBm, ...
    results_25PdBm, results_30PdBm, results_35PdBm, results_40PdBm);


PdBm = [10, 15, 20, 25, 30, 35, 40];
sz = size(results);
ftsz = 15;

%% Figure 1 - Rate vs Tx, 100 feedback bits
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
% title("Number of feedback bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('Achievable Rate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 2 - Rate vs Tx, 10 & 40 feedback bits
b1 = 4; b2 = 1;
m = 2;
figure(2);
c = 2;
plot(PdBm, squeeze(results(b1,2,:)), '+-', 'Color', colour_list{1}, 'Marker', marker_list{1}, 'DisplayName', strcat(NetNames{2}), 'LineWidth', linewidth)
hold on;
for net = [3,4,5,7]
    plot(PdBm, squeeze(results(b1,net,:)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " (", int2str(results(b1,1,1)), " bits)"))
    plot(PdBm, squeeze(results(b2,net,:)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " (", int2str(results(b2,1,1)), " bits)"))
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
% title("Number of feedback bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('Achievable Rate (bps/Hz)')
legend('NumColumns', 1, 'location', 'northwest')
ylim([0, 25])
fontsize(gca,ftsz,"pixels")

%% Figure 3 - Rate vs Bits, 40 & 15 Tx dBm
bits = 1:10;
mark = {'o-', '', '', '', '', '', '*-'};
figure(3);
p = 7;
c = 1;
m = 1;
for net = [2,3,4,5,7]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " (", int2str(PdBm(p)), " dBm)"))
    c = c+1;
    m = m+1;
    hold on;
end
p = 3;
c = 1;
m = 1;
for net = [2,3,4,5,7]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'LineWidth', linewidth, ...
        'DisplayName', strcat(NetNames{net}, " (", int2str(PdBm(p)), " dBm)"))
    c = c+1;
    m = m+1;
    hold on;
end
hold off;
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
% title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
xlabel('Number of feedback bits')
ylabel('Achievable Rate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
% legend('location', 'eastoutside')
ylim([0, 25])
% set (gca, 'Xscale', 'log');
% set(gca,'XTick', results(bits,1,1));
fontsize(gca,ftsz,"pixels")

%% Figure 4 - Train/Val Loss Setup 1
% linewidth = 2;
ftsz = 20;
linewidth = 3;
figure(4);
loss = '3'; % 40 bits
AQEWMMSE_loss = readmatrix(dir + trial + "/40PdBm/AQE_loss" + loss + ".csv");
AQE_loss = readmatrix(dir + trial + "/06/40PdBm/AQEnoW_loss" + loss + ".csv");
ACF_loss = readmatrix(dir + trial + "/40PdBm/ACF_loss" + loss + ".csv");
linQ_loss = readmatrix(dir + trial + "/40PdBm/linQ_loss" + loss + ".csv");

plot(64000*AQEWMMSE_loss(:,1), '-', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE train', 'LineWidth', linewidth)
hold on;
plot(16000*AQEWMMSE_loss(:,2), '--', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE val', 'LineWidth', linewidth)
plot(64000*AQE_loss(:,1), '-', 'Color', colour_list{3}, 'DisplayName', 'AQE train', 'LineWidth', linewidth)
plot(16000*AQE_loss(:,2), '--', 'Color', colour_list{3}, 'DisplayName', 'AQE val', 'LineWidth', linewidth)
plot(64000*ACF_loss(:,1), '-', 'Color', colour_list{4}, 'DisplayName', 'ACF train', 'LineWidth', linewidth)
plot(16000*ACF_loss(:,2), '--', 'Color', colour_list{4}, 'DisplayName', 'ACF val', 'LineWidth', linewidth)
plot(64000*linQ_loss(:,1), '-', 'Color', colour_list{5}, 'DisplayName', 'linQ train', 'LineWidth', linewidth)
plot(16000*linQ_loss(:,2), '--', 'Color', colour_list{5}, 'DisplayName', 'linQ val', 'LineWidth', linewidth)
hold off;

xlabel('Epoch')
ylabel('Loss')
legend('NumColumns', 2, 'location', 'best')
ylim([-2700, -900])
fontsize(gca,ftsz,"pixels")
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')


%% Figure 5 - Train/Val Loss Setup 2
% linewidth = 2;
figure(5);
loss = '3'; % 40 bits
AQEWMMSE_loss = readmatrix(dir + trial + "/20PdBm/AQE_loss" + loss + ".csv");
AQE_loss = readmatrix(dir + trial + "/06/20PdBm/AQEnoW_loss" + loss + ".csv");
ACF_loss = readmatrix(dir + trial + "/20PdBm/ACF_loss" + loss + ".csv");
linQ_loss = readmatrix(dir + trial + "/20PdBm/linQ_loss" + loss + ".csv");

plot(64000*AQEWMMSE_loss(:,1), '-', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE train', 'LineWidth', linewidth)
hold on;
plot(16000*AQEWMMSE_loss(:,2), '--', 'Color', colour_list{2}, 'DisplayName', 'AQE-WMMSE val', 'LineWidth', linewidth)
plot(64000*AQE_loss(:,1), '-', 'Color', colour_list{3}, 'DisplayName', 'AQE train', 'LineWidth', linewidth)
plot(16000*AQE_loss(:,2), '--', 'Color', colour_list{3}, 'DisplayName', 'AQE val', 'LineWidth', linewidth)
plot(64000*ACF_loss(:,1), '-', 'Color', colour_list{4}, 'DisplayName', 'ACF train', 'LineWidth', linewidth)
plot(16000*ACF_loss(:,2), '--', 'Color', colour_list{4}, 'DisplayName', 'ACF val', 'LineWidth', linewidth)
plot(64000*linQ_loss(:,1), '-', 'Color', colour_list{5}, 'DisplayName', 'linQ train', 'LineWidth', linewidth)
plot(16000*linQ_loss(:,2), '--', 'Color', colour_list{5}, 'DisplayName', 'linQ val', 'LineWidth', linewidth)
hold off;

xlabel('Epoch')
ylabel('Loss')
legend('NumColumns', 2, 'location', 'best')
% ylim([-2700, -900])
fontsize(gca,ftsz,"pixels")
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')