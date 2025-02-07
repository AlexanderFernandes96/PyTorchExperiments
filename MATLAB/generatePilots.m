% This program must be run by an external script initializing all variables

PxA = 10^(SNRdB/10); % Transmission Power
PxU = PxA;

if strcmp(pilot_scheme{1}(1:2), 'HD')
    Q_M = dftmtx(M)/sqrt(M);
    Q_K = dftmtx(K)/sqrt(K);
    SA = [Q_M, zeros(M,K)];
    SU = [zeros(K,M), Q_K];
    if M > K
        ExA = 2*PxA;
        ExU = 2*PxU*(M/K);
    elseif M < K
        ExA = 2*PxA*(K/M);
        ExU = 2*PxU;
    else
        ExA = 2*PxA;
        ExU = 2*PxU;
    end

elseif strcmp(pilot_scheme{1}(1:2), 'FD')
    Q_M = dftmtx(M)/sqrt(M);
    Q_K = dftmtx(K)/sqrt(K);
    if M > K
        SA = [Q_M, Q_M];
        q = floor(M/K); r = mod(M,K);
        Q_r = dftmtx(r)/sqrt(r);
        R = [Q_r;zeros(K-r,r)];
    %     R = zeros(K,r);
        P = [repmat(Q_K,[1,q]), R];
        SU = [P, -P];
    elseif M < K
        SU = [Q_K, Q_K];
        q = floor(K/M); r = mod(K,M);
        Q_r = dftmtx(r)/sqrt(r);
        R = [Q_r;zeros(K-r,r)];
    %     R = zeros(M,r);
        P = [repmat(Q_M,[1,q]), R];
        SA = [P, -P];
    else
        SA = [Q_M, Q_M];
        SU = [Q_K, -Q_K];
    end
    ExA = PxA;
    ExU = PxU;
end

% E refers to the energy over the full duration of pilot transmission is the same for AP and UE
% P refers to the transmit power of a single pilot transmission is the same for AP and UE
if strcmp(pilot_scheme{1}(3), 'E')
    Xa = sqrt(ExA)*SA;
    Xu = sqrt(ExU)*SU;
elseif strcmp(pilot_scheme{1}(3), 'P')
    Xa = sqrt(PxA)*SA;
    Xu = sqrt(PxU)*SU;
else
    error("Specify Pilot Scheme with 'E'nergy or 'P'ower constraint.")
end

[~,L] = size(Xa);
T = B*L; % training overhead

XA = repmat(Xa, [1,B]);
XU = repmat(Xu, [1,B]);

X = [Xa; Xu];
Xpinv = pinv(X);

