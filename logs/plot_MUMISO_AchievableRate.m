% This script is a scratch pad to plot data from MU-MISO_AchievableRate/
clear all; close all; delete(gcp('nocreate')); clc;

dir = "MU-MISO_AchievableRateExperiments/";
results = zeros(6,11,7);
trial = "03";
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

b = 5; % Nc = 100
figure(1);
for net = 2:7
    plot(PdBm, squeeze(results(b,net,:)), 'o-', 'DisplayName', NetNames{net})
    hold on;
end
hold off;
grid on;
title("Number of feedback bits: ", int2str(results(b,1,1)) + " bits");
xlabel('Transmit Power (dBm)')
ylabel('AchievableRate (bps/Hz)')
legend('location', 'best')


bits = [1, 2, 3, 4, 6];
mark = {'o-', '', '', '', '', '', '*-'};
for p = 1:7
    figure
    for net = [2, 3, 4, 6, 7]
            plot(results(bits,1,1), squeeze(results(bits,net,p)), 'o-', 'DisplayName', NetNames{net})
            hold on;
    end
    hold off;
    set(gca,'xminorgrid','off','yminorgrid','off','xgrid','on','ygrid','on')
    title("Transmit Power: ", int2str(PdBm(p)) + " (dBm)");
    xlabel('Number of feedback bits')
    ylabel('AchievableRate (bps/Hz)')
    legend('location', 'best')
    set (gca, 'Xscale', 'log');
    set(gca,'XTick', results(bits,1,1));
end