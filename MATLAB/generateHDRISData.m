% This script generates transmit - receive signal data for a wireless 
% RIS-assisted communication system
clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src\")
%% Setup system model / script parameters
systemModelParameters

dataDir = "datasets/HDRISData/00/";
fileSaveName = dataDir + "HDRISData";
dfile = fileSaveName + ".txt";
if exist(dfile, 'file') ; delete(dfile); end
diary(dfile)
diary on
vars2save =       {"channel_type", ...
                   "LOS", ...
                   "B", ...
                   "L", ...
                   "T", ...
                   "K", ...
                   "M", ...
                   "N", ...
                   "Nw", ...
                   "Nh", ...
                   "Xu", ...
                   "Psi", ...
                   "Hur_mc", ...
                   "Hra_mc", ...
                   "Hua_mc", ...
                   ..."g0", ...
                   ..."d_AP_RIS", ...
                   ..."a_AP_RIS", ...
                   ..."d_AP_UE", ...
                   ..."a_AP_UE", ...
                   ..."d_UE_RIS", ...
                   ..."a_UE_RIS", ...
                   ..."g_si", ...
                   ..."SNRdB_list", ...
                   "mc_runs"};

%% Generate pilots and RIS phase shifts
Pu = 10^(SNRdB/10); % Transmission Power
Xu = sqrt(Pu).*dftmtx(K)/sqrt(K);
% Xu = sqrt(Pu).*eye(K);

[~,L] = size(Xu);
T = B*L; % training overhead

XU = repmat(Xu, [1,B]);

F_N1 = dftmtx(N+1);
Psi = zeros(B,N); % RIS phase shifts per block
for b = 1:B
    Psi(b,:) = F_N1(mod(b-1,N+1)+1, 2:end); % DFT scheme
end
ONES = ones(B,M+K);

%% Monte Carlo
% channel matrices vectorized by stacking column vectors via H(:) operator
% then transposed as row vectors so that each row is a mc run
Hur_mc = complex(zeros(mc_runs,N*K));
Hra_mc = complex(zeros(mc_runs,M*N));
Hua_mc = complex(zeros(mc_runs,M*K));

fprintf('Monte Carlo Run: ');
for mc_run = 1:mc_runs
if mod(mc_run,mc_runs/25) == 0
    fprintf('%i ', mc_run);
end
%% Create system model via channel matrices
generateHDRISchannels
% Creates Channel Matrices based on scructure of the channel
%     Hur = (N,K) UE  -> RIS
%     Hra = (M,N) RIS -> AP
%     Hua = (M,K) UE  -> AP

% %% Transmit Pilots through RIS communication system
% % TODO in future: use receive signal to perform channel estimation for
% % imperfect CSI
% Y = zeros(M,T); % Receive Signal
% for t = 1:T
%     b = floor((t-1)/L)+1;
% 
%     % Half-Duplex: UE -> RIS -> AP
%     Y(:,t) = Hua*XU(:,t) + ...
%              Hra*diag(Psi(b,:))*Hur*XU(:,t) + ...
%              sqrt(1/2)*(randn(M,1) + 1j*randn(M,1));
% end

Hur_mc(mc_run,:) = Hur(:).'; % Example:     hur <=> Hur(:)
Hra_mc(mc_run,:) = Hra(:).'; % vectorize:   hur = reshape(Hur, [N*K, 1])
Hua_mc(mc_run,:) = Hua(:).'; % unvectorize: Hur = reshape(hur, [N, K])
end % mc_run

%% Print
fprintf("\n\n");

%% Save data
save(fileSaveName + ".mat", vars2save{:})
A = [LOS, B, L, T, K, M, N, Nw, Nh, mc_runs];
Tab = array2table(A);
Tab.Properties.VariableNames(1:length(A)) = ...
    {'LOS', 'B', 'L', 'T', 'K', 'M', 'N', 'Nw', 'Nh', 'mc_runs'};
writetable(Tab,dataDir + "systemModelParameters.csv")
writematrix(Hur_mc, dataDir + "Hur.csv")
writematrix(Hra_mc, dataDir + "Hra.csv")
writematrix(Hua_mc, dataDir + "Hua.csv")
delete(gcp('nocreate'))
fprintf("Script Execution time:\n")
fprintElapsedTime(TSTART);
diary off


