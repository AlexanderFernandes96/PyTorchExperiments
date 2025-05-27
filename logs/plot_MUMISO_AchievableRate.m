%% Start
% This script is a scratch pad to plot data from MU-MISO_AchievableRate/
% clear all; close all; delete(gcp('nocreate')); clc;

%% Plot parameters
% Colours
% green = [27,158,119]./255;
% orange = [217,95,2]./255;
% purple = [117,112,179]./255;
% brown = [165,42,42]./255;
% blue = [51,51,255]./255;
% magenta = [255, 0, 255]./255;
% indigo = [75,0,130]./255;
% red = [255, 0, 0]./255;

% https://colorbrewer2.org/#type=qualitative&scheme=Accent&n=5
red =  [228,26,28]./255;
blue = [55,126,184]./255;
green = [77,175,74]./255;
purple = [152,78,163]./255;
orange =   [255,127,0]./255;

colour_list = {red, blue, green, purple, orange};
marker_list = {'o', 's', 'd', '^', 'v', 'x', '+', '*', '<', '>'};

dir = "MU-MISO_AchievableRateExperiments/";
results = zeros(6,11,7);
trial = "04modified";
opts = detectImportOptions(dir + trial + "/10PdBm/results.csv");
NetNames = strrep(strrep(opts.VariableNames, 'R_', ''),'_',' ');
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

b = 10;
c = 1;
m = 1;
figure(1);
for net = 2:6
    plot(PdBm, squeeze(results(b,net,:)), '-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net})
    c = c+1;
    m = m+1;
    hold on;
end
c = 1;
for net = 7:11
    plot(PdBm, squeeze(results(b,net,:)), '--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', NetNames{net})
    c = c+1;
    m = m+1;
end
hold off;
grid on;
% title("Number of feedback bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('AchievableRate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
ylim([0, 25])

b = 9;
m = 1;
figure(2);
c = 1;
for net = [3,4,6]
    plot(PdBm, squeeze(results(b,net,:)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', strcat(NetNames{net}, " (", int2str(results(b,1,1)), " bits)"))
    c = c+1;
    m = m+1;
    hold on;
end
plot(PdBm, squeeze(results(b,2,:)), 'k+-', 'DisplayName', strcat(NetNames{2}))
b = 1;
c = 1;
for net = [3,4,6]
    plot(PdBm, squeeze(results(b,net,:)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', strcat(NetNames{net}, " (", int2str(results(b,1,1)), " bits)"))
    c = c+1;
    m = m+1;
end
hold off;
grid on;
% title("Number of feedback bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('AchievableRate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
ylim([0, 25])


bits = 1:10;
mark = {'o-', '', '', '', '', '', '*-'};
figure(3);
p = 6;
c = 1;
m = 1;
for net = [2, 3, 4, 6]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', strcat(NetNames{net}, " (", int2str(PdBm(p)), " dBm)"))
    c = c+1;
    m = m+1;
    hold on;
end
p = 2;
c = 1;
for net = [2, 3, 4, 6]
    plot(results(bits,1,1), squeeze(results(bits,net,p)), '*--', 'Color', colour_list{c}, ...
        'Marker', marker_list{m}, 'DisplayName', strcat(NetNames{net}, " (", int2str(PdBm(p)), " dBm)"))
    c = c+1;
    m = m+1;
    hold on;
end
hold off;
set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
% title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
xlabel('Number of feedback bits')
ylabel('AchievableRate (bps/Hz)')
legend('NumColumns', 2, 'location', 'best')
% legend('location', 'eastoutside')
ylim([0, 25])
% set (gca, 'Xscale', 'log');
% set(gca,'XTick', results(bits,1,1));


% % bits = [1,2,3,4,6];
% bits = 1:10;
% mark = {'o-', '', '', '', '', '', '*-'};
% for p = 1:7
%     figure
%     for net = [2, 3, 4, 6, 7]
%             plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'DisplayName', NetNames{net})
%             hold on;
%     end
%     hold off;
%     set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
%     title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
%     xlabel('Number of feedback bits')
%     ylabel('AchievableRate (bps/Hz)')
%     legend('location', 'best')
%     ylim([0, 25])
% %     set (gca, 'Xscale', 'log');
% %     set(gca,'XTick', results(bits,1,1));
% end
% bits = [1,2,3,4,6];
