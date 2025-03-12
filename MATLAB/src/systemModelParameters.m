%% Parameters
mc_runs = 100;
% M = 8;  % AP
% K = 6;  % Users
% Nw = 8;
% Nh = 8;
% N = Nw*Nh; % RIS
% LOS = 3; % Number of LOS paths
% M = 4;  % AP
% K = 3;  % Users
M = 1;  % AP
K = 1;  % Users
% Nw = 10;
% Nh = 10;
Nw = 25;
Nh = 25;
N = Nw*Nh; % Number of RIS elements
LOS = 2; % Number of LOS paths
B = N+1; % Number of RIS transmission blocks
SNRdB = 0;
% channel_type = 'unstructured';
channel_type = 'geometric';
g_si = 1; % Self-Interference gain due to environmental reflections
g_dp = 1; % Direct-Path gain
g_cc = 1; % RIS cascaded channels gain

% Generate pilot scheme based on energy or power constraint: use E or P
% pilot_scheme = "S1P"; % Scheme 1: Simultaneous transmission
% pilot_scheme = "S2P"; % Scheme 2: Nonsimultaneous transmission

% B_list = N+1:-1:25;
% B_list = N+1:-1:35;
% B_list = N+1:-1:13;
% B_list = N+1:-1:7;
% B_list = N-10:-1:N-10;
% SNRdB_list = 0:5:30;
SNRdB_list = 0:5:40;
% Nw_list = 2:1:5;
% Nh_list = Nw_list;
% Nh_list = 10.*ones(1,length(Nw_list));
% N_list = Nw_list .* Nh_list;
