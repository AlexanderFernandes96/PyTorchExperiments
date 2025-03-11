% This script generates transmit - receive signal data for a wireless 
% RIS-assisted communication system
clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src\")
%% Setup system model / script parameters
systemModelParameters

dataDir = "datasets/HDRISData/05/";
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
theta_mc = zeros(mc_runs,N); % optimal phase shifts
Yopt2_mc = zeros(mc_runs,M); % optimized receive signal (at base station)

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
% % TODO: receive signal for channel estimation
% Y = zeros(M,T); % Receive Signal Half-Duplex: UE -> RIS -> AP
% for t = 1:T
%     b = floor((t-1)/L)+1;
% 
%     if M == 1 && K == 1 % SISO system model, no AP/UE beamforming
%         Y(:,t) = Hua*XU(:,t) + ...
%                  Hra*diag(Psi(b,:))*Hur*XU(:,t) + ...
%                  sqrt(1/2)*(randn(M,1) + 1j*randn(M,1));
%     end
% 
% end

%% Optimize phase shifts and beamforming 
% system model: 
% Y = Hua*W*Xu + Hra*diag(exp(1j*theta))*Hur*W*Xu + N

if M == 1 && K == 1 % SISO system model
    % No beamforming matrix only RIS phase shifts to optimize
    % Hua = 1x1 scalar
    % Hra = 1xN row vector
    % Hur = Nx1 column vector
    % Solution is equation (21) from:
    % [1] Q. Wu, S. Zhang, B. Zheng, C. You, and R. Zhang, "Intelligent 
    % Reflecting Surface-Aided Wireless Communications: A Tutorial,” IEEE 
    % Trans. Commun., vol. 69, no. 5, pp. 3313–3351, May 2021, doi: 
    % 10.1109/TCOMM.2021.3051897.
    % modified using our 
    % (21) max_theta | Hua + Hra*diag(exp(1j*theta))*Hur) |^2
    %      st. 0 <= theta <= 2*pi

    theta = zeros(1,N);
    for n = 1:N
        % Knowledge of Perfect CSI
        a = angle(Hua);
        b = angle(Hra(1,n));
        c = angle(Hur(n,1));
        theta(1,n) = mod(a - (b+c) + pi, 2*pi) - pi;
    end
    
    Yopt = Hua + Hra*diag(exp(1j*theta))*Hur;
end


Hur_mc(mc_run,:) = Hur(:).';     % Example:     hur <=> Hur(:)
Hra_mc(mc_run,:) = Hra(:).';     % vectorize:   hur = reshape(Hur, [N*K,1])
Hua_mc(mc_run,:) = Hua(:).';     % unvectorize: Hur = reshape(hur, [N,K])
theta_mc(mc_run,:) = theta;      % optimized RIS phase shifts
Yopt2_mc(mc_run,:) = Yopt'*Yopt; % test receive signal is optimized
end % mc_run

%% Print
fprintf("\n\n");
fprintf(" Optimized receive signal: mean(Yopt' * Yopt) = %.4f\n", ...
    mean(Yopt2_mc, 1));

%% Save data
save(fileSaveName + ".mat", vars2save{:})
A = [LOS, B, L, T, K, M, N, Nw, Nh, mc_runs];
Tab = array2table(A);
Tab.Properties.VariableNames(1:length(A)) = ...
    {'LOS', 'B', 'L', 'T', 'K', 'M', 'N', 'Nw', 'Nh', 'mc_runs'};
writetable(Tab,dataDir + "systemModelParameters.csv")

% Save channels
% real
writematrix(real(Hur_mc), dataDir + "Hur_r.csv") 
writematrix(real(Hra_mc), dataDir + "Hra_r.csv")
writematrix(real(Hua_mc), dataDir + "Hua_r.csv")
% imaginary
writematrix(imag(Hur_mc), dataDir + "Hur_i.csv") 
writematrix(imag(Hra_mc), dataDir + "Hra_i.csv")
writematrix(imag(Hua_mc), dataDir + "Hua_i.csv")

% Save optimal RIS phase shifts (-pi <= theta < pi)
writematrix(theta_mc, dataDir + "RISopt.csv")

delete(gcp('nocreate'))
fprintf("Script Execution time:\n")
fprintElapsedTime(TSTART);
diary off


