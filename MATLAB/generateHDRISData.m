% This script generates transmit - receive signal data for a wireless 
% RIS-assisted communication system
clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src")
%% Setup system model / script parameters
systemModelParameters

% dataDir = "~/scratch/datasets/HDRISData/09/test2/";
dataDir = "datasets/HDRISData/09/test2/";
mkdir(dataDir);
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
                   ..."Hur_mc", ...
                   ..."Hra_mc", ...
                   ..."Hua_mc", ...
                   "Hru_mc", ...
                   "Har_mc", ...
                   "Hau_mc", ...
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
% Uplink:
% Hur_mc = complex(zeros(mc_runs,N*K));
% Hra_mc = complex(zeros(mc_runs,M*N));
% Hua_mc = complex(zeros(mc_runs,M*K));
% Downlink:
Hru_mc = complex(zeros(mc_runs,N*K));
Har_mc = complex(zeros(mc_runs,M*N));
Hau_mc = complex(zeros(mc_runs,M*K));
theta_mc = zeros(mc_runs,N*K); % optimal phase shifts
w_mc = zeros(mc_runs,M*K); % optimal beamforming
Yopt2_mc = zeros(mc_runs,1); % optimized receive signal (at the users)
Yrand2_mc = zeros(mc_runs,1); % random phases receive signal (at the users)

fprintf('Monte Carlo Run: ');
for mc_run = 1:mc_runs
if mod(mc_run,mc_runs/25) == 0
    fprintf('%i/%i\n', mc_run, mc_runs);
    fprintf("Script Execution time:\n")
    fprintElapsedTime(TSTART);
end
%% Create system model via channel matrices
generateHDRISchannels
% Creates Channel Matrices based on scructure of the channel
% Uplink:
%     Hur = (N,K) UE  -> RIS
%     Hra = (M,N) RIS -> AP
%     Hua = (M,K) UE  -> AP
% Downlink: channels reciprocity makes them matrix transpose equivalent
%     Hru = (K,N) RIS -> UE
%     Har = (N,M) AP  -> RIS
%     Hau = (K,M) AP  -> UE
Hru = Hur.';
Har = Hra.';
Hau = Hua.';

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
% SISO:
% Y = Hua*Xu + Hra*diag(exp(1j*theta))*Hur*Xu + N (Uplink)
% Y = Hau*Xa + Hru*diag(exp(1j*theta))*Har*Xa + N (Downlink)
% MISO:
% Y = W*(Hua + Hra*diag(exp(1j*theta))*Hur)*xu + N (Uplink)
% y = (hau + hru*diag(exp(1j*theta))*Har)*W*Xa + N (Downlink)

if M == 1 && K == 1 % SISO system model
    % No beamforming matrix only RIS phase shifts to optimize
    % Hua = 1x1 scalar
    % Hra = 1xN row vector
    % Hur = Nx1 column vector
    % SISO optimal phases are the same regardless of Uplink/Downlink
    % Solution is equation (21) from:
    % [1] Q. Wu, S. Zhang, B. Zheng, C. You, and R. Zhang, "Intelligent 
    % Reflecting Surface-Aided Wireless Communications: A Tutorial,” IEEE 
    % Trans. Commun., vol. 69, no. 5, pp. 3313–3351, May 2021, doi: 
    % 10.1109/TCOMM.2021.3051897.
    % modified using our 
    % (21) max_theta | hua + hra*diag(exp(1j*theta))*hur) |^2
    %      st. 0 <= theta <= 2*pi

    theta_opt = zeros(1,N);
    w_opt = zeros(1,M);
    for n = 1:N
        % Knowledge of Perfect CSI
        a = angle(Hua);
        b = angle(Hra(1,n));
        c = angle(Hur(n,1));
        theta_opt(1,n) = mod(a - (b+c) + pi, 2*pi) - pi;
    end
    theta_rand = 2*pi*rand(1,N);
    Yopt = Hua + Hra*diag(exp(1j*theta_opt))*Hur;
    Yrand = Hua + Hra*diag(exp(1j*theta_rand))*Hur;

    Yopt2 = Yopt'*Yopt;
    Yrand2 = Yrand'*Yrand;
else
    % Solve for beamforming matrix and RIS phase shifts
    % Hua = MxK scalar
    % Hra = MxN row vector
    % Hur = NxK column vector, K single antenna users
    % Solution can be found as a homogeneous QCPQ
    % [1] Q. Wu and R. Zhang, “Intelligent Reflecting Surface Enhanced 
    % Wireless Network: Joint Active and Passive Beamforming Design,” Proc.
    % IEEE Glob. Commun. Conf. GLOBECOM, 2018, 
    % doi: 10.1109/GLOCOM.2018.8647620.
    
    theta_opt = zeros(N,k);
    w_opt = zeros(M,k);
    Yopt2 = zeros(K,1);
    Yrand2 = zeros(K,1);
    for k = 1:K % find optimal phases for each k-th user
        hau = Hau(k,:);
        hru = Hru(k,:);
        Phi = diag(hru)*Har;
        R = [Phi*Phi', Phi*hau'; hau*Phi', 0];

        % to install cvx see: https://cvxr.com/cvx/doc/install.html
        cvx_begin quiet
            variable V(N+1,N+1) complex semidefinite
            maximize(trace(R*V))
            diag(V) == 1
        cvx_end

        [U,D] = eig(V);
        r = 1/sqrt(2)*(rand(N+1,1) + 1j*rand(N+1,1));
        v = U*sqrt(D)*r;
        theta_opt(:,k) = angle(v(1:N) / v(N+1));
        
        y = hau + hru*diag(exp(1j*theta_opt(:,k)))*Har;
        w_opt(:,k) = y' / norm(y);
        
        theta_rand = 2*pi*rand(1,N);
        y_rand = hau + hru*diag(exp(1j*theta_rand))*Har;
        w_rand = y' / norm(y_rand);
        Yopt = (hau + hru*diag(exp(1j*theta_opt(:,k)))*Har)*w_opt(:,k);
        Yrand = (hau + hru*diag(exp(1j*theta_rand))*Har)*w_rand;
        
        Yopt2(k) = Yopt*Yopt';
        Yrand2(k) = Yrand*Yrand';
    end
    theta_opt = theta_opt(:).'; % stack all user phases into one row vector
    w_opt = w_opt(:).';
end

% Example:     hur <=> Hur(:) for Hur = N by K matrix
% vectorize:   hur = reshape(Hur, [N*K,1]), stack columns into one column
% unvectorize: Hur = reshape(hur, [N,K]), unstack into K columns
Hru_mc(mc_run,:) = Hru(:).';     
Har_mc(mc_run,:) = Har(:).';     
Hau_mc(mc_run,:) = Hau(:).';     
theta_mc(mc_run,:) = theta_opt;  % optimized RIS phase shifts
w_mc(mc_run,:) = w_opt;  % optimized beamforming matrix
Yopt2_mc(mc_run,:) = mean(Yopt2); % test receive signal is optimized
Yrand2_mc(mc_run,:) = mean(Yrand2); % test receive signal is optimized
end % mc_run

%% Print
fprintf("\n\n");
fprintf("Optimized receive signal: mean(||Yopt||^2) = %.4f\n", ...
    mean(Yopt2_mc, 1));
fprintf("Random receive signal: mean(||Yrand||^2) = %.4f\n", ...
    mean(Yrand2_mc, 1));

%% Save data
save(fileSaveName + ".mat", vars2save{:})
A = [LOS, B, L, T, K, M, N, Nw, Nh, mc_runs];
Tab = array2table(A);
Tab.Properties.VariableNames(1:length(A)) = ...
    {'LOS', 'B', 'L', 'T', 'K', 'M', 'N', 'Nw', 'Nh', 'mc_runs'};
writetable(Tab,dataDir + "systemModelParameters.csv")

% Save channels into a single csv file
% % Uplink
% % real
% writematrix(real(Hur_mc), dataDir + "Hur_r.csv") 
% writematrix(real(Hra_mc), dataDir + "Hra_r.csv")
% writematrix(real(Hua_mc), dataDir + "Hua_r.csv")
% % imaginary
% writematrix(imag(Hur_mc), dataDir + "Hur_i.csv") 
% writematrix(imag(Hra_mc), dataDir + "Hra_i.csv")
% writematrix(imag(Hua_mc), dataDir + "Hua_i.csv")

% Downlink
% real
writematrix(real(Hru_mc), dataDir + "Hru_r.csv") 
writematrix(real(Har_mc), dataDir + "Har_r.csv")
writematrix(real(Hau_mc), dataDir + "Hau_r.csv")
% imaginary
writematrix(imag(Hru_mc), dataDir + "Hru_i.csv") 
writematrix(imag(Har_mc), dataDir + "Har_i.csv")
writematrix(imag(Hau_mc), dataDir + "Hau_i.csv")

% Save optimal RIS phase shifts (-pi <= theta < pi) and beamforming matrix
writematrix(theta_mc, dataDir + "RISopt.csv")
writematrix(w_mc, dataDir + "beamforming.csv")

delete(gcp('nocreate'))
fprintf("Script Execution time:\n")
fprintElapsedTime(TSTART);
diary off


