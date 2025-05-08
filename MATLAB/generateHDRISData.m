% This script generates transmit - receive signal data for a wireless 
% RIS-assisted communication system along with optimal RIS phases and
% beamforming precoder
clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src")
%% Setup system model / script parameters
systemModelParameters

job_id = getenv("SLURM_ARRAY_TASK_ID");
dataDir = "~/scratch/datasets/HDRISData/13/";
%job_id = 0;
%dataDir = "datasets/HDRISData/13/";
rng(job_id)
dataDir = dataDir + num2str(job_id) + "/";
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
                   "d_ra", ...
                   "a_ra", ...
                   "d_ur", ...
                   "a_ur", ...
                   "d_ua", ...
                   "a_ua", ...
                   "g_ur", ...
                   "g_ra", ...
                   "g_ua", ...
                   "CH_err", ...
                   "SNRdB", ...
                   "SINRdB", ...
                   "mc_runs"};

%% Generate pilots and RIS phase shifts
P = 10^(SNRdB/10); % Transmission Power
Xu = sqrt(P).*dftmtx(K)/sqrt(K);
% Xu = sqrt(P).*eye(K);

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
nmse_Hru_mc = zeros(mc_runs,1);
nmse_Har_mc = zeros(mc_runs,1);
nmse_Hau_mc = zeros(mc_runs,1);
theta_mc = zeros(mc_runs,N); % optimal phase shifts
w_mc = zeros(mc_runs,M*K); % optimal beamforming
Ropt2_mc = zeros(mc_runs,1); % optimized receive signal (at the users)
Rrand2_mc = zeros(mc_runs,1); % random phases receive signal (at the users)

fprintf('Monte Carlo Run:\n');
for mc_run = 1:mc_runs
% if mod(mc_run,mc_runs/25) == 0
    fprintf('%i/%i\n', mc_run, mc_runs);
    fprintf("Script Execution time:\n")
    fprintElapsedTime(TSTART);
% end
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
Hru_true = Hur.';
Har_true = Hra.';
Hau_true = Hua.';

Hru = Hru_true + sqrt(CH_err*1/2)*(randn(K,N) + 1j*randn(K,N));
Har = Har_true + sqrt(CH_err*1/2)*(randn(N,M) + 1j*randn(N,M));
Hau = Hau_true + sqrt(CH_err*1/2)*(randn(K,M) + 1j*randn(K,M));

nmse_Hru = norm(Hru_true - Hru,'fro')^2 / norm(Hru_true,'fro')^2;
nmse_Har = norm(Har_true - Har,'fro')^2 / norm(Har_true,'fro')^2;
nmse_Hau = norm(Hau_true - Hau,'fro')^2 / norm(Hau_true,'fro')^2;

nmse_Hru_mc(mc_run) = nmse_Hru;
nmse_Har_mc(mc_run) = nmse_Har;
nmse_Hau_mc(mc_run) = nmse_Hau;
fprintf("nmse_Hru %.3e, nmse_Har %.3e, nmse_Hau %.3e\n", nmse_Hru, nmse_Har, nmse_Hau)

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

    theta = zeros(1,N);
    w_opt = zeros(1,M);
    for n = 1:N
        % Knowledge of Perfect CSI
        a_kk = angle(Hua);
        b = angle(Hra(1,n));
        c = angle(Hur(n,1));
        theta(1,n) = mod(a_kk - (b+c) + pi, 2*pi) - pi;
    end
    theta_rand = 2*pi*rand(1,N);
    Yopt = Hua + Hra*diag(exp(1j*theta))*Hur;
    Yrand = Hua + Hra*diag(exp(1j*theta_rand))*Hur;

    Ropt = Yopt'*Yopt;
    Rrand = Yrand'*Yrand;

elseif K == 1 % MISO system model

%     % find optimal phases for only the k-th user
%     for k = 1:K
%         hau = Hau(k,:);
%         hru = Hru(k,:);
%         Phi = diag(hru)*Har;
%         R = [Phi*Phi', Phi*hau'; hau*Phi', 0];
% 
%         % to install cvx see: https://cvxr.com/cvx/doc/install.html
%         cvx_begin quiet
%             variable V(N+1,N+1) complex semidefinite
%             maximize(trace(R*V))
%             diag(V) == 1
%         cvx_end
% 
%         [U,D] = eig(V);
%         r = 1/sqrt(2)*(rand(N+1,1) + 1j*rand(N+1,1));
%         v = U*sqrt(D)*r;
%         theta_opt(:,k) = angle(v(1:N) / v(N+1));
%         
%         y = hau + hru*diag(exp(1j*theta_opt(:,k)))*Har;
%         W_opt(:,k) = y' / norm(y);
%     end

else
    % Solve for beamforming matrix and RIS phase shifts
    % Hua = MxK scalar
    % Hra = MxN row vector
    % Hur = NxK column vector, K single antenna users
    % Solution can be found as a homogeneous QCPQ
    % [1] Q. Wu and R. Zhang, “Intelligent Reflecting Surface Enhanced 
    % Wireless Network via Joint Active and Passive Beamforming,” IEEE 
    % Trans. Wirel. Commun., vol. 18, no. 11, pp. 5394–5409, Nov. 2019, 
    % doi: 10.1109/TWC.2019.2936025.
    
    %% Alternating Optimization Algorithm
    max_iterations = 30;
    W_opt = zeros(M,K);
    gammavar = 10^(SINRdB/10)*ones(K,1); % SINR constraint for all users
    tx_power_prev = Inf;
    Ropt = zeros(K,1);
    Rrand = zeros(K,1);

    % 1. Initialize phase shifts to be optimal without beamforming
    cvx_begin quiet
        variable V(N+1,N+1) complex semidefinite
        variable alphavar(K) % SINR residual of user k
        maximize sum(alphavar)
        
        subject to
        for k = 1:K
            hau = Hau(k,:);
            hru = Hru(k,:);
            a_kk = diag(hru)*Har;
            b_kk = hau;
            Rkk = [a_kk*a_kk', a_kk*b_kk'; ...
                   b_kk*a_kk', 0];
            trace(Rkk*V) + b_kk*b_kk' >= alphavar(k);
            alphavar(k) >= 0;
        end
        diag(V) == 1;
    cvx_end
%     fprintf(['Initialize RIS: ', cvx_status, '\n']);

    % Gaussian random vector to obtain approximate best rank 1 vector
    [U,D] = eig(V);
    num_r = 1000;
    r = 1/sqrt(2)*(rand(N+1,num_r) + 1j*rand(N+1,num_r));
    v = U*sqrt(D)*r;
    v_init = v(:,1);
    Cost_init = 0;
    for n = 1:num_r
        Cost = 0;
        for k = 1:K
            hau = Hau(k,:);
            hru = Hru(k,:);
            a_kk = diag(hru)*Har;
            b_kk = hau;
            Rkk = [a_kk*a_kk', a_kk*b_kk'; ...
                   b_kk*a_kk', 0];
            Cost = Cost + (v(:,n)'*Rkk*v(:,n)) + b_kk*b_kk';
        end
        if Cost > Cost_init
            Cost_init = Cost;
            v_init = v(:,n);
            n_init = n;
        end
    end
    theta = angle(v_init(1:N) / v_init(N+1));

    for iter = 1:max_iterations
        % 2. Solve P3 for given RIS phases to obtain beamforming
        % Solve for W multiuser beamforming via powerscaling constraint
        % https://github.com/emilbjornson/optimal-beamforming/blob/master/functionFeasibilityProblem_cvx.m
        % [1] Z. Q. Luo and W. Yu, “An introduction to convex optimization 
        % for communications and signal processing,” IEEE J. Sel. Areas 
        % Commun., vol. 24, no. 8, pp. 1426–1438, Aug. 2006, 
        % doi: 10.1109/JSAC.2006.879347.
        cvx_begin quiet
            variable W(M,K) complex % beamforming matrix k data streams for M transmit antennas
            variable betavar % power scaling constraint

            minimize betavar % minimize the power indirectly by scaling power constraint
            
            subject to

            % SINR constraints (K users)
            w_sum = 0;
            for k = 1:K
                % complete communication channel to the kth user
                hk = Hau(k,:) + Hru(k,:)*diag(exp(1j*theta))*Har;
                
                % Useful link is assumed to be real-valued
                imag(hk*W(:,k)) == 0;
                % SOCP formulation for the SINR constraint of user k
                sqrt(1 + 1/gammavar(k))*real(hk*W(:,k)) >= norm([hk*W(:,[1:k-1 k+1:K]) 10^(-SNRdB/20)]);
                w_sum = w_sum + W(:,k)'*W(:,k);
            end
            
            %Power constraints scaled by the variable betavar
            w_sum <= betavar;
            
            betavar >= 0; % Power constraints must be positive
        cvx_end
%         fprintf(['AO: ', cvx_status, ', ']);

        % 3. Solve problem P4' for given beamforming matrix
        theta_prev = theta;
        cvx_begin quiet
            variable V(N+1,N+1) complex semidefinite
            variable alphavar(K) % SINR residual of user k
            maximize sum(alphavar)
            
            subject to
            for k = 1:K
                hau = Hau(k,:);
                hru = Hru(k,:);
                a_kk = diag(hru)*Har*W(:,k);
                b_kk = hau*W(:,k);
                Rkk = [a_kk*a_kk', a_kk*b_kk'; ...
                       b_kk*a_kk', 0];
                s = 0;
                for j = 1:K
                    if j ~= k
                        a_kj = diag(hru)*Har*W(:,j);
                        b_kj = hau*W(:,j);
                        Rkj = [a_kj*a_kj', a_kj*b_kj'; ...
                               b_kj*a_kj', 0];
                        s = s + trace(Rkj*V) + b_kj*b_kj';
                    end
                end
                trace(Rkk*V) + b_kk*b_kk' >= gammavar(k)*(s + 10^(-SNRdB/10)) + alphavar(k);
                alphavar(k) >= 0;
            end
            diag(V) == 1;
        cvx_end
%         fprintf([cvx_status, '\n']);
        
        if strcmp(cvx_status, 'Infeasible')
            W_opt = W;
            theta_opt = theta;
            break
        else
            % Gaussian random vector to obtain approximate best rank 1 vector
            [U,D] = eig(V);
            num_r = 1000;
            r = 1/sqrt(2)*(rand(N+1,num_r) + 1j*rand(N+1,num_r));
            v = U*sqrt(D)*r;
            v_best = v(:,1);
            Cost_best = 0;
            for n = 1:num_r
                Cost = 0;
                for k = 1:K
                    hau = Hau(k,:);
                    hru = Hru(k,:);
                    a_kk = diag(hru)*Har*W(:,k);
                    b_kk = hau*W(:,k);
                    Rkk = [a_kk*a_kk', a_kk*b_kk'; ...
                           b_kk*a_kk', 0];
                    s = 0;
                    for j = 1:K
                        if j ~= k
                            a_kj = diag(hru)*Har*W(:,j);
                            b_kj = hau*W(:,j);
                            Rkj = [a_kj*a_kj', a_kj*b_kj'; ...
                                   b_kj*a_kj', 0];
                            s = s + (v(:,n)'*Rkj*v(:,n) + b_kj*b_kj');
                        end
                    end
                    Cost = Cost + ((v(:,n)'*Rkk*v(:,n)) + b_kk*b_kk') / (s + 10^(-SNRdB/10));
                end
                if Cost > Cost_best
                    Cost_best = Cost;
                    v_best = v(:,n);
                    n_best = n;
                end
            end
            theta = angle(v_best(1:N) / v_best(N+1));
        end

        % 4. Stop when infeasible or the transmit power stops decreasing
        tx_power = norm(W,'fro');
        fprintf('%i: %.4e\n', iter, tx_power);

        if tx_power_prev - tx_power > 10^(-SNRdB/10)
            tx_power_prev = tx_power;
            W_opt = W;
            theta_opt = theta;
        else
            break
        end

    end % 5. End Alternating Optimization

%     W_opt = P*W_opt/norm(W_opt,'fro');

    % Compare optimal phases vs random phases given optimal beamforming
    for k = 1:K 
        hau = Hau_true(k,:);
        hru = Hru_true(k,:);
        theta_rand = 2*pi*rand(1,N) - pi;
        h_opt = hau + hru*diag(exp(1j*theta_opt))*Har_true;
        h_rand = hau + hru*diag(exp(1j*theta_rand))*Har_true;
        intf_opt = 10^(-SNRdB/10);
        intf_rand = 10^(-SNRdB/10);
        for l = 1:K
            if l ~= k
                intf_opt = intf_opt + norm(h_opt*W_opt(:,l))^2;
                intf_rand = intf_rand + norm(h_rand*W_opt(:,l))^2;
            end
        end
        Ropt(k) = log2(1 + norm(h_opt*W_opt(:,k))^2 / intf_opt);
        Rrand(k) = log2(1 + norm(h_rand*W_opt(:,k))^2 / intf_rand);
    end
    
    theta_opt = theta_opt.'; % stack all phases into one row vector
    w_opt = W_opt(:).';
end

% Example:     hur <=> Hur(:) for Hur = N by K matrix
% vectorize:   hur = reshape(Hur, [N*K,1]), stack columns into one column
% unvectorize: Hur = reshape(hur, [N,K]), unstack into K columns
Hru_mc(mc_run,:) = Hru_true(:).';
Har_mc(mc_run,:) = Har_true(:).';
Hau_mc(mc_run,:) = Hau_true(:).';
theta_mc(mc_run,:) = theta_opt.';  % optimized RIS phase shifts
w_mc(mc_run,:) = w_opt;  % optimized beamforming matrix
Ropt2_mc(mc_run,:) = sum(Ropt); % test receive signal is optimized
Rrand2_mc(mc_run,:) = sum(Rrand); % test receive signal is optimized
end % mc_run

%% Print
fprintf("\n------------------------------------------------------------\n")
fprintf("Mean Sum Rate over montecarlo runs:\n");
fprintf("Optimized RIS: %.4f\n", mean(Ropt2_mc, 1));
fprintf("Random RIS: %.4f\n", mean(Rrand2_mc, 1));
fprintf("Average Channel Error:\n")
fprintf("nmse_Hru %.3e, nmse_Har %.3e, nmse_Hau %.3e\n", ...
    mean(nmse_Hru_mc), mean(nmse_Har_mc), mean(nmse_Hau_mc))

%% Save data
save(fileSaveName + ".mat", vars2save{:})
A = [LOS, K, M, N, Nw, Nh, ...
    d_ra, a_ra, d_ur, a_ur, d_ua, a_ua, ...
    g_ur, g_ra, g_ua, CH_err, SNRdB, SINRdB, mc_runs];
Tab = array2table(A);
Tab.Properties.VariableNames(1:length(A)) = ...
{'LOS', 'K', 'M', 'N', 'Nw', 'Nh', ...
 'd_ra', 'a_ra', 'd_ur', 'a_ur', 'd_ua', 'a_ua', ...
 'g_ur', 'g_ra', 'g_ua', 'CH_err', 'SNRdB', 'SINRdB', 'mc_runs'};
writetable(Tab, dataDir + "systemModelParameters.csv")

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
writematrix(theta_mc, dataDir + "RISopt.csv") % N RIS elements
writematrix(w_mc, dataDir + "beamforming.csv") % W is MxK, w = W(:).'
writematrix(real(w_mc), dataDir + "wopt_r.csv")
writematrix(imag(w_mc), dataDir + "wopt_i.csv")

delete(gcp('nocreate'))
fprintf("Script Execution time:\n")
fprintElapsedTime(TSTART);
diary off


