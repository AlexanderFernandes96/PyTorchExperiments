% This script shows the RIS channels graphically
% clear all; close all; delete(gcp('nocreate')); clc; 
TSTART = tic;
addpath("src\")
%% Load system model / script parameters
dataDir = "datasets/HDRISData/05/";
fileName = dataDir + "HDRISData.mat";
load(fileName)

for mc = 1:50

    Hur = reshape(Hur_mc(mc,:), [N,K]);
    Hra = reshape(Hra_mc(mc,:), [M,N]);
    Hua = reshape(Hua_mc(mc,:), [M,K]);
    theta = zeros(1,N);
    
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

        
    end
    imsize = 2000;
    figure(1)
    imshow(mat2gray(reshape(theta, [Nw, Nh])), 'InitialMagnification', imsize)
    title(['theta - RIS opt, mc = ', num2str(mc)])
    F = fft2(reshape(theta, [Nw, Nh]));
    F = abs(fftshift(F));
    % F = log(F+1);
    figure(2)
    imshow(mat2gray(F), 'InitialMagnification', imsize)
    title(['theta 2D FFT - RIS opt, mc = ', num2str(mc)])
    figure(3)
    imshow(mat2gray(reshape(abs(Hur), [Nw, Nh])), 'InitialMagnification', imsize)
    title(['Hur mag, mc = ', num2str(mc)])
    figure(4)
    imshow(mat2gray(reshape(angle(Hur), [Nw, Nh])), 'InitialMagnification', imsize)
    title(['Hur phase, mc = ', num2str(mc)])
    figure(5)
    imshow(mat2gray(reshape(abs(Hra), [Nw, Nh])), 'InitialMagnification', imsize)
    title(['Hra mag, mc = ', num2str(mc)])
    figure(6)
    imshow(mat2gray(reshape(angle(Hra), [Nw, Nh])), 'InitialMagnification', imsize)
    title(['Hra phase, mc = ', num2str(mc)])
    pause(1)
end