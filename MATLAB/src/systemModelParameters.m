%% Parameters
mc_runs = 5000;
% M = 8;  % AP
% K = 6;  % Users
% Nw = 8;
% Nh = 8;
% N = Nw*Nh; % RIS
% LOS = 3; % Number of LOS paths
M = 4;  % AP
K = 3;  % Users
% M = 1;  % AP
% K = 1;  % Users
% Nw = 10;
% Nh = 10;
% Nw = 8;
% Nh = 8;
Nw = 10;
Nh = 10;
N = Nw*Nh; % Number of RIS elements
LOS = 5; % Number of LOS paths
B = N+1; % Number of RIS transmission blocks
SNRdB = 80;
SINRdB = 20;
% channel_type = 'unstructured';
channel_type = 'geometric';
g_ur = 10^(-6/10); % User-RIS gain
g_ra = 10^(-8/10); % RIS-AP gain
g_ua = 10^(-10/10); % Direct-Path gain
CH_err = 10^(-40/10);

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
