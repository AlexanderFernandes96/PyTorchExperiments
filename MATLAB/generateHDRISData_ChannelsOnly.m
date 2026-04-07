% This script generates transmit - receive signal data for a wireless 
% RIS-assisted communication system along with optimal RIS phases and
% beamforming precoder
clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src")
%% Setup system model / script parameters
systemModelParameters

% job_id = 3;
% rng(job_id)
for CH_err = [10^(-45/10), 10^(-40/10), 10^(-35/10), 10^(-30/10), 10^(-25/10), 10^(-20/10)]
    %% Generate pilots and RIS phase shifts
    P = 10^(PdBm/10); % Transmission Power
    SNR = 10^(SNRdB/10);
    
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
    Hru_err_mc = complex(zeros(mc_runs,N*K));
    Har_err_mc = complex(zeros(mc_runs,M*N));
    Hau_err_mc = complex(zeros(mc_runs,M*K));
    nmse_Hru_mc = zeros(mc_runs,1);
    nmse_Har_mc = zeros(mc_runs,1);
    nmse_Hau_mc = zeros(mc_runs,1);
    nmse_h_mc = zeros(mc_runs,1);
    theta_mc = zeros(mc_runs,N); % optimal phase shifts
    w_mc = zeros(mc_runs,M*K); % optimal beamforming
    Ropt2_mc = zeros(mc_runs,1); % optimized receive signal (at the users)
    Rrand2_mc = zeros(mc_runs,1); % random phases receive signal (at the users)
    
    fprintf('Monte Carlo Run:\n');
    mc_run_print = mc_runs/1000;
    parfor mc_run = 1:mc_runs
    % if mod(mc_run,mc_runs/mc_run_print) == 0
    %     fprintf('%i/%i\n', mc_run, mc_runs);
    %     fprintElapsedTime(TSTART);
    % end
    %% Create system model via channel matrices
    % generateHDRISchannels % This script creates uplink channels, 
    %                       % can generate the downlink using the uplink model.
    
    if strcmp(channel_type, 'unstructured')
        % Rayleigh
        Hur = sqrt(1/2)*(randn(N,K) + 1j*randn(N,K)); % UE  -> RIS
        Hra = sqrt(1/2)*(randn(M,N) + 1j*randn(M,N)); % RIS -> AP
        Hua = sqrt(1/2)*(randn(M,K) + 1j*randn(M,K)); % UE  -> AP
    elseif strcmp(channel_type, 'geometric')
        % geometric
        Hur = zeros(N,K);                                % UE  -> RIS
        for k = 1:K
            Hur(:,k) = generateLOSchannel([Nw,Nh],2, 1,1, LOS);
        end
        Hra = generateLOSchannel(M,1, [Nw,Nh],2, LOS);   % RIS -> AP
        Hua = zeros(M,K);                                % UE  -> AP
        for k = 1:K
            Hua(:,k) = generateLOSchannel(M,1, 1,1, LOS);
        end
    end
    
    Hur = sqrt(g_ur)*Hur/norm(Hur,2);
    Hra = sqrt(g_ra)*Hra/norm(Hra,2);
    Hua = sqrt(g_ua)*Hua/norm(Hua,2);
    
    % Creates Channel Matrices based on scructure of the channel
    % Uplink:
    %     Hur = (N,K) UE  -> RIS
    %     Hra = (M,N) RIS -> AP
    %     Hua = (M,K) UE  -> AP
    % Downlink: reciprocal channels implies matrix transpose equivalent
    %     Hru = (K,N) RIS -> UE
    %     Har = (N,M) AP  -> RIS
    %     Hau = (K,M) AP  -> UE
    Hru = Hur.';
    Har = Hra.';
    Hau = Hua.';
    
    % Introduce Channel Estimation Errors:
    Hru_true = Hru;
    Har_true = Har;
    Hau_true = Hau;
    
    Hru_err = sqrt(CH_err*1/2)*(randn(K,N) + 1j*randn(K,N)) * norm(Hru_true,'fro');
    Har_err = sqrt(CH_err*1/2)*(randn(N,M) + 1j*randn(N,M)) * norm(Har_true,'fro');
    Hau_err = sqrt(CH_err*1/2)*(randn(K,M) + 1j*randn(K,M)) * norm(Hau_true,'fro');
    
    Hru = Hru_true + Hru_err;
    Har = Har_true + Har_err;
    Hau = Hau_true + Hau_err;
    
    HruHar_kr = khatrirao(Hru, Har.');
    h = [Hau(:); HruHar_kr(:)];
    HruHar_kr_true = khatrirao(Hru_true, Har_true.');
    h_true = [Hau_true(:); HruHar_kr_true(:)];
    
    nmse_Hru = norm(Hru_true - Hru,'fro')^2 / norm(Hru_true,'fro')^2;
    nmse_Har = norm(Har_true - Har,'fro')^2 / norm(Har_true,'fro')^2;
    nmse_Hau = norm(Hau_true - Hau,'fro')^2 / norm(Hau_true,'fro')^2;
    nmse_h = norm(h_true - h,'fro')^2 / norm(h_true,'fro')^2;
    
    nmse_Hru_mc(mc_run) = nmse_Hru;
    nmse_Har_mc(mc_run) = nmse_Har;
    nmse_Hau_mc(mc_run) = nmse_Hau;
    nmse_h_mc(mc_run) = nmse_h;
    % fprintf("nmse_Hru %.3e, nmse_Har %.3e, nmse_Hau %.3e\n", nmse_Hru, nmse_Har, nmse_Hau)
    
    % Example:     hur <=> Hur(:) for Hur = N by K matrix
    % vectorize:   hur = reshape(Hur, [N*K,1]), stack columns into one column
    % unvectorize: Hur = reshape(hur, [N,K]), unstack into K columns
    Hru_mc(mc_run,:) = Hru_true(:).';
    Har_mc(mc_run,:) = Har_true(:).';
    Hau_mc(mc_run,:) = Hau_true(:).';
    Hru_err_mc(mc_run,:) = Hru_err(:).';
    Har_err_mc(mc_run,:) = Har_err(:).';
    Hau_err_mc(mc_run,:) = Hau_err(:).';
    end % mc_run
    
    %% Print
    fprintf("\n------------------------------------------------------------\n")
    fprintf("10*log10(CH_err) => %.6f\n", 10*log10(CH_err));
    fprintf("Mean Sum Rate over montecarlo runs:\n");
    fprintf("Optimized RIS: %.6f +/- %.6f\n", mean(Ropt2_mc, 1), var(Ropt2_mc, 1));
    fprintf("Random RIS: %.6f +/- %.6f\n", mean(Rrand2_mc, 1), var(Rrand2_mc, 1));
    fprintf("Average Channel Error: nmse_h %.6e +/- %.6e\n", mean(nmse_h_mc), var(nmse_h_mc))
    fprintf("nmse_Hru %.6e +/- %.6e, nmse_Har %.6e +/- %.6e, nmse_Hau %.6e +/- %.6e\n", ...
        mean(nmse_Hru_mc), var(nmse_Hru_mc), mean(nmse_Har_mc), var(nmse_Har_mc), mean(nmse_Hau_mc), var(nmse_Hau_mc))
    
    fprintf("Script Execution time:\n")
    fprintElapsedTime(TSTART);
end

delete(gcp('nocreate'))
diary off
