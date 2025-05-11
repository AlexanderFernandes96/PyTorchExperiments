from copy import deepcopy
import numpy as np
import pandas
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim
from tqdm import tqdm
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import torch
# from ray import tune
# from ray.tune.search.optuna import OptunaSearch
# from ray.tune.schedulers import ASHAScheduler
import pprint
import sys
from pathlib import Path

# Disable the loading bars:
DISABLE_TQDM = False
# DISABLE_TQDM = True

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Get cpu, gpu or mps device for training.
device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {device} device", flush=True)

def load_complex(dataset_dir, variable_name_real, variable_name_imag):
    return (np.loadtxt(dataset_dir + variable_name_real + ".csv", delimiter=',') +
            1j * np.loadtxt(dataset_dir + variable_name_imag + ".csv", delimiter=','))

    # Hau = (K, M)    AP  -> UE
    # Har = (N, M)    AP  -> RIS
    # Hru = (K, N)    RIS -> UE
    # W   = (M, K)    UE stream -> AP

class EncoderLayer(nn.Module):
    def __init__(self, K_UE, M_AP, N_RIS, Nc_RIS):
        super(EncoderLayer, self).__init__()
        # Hout = floor((Hin + 2*padding[0] - dilation[0]*(kernel_size[0]-1) - 1)/stride[0] + 1)
        # Wout = floor((Win + 2*padding[1] - dilation[1]*(kernel_size[1]-1) - 1)/stride[1] + 1)
        self.layer_theta = nn.Sequential(
            # nn.Conv2d(1, 8, 3, padding=0, bias=False), # 8 = 10 + 2*0 - (3-1)
            # nn.BatchNorm2d(8),
            # nn.ReLU(),
            # nn.Conv2d(8, 16, 3, padding=0, bias=False), # 6
            # nn.BatchNorm2d(16),
            # nn.ReLU(),
            # nn.Conv2d(16, 32, 3, padding=0, bias=False), # 4
            # nn.BatchNorm2d(32),
            # nn.ReLU(),
            # nn.Conv2d(32, 64, 3, padding=0, bias=False), # 2
            # nn.BatchNorm2d(64),
            # nn.ReLU(),
            # nn.MaxPool2d(2, 2),
            nn.Linear(N_RIS, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_w_mag = nn.Sequential(
            nn.Linear(M_AP*K_UE, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_w_ang = nn.Sequential(
            nn.Linear(M_AP*K_UE, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_har_mag = nn.Sequential(
            nn.Linear(N_RIS*M_AP, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_har_ang = nn.Sequential(
            nn.Linear(N_RIS*M_AP, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_hru_mag = nn.Sequential(
            nn.Linear(N_RIS*K_UE, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_hru_ang = nn.Sequential(
            nn.Linear(N_RIS*K_UE, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_hau_mag = nn.Sequential(
            # nn.Conv2d(1, 64, 1, padding=0, bias=False),
            # nn.BatchNorm2d(64),
            # nn.ReLU(),
            nn.Linear(K_UE*M_AP, Nc_RIS),
            nn.ReLU(),
        )
        self.layer_hau_ang = nn.Sequential(
            nn.Linear(K_UE*M_AP, Nc_RIS),
            nn.ReLU(),
        )
        self.linear_encoder = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(9 * Nc_RIS, Nc_RIS),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(Nc_RIS, Nc_RIS),
            nn.ReLU(),
        )

    def forward(self, x):
        theta   = x[0].float()
        w_mag   = x[1].float()
        w_ang   = x[2].float()
        har_mag = x[3].float()
        har_ang = x[4].float()
        hru_mag = x[5].float()
        hru_ang = x[6].float()
        hau_mag = x[7].float()
        hau_ang = x[8].float()
        theta   = torch.flatten(theta, start_dim=1)
        w_mag   = torch.flatten(w_mag, start_dim=1)
        w_ang   = torch.flatten(w_ang, start_dim=1)
        har_mag = torch.flatten(har_mag, start_dim=1)
        har_ang = torch.flatten(har_ang, start_dim=1)
        hru_mag = torch.flatten(hru_mag, start_dim=1)
        hru_ang = torch.flatten(hru_ang, start_dim=1)
        hau_mag = torch.flatten(hau_mag, start_dim=1)
        hau_ang = torch.flatten(hau_ang, start_dim=1)
        theta   = self.layer_theta(theta)
        w_mag   = self.layer_w_mag(w_mag)
        w_ang   = self.layer_w_ang(w_ang)
        hra_mag = self.layer_har_mag(har_mag)
        hra_ang = self.layer_har_ang(har_ang)
        hur_mag = self.layer_hru_mag(hru_mag)
        hur_ang = self.layer_hru_ang(hru_ang)
        hua_mag = self.layer_hau_mag(hau_mag)
        hua_ang = self.layer_hau_ang(hau_ang)
        x_in = torch.cat((theta, w_mag, w_ang, hra_mag, hra_ang, hur_mag, hur_ang, hua_mag, hua_ang), 1)
        x_enc = self.linear_encoder(x_in)
        return x_enc

# class EncoderLayerOnlyChannels(nn.Module):
#     def __init__(self, N_RIS, Nc_RIS):
#         super(EncoderLayerOnlyChannels, self).__init__()
#         self.layer_hra_mag = nn.Sequential(
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#         )
#         self.layer_hra_ang = nn.Sequential(
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#         )
#         self.layer_hur_mag = nn.Sequential(
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#         )
#         self.layer_hur_ang = nn.Sequential(
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#         )
#         self.layer_hua_mag = nn.Sequential(
#             nn.Linear(1, N_RIS),
#             nn.ReLU(),
#         )
#         self.layer_hua_ang = nn.Sequential(
#             nn.Linear(1, N_RIS),
#             nn.ReLU(),
#         )
#         # self.linear_mag = nn.Sequential(
#         #     nn.Dropout(0.2),
#         #     nn.Linear(3*64, 64),
#         #     nn.ReLU(),
#         #     nn.Dropout(0.2),
#         #     nn.Linear(64, 64),
#         #     nn.ReLU(),
#         # )
#         # self.linear_ang = nn.Sequential(
#         #     nn.Dropout(0.2),
#         #     nn.Linear(3*64, 64),
#         #     nn.ReLU(),
#         #     nn.Dropout(0.2),
#         #     nn.Linear(64, 64),
#         #     nn.ReLU(),
#         # )
#         self.linear_encoder = nn.Sequential(
#             nn.Dropout(0.2),
#             nn.Linear(6*N_RIS, N_RIS),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(N_RIS, Nc_RIS),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(Nc_RIS, Nc_RIS),
#             nn.ReLU(),
#         )
#     def forward(self, x):
#         # hra_mag = torch.reshape(x[1], (-1, 1, sysmodelparams["Nw"], sysmodelparams["Nh"])).float()
#         # hra_ang = torch.reshape(x[2], (-1, 1, sysmodelparams["Nw"], sysmodelparams["Nh"])).float()
#         # hur_mag = torch.reshape(x[3], (-1, 1, sysmodelparams["Nw"], sysmodelparams["Nh"])).float()
#         # hur_ang = torch.reshape(x[4], (-1, 1, sysmodelparams["Nw"], sysmodelparams["Nh"])).float()
#         # hua_mag = torch.reshape(x[5], (-1, 1, 1, 1)).float()
#         # hua_ang = torch.reshape(x[6], (-1, 1, 1, 1)).float()
#         # hra_mag = torch.flatten(self.layer_hra_mag(hra_mag), start_dim=1)
#         # hra_ang = torch.flatten(self.layer_hra_ang(hra_ang), start_dim=1)
#         # hur_mag = torch.flatten(self.layer_hur_mag(hur_mag), start_dim=1)
#         # hur_ang = torch.flatten(self.layer_hur_ang(hur_ang), start_dim=1)
#         # hua_mag = torch.flatten(self.layer_hua_mag(hua_mag), start_dim=1)
#         # hua_ang = torch.flatten(self.layer_hua_ang(hua_ang), start_dim=1)
#         # x_mag = self.linear_mag(torch.cat((hra_mag, hur_mag, hua_mag), 1))
#         # x_ang = self.linear_ang(torch.cat((hra_ang, hur_ang, hua_ang), 1))
#         # x_in = torch.cat((x_mag, x_ang), 1)
#         hra_mag = x[1].float()
#         hra_ang = x[2].float()
#         hur_mag = x[3].float()
#         hur_ang = x[4].float()
#         hua_mag = torch.reshape(x[5], (-1, 1)).float()
#         hua_ang = torch.reshape(x[6], (-1, 1)).float()
#         hra_mag = self.layer_hra_mag(hra_mag)
#         hra_ang = self.layer_hra_ang(hra_ang)
#         hur_mag = self.layer_hur_mag(hur_mag)
#         hur_ang = self.layer_hur_ang(hur_ang)
#         hua_mag = self.layer_hua_mag(hua_mag)
#         hua_ang = self.layer_hua_ang(hua_ang)
#         x_in = torch.cat((hra_mag, hra_ang, hur_mag, hur_ang, hua_mag, hua_ang), 1)
#         x_enc = self.linear_encoder(x_in)
#         return x_enc

# class EncoderLayerOnlyTheta(nn.Module):
#     def __init__(self, N_RIS, Nc_RIS):
#         super(EncoderLayerOnlyTheta, self).__init__()
#         self.layer_theta = nn.Sequential(
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#         )
#         self.linear_encoder = nn.Sequential(
#             nn.Dropout(0.2),
#             nn.Linear(N_RIS, N_RIS),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(N_RIS, Nc_RIS),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(Nc_RIS, Nc_RIS),
#             nn.ReLU(),
#         )
#     def forward(self, x):
#         # theta = torch.reshape(x[0], (-1, 1, sysmodelparams["Nw"], sysmodelparams["Nh"])).float()
#         theta   = x[0].float()
#         x_in  = torch.flatten(self.layer_theta(theta), start_dim=1)
#         x_enc = self.linear_encoder(x_in)
#         return x_enc

class QuantizerLayer(nn.Module):
    def __init__(self, C_code_words, dev):
        super(QuantizerLayer, self).__init__()
        # a = amplitude, b = shift, c = slope
        # for i = 0 to C_code_words-1:
        #   z += a[i] * tanh( c[i] * (theta_n - b[i]) )
        # where theta_n is a scalar value: [-pi, +pi) and z is the quantized theta_n
        self.a = torch.nn.Parameter(
            data=torch.from_numpy(
                np.ones(C_code_words-1) * np.pi / ( C_code_words-1 )
            ), requires_grad=False)
        spacing = np.linspace(-1, 1, C_code_words + 1) * np.pi
        self.b = torch.nn.Parameter(
            data=torch.from_numpy(
                np.delete(spacing,[0,-1])
                # np.random.rand(C_code_words - 1, 1) * 2 * np.pi - 3 * np.pi),
            ), requires_grad=True)
        c_slope = 0.5
        if len(self.b) > 1:
            self.c = torch.nn.Parameter(
                # data=torch.from_numpy((15 / np.mean(np.diff(self.b.data.numpy()))) * np.ones(C_code_words - 1)),
                data=torch.from_numpy((c_slope * 2 * np.pi / np.mean(np.diff(self.b.data.numpy())) ) * np.ones(C_code_words - 1)),
                # data=torch.from_numpy(0.9 * np.ones(C_code_words - 1)),
                requires_grad=True)
        else:
            self.b = torch.nn.Parameter(data=torch.from_numpy(np.zeros(C_code_words - 1)), requires_grad=True)
            self.c = torch.nn.Parameter(
                data=torch.from_numpy(c_slope * np.ones(C_code_words - 1)),
                # data=torch.from_numpy(15 / np.pi * np.ones(C_code_words - 1)),
                requires_grad=True)
        self.C_code_words = C_code_words
        self.hardQ = False
        self.device = dev

    def forward(self, theta_enc):
        # theta_enc = matrix (number of samples of train/test dataset, Nc_RIS), in the range: [-pi, +pi)
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1], device=self.device)
        for i in range(self.C_code_words - 1):
            if self.hardQ:
                theta_qnt += self.a[i] * torch.sign(self.c[i] * (theta_enc - self.b[i]))
            else:
                theta_qnt += self.a[i] * torch.tanh(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

    def plot_vals(self):
        a = np.array(self.a.cpu().detach().numpy())
        b = np.array(self.b.cpu().detach().numpy())
        c = np.array(self.c.cpu().detach().numpy())
        print(a,b,c, flush=True)
        if len(b) > 1:
            bdiff = np.max(np.diff(b))
            x_vals = np.linspace(np.min(b) - bdiff, np.max(b) + bdiff, 10000)
        else:
            x_vals = np.linspace(np.min(b) - np.pi, np.max(b) + np.pi, 10000)
        soft_quant = []
        hard_quant = []
        for x_val in x_vals:
            soft_quant.append(np.sum(a * np.tanh(c * (x_val - b))))
            hard_quant.append(np.sum(a * np.sign(c * (x_val - b))))
        return x_vals, soft_quant, hard_quant

class DecoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS):
        super(DecoderLayer, self).__init__()
        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS, Nc_RIS),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(Nc_RIS, N_RIS),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(N_RIS, N_RIS),
            nn.ReLU(),
            # nn.Dropout(0.2),
            # nn.Linear(128, 128),
            # nn.LeakyReLU(),
            # nn.Tanh(),
        )
        self.out_layer = nn.Sequential(
            nn.Linear(N_RIS, N_RIS),
            # nn.LeakyReLU(),
            # nn.Tanh(), # Note Tanh at output makes training harder considering the optimal value is periodic wrt 2pi
        )

        # self.cnn_layer = nn.Sequential(
        #     nn.Upsample(scale_factor=2),
        #     # nn.ConvTranspose2d(64, 64, 3, padding=1),
        #     # nn.ReLU(),
        #     # nn.BatchNorm2d(64),
        #     # nn.ConvTranspose2d(128, 128, 3, padding=1),
        #     # nn.ReLU(),
        #     # nn.BatchNorm2d(128),
        #     # nn.ConvTranspose2d(128, 128, 3, padding=1),
        #     # nn.ReLU(),
        #     # nn.BatchNorm2d(128),
        #     nn.ConvTranspose2d(128, 64, 3, padding=0),
        #     nn.ReLU(),
        #     nn.BatchNorm2d(64),
        #     nn.ConvTranspose2d(64, 32, 5, padding=0),
        #     nn.ReLU(),
        #     nn.BatchNorm2d(32),
        #     nn.ConvTranspose2d(32, 1, 5, padding=1),
        #     nn.ReLU(),
        #     nn.BatchNorm2d(1),
        # )
        # self.reshape_dim = (128, 1, 1)

        # self.cnn_layer = nn.Sequential(
        #     nn.Conv2d(5, 28, 3, stride=1, padding=0, padding_mode='circular'),
        #     nn.BatchNorm2d(28),
        #     nn.LeakyReLU(),
        #     nn.Conv2d(28, 32, 3, stride=1, padding=0, padding_mode='circular'),
        #     nn.BatchNorm2d(32),
        #     nn.LeakyReLU(),
        #     nn.MaxPool2d(4, 4),
        # )

        # self.out_layer = nn.Sequential(
        #     nn.Linear(100, N_RIS),
        #     # nn.LeakyReLU(),
        #     nn.Tanh(),
        # )

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        # theta_cnn = self.cnn_layer(theta_dec.view(theta_dec.size(0), *self.reshape_dim))
        # theta_cnn = torch.flatten(theta_cnn, start_dim=1)
        theta_out = self.out_layer(theta_dec)
        return theta_out
        # return torch.angle(torch.exp(1j * theta_out))

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, K_UE, M_AP, N_RIS, Nc_RIS, C_code_words, dev):
        super(AutoQEncoder, self).__init__()
        self.encoder_layer = EncoderLayer(K_UE, M_AP, N_RIS, Nc_RIS).to(dev)
        self.quantizer_layer = QuantizerLayer(C_code_words, dev).to(dev)
        self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS).to(dev)
    def forward(self, x):
        x_enc = self.encoder_layer(x)
        x_qnt = self.quantizer_layer(x_enc)
        x_dec = self.decoder_layer(x_qnt)
        return x_dec.double()

# class AutoQEncoderOnlyChannels(nn.Module):
#     def __init__(self, N_RIS, Nc_RIS, C_code_words, dev):
#         super(AutoQEncoderOnlyChannels, self).__init__()
#         self.encoder_layer = EncoderLayerOnlyChannels(N_RIS, Nc_RIS).to(dev)
#         self.quantizer_layer = QuantizerLayer(C_code_words, dev).to(dev)
#         self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS).to(dev)
#     def forward(self, x):
#         x_enc = self.encoder_layer(x)
#         x_qnt = self.quantizer_layer(x_enc)
#         x_dec = self.decoder_layer(x_qnt)
#         return x_dec.double()
#
# class AutoQEncoderOnlyTheta(nn.Module):
#     def __init__(self, N_RIS, Nc_RIS, C_code_words, dev):
#         super(AutoQEncoderOnlyTheta, self).__init__()
#         self.encoder_layer = EncoderLayerOnlyTheta(N_RIS, Nc_RIS).to(dev)
#         self.quantizer_layer = QuantizerLayer(C_code_words, dev).to(dev)
#         self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS).to(dev)
#     def forward(self, x):
#         x_enc = self.encoder_layer(x)
#         x_qnt = self.quantizer_layer(x_enc)
#         x_dec = self.decoder_layer(x_qnt)
#         return x_dec.double()

class LinearQuantizer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS, C_code_words, dev):
        super(LinearQuantizer, self).__init__()
        self.encoder_layer = nn.Linear(N_RIS, Nc_RIS).to(dev)
        self.quantizer_layer = QuantizerLayer(C_code_words, dev).to(dev)
        self.decoder_layer = nn.Linear(Nc_RIS, N_RIS).to(dev)
        # self.encoder_layer = nn.Identity(N_RIS, Nc_RIS).to(dev)
        # self.quantizer_layer = QuantizerLayer(C_code_words).to(dev)
        # self.decoder_layer = nn.Identity(Nc_RIS, N_RIS).to(dev)
    def forward(self, x):
        # theta = torch.flatten(x[:,0,:,:], start_dim=1) # get only the theta values
        # theta = x[:,0,:] # get only the theta values
        theta = x[0] # get only the theta values
        theta_enc = self.encoder_layer(theta.float())
        theta_qnt = self.quantizer_layer(theta_enc)
        theta_dec = self.decoder_layer(theta_qnt)
        return theta_dec.double()

class LoadData(Dataset):
    def __init__(self, data):
        super(LoadData, self).__init__()
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# https://stackoverflow.com/questions/55894693/understanding-pytorch-einsum
# https://rockt.ai/2018/04/30/einsum
# Hau = (K, M)    AP  -> UE
# Har = (N, M)    AP  -> RIS
# Hru = (K, N)    RIS -> UE
# W   = (M, K)    UE stream -> AP
def batchSumRate(theta, Wopt, Hau, Har, Hru):
    n = torch.pow(10*torch.ones(theta.shape[0], device=device), -trainparams['snr_dB']/10)
    R = torch.zeros((theta.shape[0], trainparams['K_UE']), device=device)
    for k in range(trainparams['K_UE']):
        hruHar = torch.einsum("bn, bnm -> bnm", Hru[:,k,:], Har)
        hk = Hau[:, k, :] + torch.einsum("bn, bnm -> bm", torch.exp(1j*theta), hruHar)
        S = torch.pow(torch.norm(torch.einsum("bm, bm -> b", hk, Wopt[:, :, k])), 2)
        N = torch.zeros(theta.shape[0], device=device)
        for l in range(trainparams['K_UE']):
            if l != k:
                N += torch.pow(torch.norm(torch.einsum("bm, bm -> b", hk, Wopt[:, :, l])), 2)
        N += n
        R[:,k] = torch.log2(torch.ones(theta.shape[0], device=device) + torch.div(S, N))
    return torch.einsum("bk -> b", R)

def Loss(theta, Wopt, Hau, Har, Hru):
    return -torch.mean(batchSumRate(theta, Wopt, Hau, Har, Hru))

class Trainer(object):
    def __init__(self, train_loader, trainparams, model, dev):
        self.train_loader = train_loader
        self.N_RIS = trainparams['N_RIS']
        self.Nc_RIS = int(self.N_RIS * trainparams['Nc_RIS_compressed_ratio'])
        self.C_code_words = trainparams['C_code_words']
        self.device = dev
        self.model = model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=trainparams['lr'], amsgrad=True)
        # self.optimizer = optim.AdamW(self.model.parameters(), lr=trainparams['lr'], amsgrad=True)
        # self.optimizer = optim.SGD(self.model.parameters(), lr=trainparams['lr'], momentum=trainparams['momentum'])
        # self.scheduler = torch.optim.lr_scheduler.OneCycleLR(self.optimizer, max_lr=trainparams['max_lr'], steps_per_epoch=len(train_loader),
        #                                                      epochs=trainparams['epochs'])
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, 'min', patience=int(trainparams['epoch_val']/4))

    def train(self, val_loader, trainparams):

        val_loss_min = np.inf
        val_loss_min_earlystop = np.inf

        model_validated = deepcopy(self.model)  # if val loss does not decrease, return the copy of AQEnet before training
        train_losses = []
        val_losses = []
        num_epochs = 0
        running_loss = 0.0
        for epoch in tqdm(range(trainparams['epochs']), disable=DISABLE_TQDM):
            train_loss = 0.0
            val_loss = 0.0

            # Train the model
            self.model.train()
            with torch.enable_grad():
                try:
                    self.model.quantizer_layer.hardQ = False
                except AttributeError:
                    self.model.module.quantizer_layer.hardQ = False
                for i, data in (enumerate(self.train_loader)):
                    inputs, theta_opt, Wopt, Hau, Har, Hru = data
                    self.optimizer.zero_grad()                              # clear gradients of all variables to optimize
                    outputs = self.model(inputs)                           # forward pass inputs into network
                    loss = Loss(outputs, Wopt, Hau, Har, Hru)   # calculate batch loss
                    loss.backward()                                         # back propagate gradients through AQE network
                    self.optimizer.step()                                   # single optimization step to update variables
                    # self.scheduler.step()                                   # One Cycle LR adjust learning rate each step
                    train_loss += loss.item() * trainparams['batch_size']   # update training loss
                    train_loss /= len(self.train_loader.dataset)            # normalize training loss


            # Validate the model
            self.model.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                try:
                    self.model.quantizer_layer.hardQ = False
                except AttributeError:
                    self.model.module.quantizer_layer.hardQ = False

                for i, data in (enumerate(val_loader)):
                    inputs, theta_opt, Wopt, Hau, Har, Hru = data
                    outputs = self.model(inputs)                       # forward pass inputs into AQE network
                    loss = Loss(outputs, Wopt, Hau, Har, Hru)   # calculate batch loss
                    val_loss += loss.item() * trainparams['batch_size']  # update validation loss
                    val_loss /= len(val_loader.dataset)                 # normalize validation loss

                before_lr = self.optimizer.param_groups[0]['lr']
                self.scheduler.step(val_loss)                                   # decay learning rate
                after_lr = self.optimizer.param_groups[0]['lr']
                print(before_lr, '->', after_lr, flush=True)

                if trainparams['epoch_echo']:
                    print('Epoch: {} \tTraining Loss: {:.10f} \tValidation Loss: {:.10f}'.format(
                        epoch, train_loss, val_loss), flush=True)

                # save model if validation loss has decreased
                if val_loss <= val_loss_min:
                    if trainparams['epoch_echo']:
                        print('Validation loss same/decreased ({:.10f} --> {:.10f})... saving model.'.format(
                            val_loss_min, val_loss), flush=True)
                    val_loss_min = val_loss
                    model_validated = deepcopy(self.model) # if val loss does not decrease, return the copy of AQEnet before training
                # else:
                #     self.model = AQEnet_not_trained
                running_loss += val_loss
                if epoch % trainparams['epoch_val'] == trainparams['epoch_val']-1:
                    if running_loss < val_loss_min_earlystop:
                        if trainparams['epoch_echo']:
                            print('Validation early stop running loss decreased ({:.10f} --> {:.10f}).'.format(
                                val_loss_min_earlystop, running_loss), flush=True)
                        val_loss_min_earlystop = running_loss
                    else:
                        if trainparams['epoch_echo']:
                            print('No Validation early stop loss decrease ({:.10f} --> {:.10f}). Early Stopping'.format(
                            val_loss_min_earlystop, running_loss), flush=True)
                        break
                    running_loss = 0.0

                train_losses.append(train_loss)
                val_losses.append(val_loss)
            num_epochs += 1
        self.model = model_validated
        return self.model, train_losses, val_losses, num_epochs

    def evaluate(self, test_loader, trainparams):
        N_RIS = trainparams['N_RIS']
        R_opt = torch.zeros(1).to(self.device)
        R = torch.zeros(1).to(self.device)
        R_rand = torch.zeros(1).to(self.device)
        test_size = len(test_loader.dataset.data)
        self.model.eval()
        with torch.no_grad():
            # replace trainable tanh quantization layer with proper quantization layer
            try:
                self.model.quantizer_layer.hardQ = False
            except AttributeError:
                self.model.module.quantizer_layer.hardQ = False

            for i, data in tqdm(enumerate(test_loader), disable=DISABLE_TQDM):
                inputs, theta_opt, Wopt, Hau, Har, Hru = data
                batchsize = theta_opt.shape[0]
                theta_model = self.model(inputs)  # forward pass inputs into AQE network
                theta_rand = torch.rand(size=(batchsize,N_RIS), dtype=torch.double, device=self.device) * 2*torch.pi - torch.pi

                R_opt  += torch.sum(batchSumRate(theta_opt, Wopt, Hau, Har, Hru))
                R      += torch.sum(batchSumRate(theta_model, Wopt, Hau, Har, Hru))
                R_rand += torch.sum(batchSumRate(theta_rand, Wopt, Hau, Har, Hru))

        # Achievable Rate
        R_opt  = R_opt / test_size
        R      = R / test_size
        R_rand = R_rand / test_size
        R = torch.nan_to_num(R, nan=trainparams['snr_dB'])
        return R_opt.item(), R.item(), R_rand.item()


if __name__ == "__main__":
    print('------------')
    print('Start Script')
    print('------------')

    # path_dir = "/home/alex96/scratch/"
    path_dir = "MATLAB/"
    dataset_dir = path_dir + "datasets/HDRISData/13/"
    results_dir = path_dir + "logs/MU-MISO_AchievableRateExperiments/00/"
    if len(sys.argv) > 1:
        results_dir = results_dir + sys.argv[1] + "/"
    results_file = "results.csv"
    trainparams_file = "trainparams.csv"

    print("make directory:", results_dir)
    Path(path_dir).mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # Make print statements go to file instead of stdout:
    if path_dir == "/home/alex96/scratch/":
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        f_python_output = open(results_dir + "python_log.out", 'w')
        sys.stdout = f_python_output
        sys.stderr = f_python_output

    ####################################################################################################################
    # Training trainparams
    ####################################################################################################################
    trainparams = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'lr': 10**(-1*np.random.uniform(2, 5)), # optimizer learning rate
                  # 'momentum': 0.9, # optimizer momentum for SGD
                  'batch_size': 2**np.random.randint(6, 11), # batch training size
                  'epochs': 100,  # total training duration
                  'epoch_val': 100, # validate early stop every epoch number
                  'epoch_echo': True, # flag to display epoch print losses
                  # 'step_size': 10, # step size for scheduler optimizer
                  # 'Nc_RIS': 100, # number of quantizers, values that N is compressed/encoded into
                  'Q_bits': 1, # number of bits of a quantizer
                  # 'max_lr': 1, # maximum learning rate for Scheduler
                  }
    # for all numpy random generators, the range is: [low, high) where the low value is included but the high value is excluded.


    # print('Using OneCycleLR Scheduler, with SGD.')
    print('Using ADAM with learning rate decay')

    Nc_array = 2**np.array(range(3,7))
    # Nc_array = [32]

    num_dirs = 25 # number of directories to use which includes data samples

    ####################################################################################################################
    # Load RIS data from .csv files
    ####################################################################################################################
    print('---------')
    print('Load Data')
    print('---------')
    trainparams['mc_runs'] = 0

    for d in range(num_dirs):
        sysmodelparams = pd.read_csv(dataset_dir + "/" + str(d) + "/" + "systemModelParameters.csv").iloc[0]
        trainparams['mc_runs'] += int(sysmodelparams['mc_runs'])
        trainparams['N_RIS'] = int(sysmodelparams['N'])
        trainparams['Nw_RIS'] = int(sysmodelparams['Nw'])
        trainparams['Nh_RIS'] = int(sysmodelparams['Nh'])
        trainparams['M_AP'] = int(sysmodelparams['M'])
        trainparams['K_UE'] = int(sysmodelparams['K'])
        trainparams['snr_dB'] = int(sysmodelparams['SNRdB'])

    print("Training Model parameters:", flush=True)
    pprint.pprint(trainparams)

    # Hau = (K, M)    AP  -> UE
    # Har = (N, M)    AP  -> RIS
    # Hru = (K, N)    RIS -> UE
    # W   = (M, K)    UE stream -> AP
    Hau = torch.zeros(trainparams['mc_runs'], trainparams['K_UE']*trainparams['M_AP'], dtype=torch.cdouble)
    Har = torch.zeros(trainparams['mc_runs'], trainparams['N_RIS']*trainparams['M_AP'], dtype=torch.cdouble)
    Hru = torch.zeros(trainparams['mc_runs'], trainparams['K_UE']*trainparams['N_RIS'], dtype=torch.cdouble)
    RISopt = torch.zeros(trainparams['mc_runs'], trainparams['N_RIS'], dtype=torch.double)
    Wopt = torch.zeros(trainparams['mc_runs'], trainparams['M_AP']*trainparams['K_UE'], dtype=torch.cdouble)

    for d in range(num_dirs):
        print(dataset_dir + str(d) + "/")
        sp = pd.read_csv(dataset_dir + str(d) + "/" + "systemModelParameters.csv").iloc[0]
        print('Loading... (Hau)')
        Hau_ = load_complex(dataset_dir + str(d) + "/", "Hau_r", "Hau_i")
        Hau[d*int(sp['mc_runs']):(d+1)*int(sp['mc_runs']), :] = torch.from_numpy(Hau_)
        print('Loading... (Har)')
        Har_ = load_complex(dataset_dir + str(d) + "/", "Har_r", "Har_i")
        Har[d*int(sp['mc_runs']):(d+1)*int(sp['mc_runs']), :] = torch.from_numpy(Har_)
        print('Loading... (Hru)')
        Hru_ = load_complex(dataset_dir + str(d) + "/", "Hru_r", "Hru_i")
        Hru[d*int(sp['mc_runs']):(d+1)*int(sp['mc_runs']), :] = torch.from_numpy(Hru_)
        print('Loading... RISopt.csv')
        RISopt_ = np.loadtxt(dataset_dir + str(d) + "/" + "RISopt.csv", delimiter=',')
        RISopt[d*int(sp['mc_runs']):(d+1)*int(sp['mc_runs']), :] = torch.from_numpy(RISopt_)
        print('Loading... (wopt)')
        wopt_ = load_complex(dataset_dir + str(d) + "/", "wopt_r", "wopt_i")
        Wopt[d*int(sp['mc_runs']):(d+1)*int(sp['mc_runs']), :] = torch.from_numpy(wopt_)

    # unvectorize by reshaping the stacked vector into Matrix along proper dimensions
    Hau = torch.transpose(torch.reshape(Hau, (trainparams['mc_runs'], trainparams['M_AP'], trainparams['K_UE'])), 1, 2).to(device)
    Har = torch.transpose(torch.reshape(Har, (trainparams['mc_runs'], trainparams['M_AP'], trainparams['N_RIS'])), 1, 2).to(device)
    Hru = torch.transpose(torch.reshape(Hru, (trainparams['mc_runs'], trainparams['N_RIS'], trainparams['K_UE'])), 1, 2).to(device)
    RISopt = RISopt.to(device)
    Wopt = torch.transpose(torch.reshape(Wopt, (trainparams['mc_runs'], trainparams['K_UE'], trainparams['M_AP'])), 1, 2).to(device)

    ################################################################################################################
    # Create the Torch Dataset
    ################################################################################################################
    print('--------------')
    print('Create Dataset')
    print('--------------')
    num_train_val = int(trainparams['train_test_split'] * trainparams['mc_runs'])
    num_test = trainparams['mc_runs'] - num_train_val
    num_train = int(trainparams['train_val_split'] * num_train_val)
    num_val = num_train_val - num_train
    train_set = [] # [[inputs0, labels0], [inputs1, labels1], ... ]
    test_set = []
    val_set = []
    for i in tqdm(range(0, trainparams['mc_runs']), disable=DISABLE_TQDM):
        input = [RISopt[i],
                 torch.abs(Wopt[i,:,:]), torch.angle(Wopt[i,:,:]),
                 torch.abs(Har[i,:,:]), torch.angle(Har[i,:,:]),
                 torch.abs(Hru[i,:,:]), torch.angle(Hru[i,:,:]),
                 torch.abs(Hau[i,:,:]), torch.angle(Hau[i,:,:])]
        data = [input, RISopt[i], Wopt[i,:,:], Hau[i,:,:], Har[i,:,:], Hru[i,:,:]]
        if i < num_train:
            train_set.append(data)
        elif i >= num_train_val:
            test_set.append(data)
        else:
            val_set.append(data)
    train_set = LoadData(train_set)
    test_set = LoadData(test_set)
    val_set = LoadData(val_set)

    ################################################################################################################
    # Train & Test model with specific hyperparameters
    ################################################################################################################
    print('------------')
    print('Train & Test')
    print('------------')
    R_opt_array = np.zeros(len(Nc_array))
    R_AQE_array = np.zeros(len(Nc_array))
    # R_AQEC_array = np.zeros(len(Nc_array))
    # R_AQET_array = np.zeros(len(Nc_array))
    R_linQ_array = np.zeros(len(Nc_array))
    R_rand_array = np.zeros(len(Nc_array))
    trainparamslist = []
    for i in range(len(Nc_array)):
        trainparams['Nc_RIS'] = Nc_array[i]
        bits = trainparams['Q_bits'] # bits per Quantizer
        trainparams['C_code_words'] = 2**bits
        trainparams['Nc_RIS_compressed_ratio'] = trainparams['Nc_RIS'] / trainparams['N_RIS']
        trainparams['overall_bits'] = trainparams['Nc_RIS'] * bits
        train_loader = DataLoader(train_set, batch_size=trainparams['batch_size'])
        test_loader = DataLoader(test_set, batch_size=trainparams['batch_size'])
        val_loader = DataLoader(val_set, batch_size=trainparams['batch_size'])

        AQEnet = AutoQEncoder(trainparams['K_UE'], trainparams['M_AP'], trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], device)
        # AQECnet = AutoQEncoderOnlyChannels(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], device)
        # AQETnet = AutoQEncoderOnlyTheta(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], device)
        linQ = LinearQuantizer(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['C_code_words'], device)

        AQEtrainer = Trainer(train_loader, trainparams, AQEnet, device)
        total_params = sum(p.numel() for p in AQEtrainer.model.parameters())
        print('AQE Number of parameters:', total_params, flush=True)
        print(AQEtrainer.model, flush=True)

        # AQECtrainer = Trainer(train_loader, trainparams, AQECnet, device)
        # total_params = sum(p.numel() for p in AQECtrainer.model.parameters())
        # print('AQEC Number of parameters:', total_params, flush=True)
        # print(AQECtrainer.model, flush=True)

        # AQETtrainer = Trainer(train_loader, trainparams, AQETnet, device)
        # total_params = sum(p.numel() for p in AQETtrainer.model.parameters())
        # print('AQET Number of parameters:', total_params, flush=True)
        # print(AQETtrainer.model, flush=True)

        linQtrainer = Trainer(train_loader, trainparams, linQ, device)
        total_params = sum(p.numel() for p in linQtrainer.model.parameters())
        print('linQ Number of parameters:', total_params, flush=True)
        print(linQtrainer.model, flush=True)

        AQEnet,     AQEnet_train_losses,    AQEnet_val_losses,  AQEnet_num_epochs   = AQEtrainer.train(val_loader, trainparams)
        # AQECnet,    AQECnet_train_losses,   AQECnet_val_losses, AQECnet_num_epochs  = AQECtrainer.train(val_loader, trainparams)
        # AQETnet,    AQETnet_train_losses,   AQETnet_val_losses, AQETnet_num_epochs  = AQETtrainer.train(val_loader, trainparams)
        linQ,       linQ_train_losses,      linQ_val_losses,    linQ_num_epochs     = linQtrainer.train(val_loader, trainparams)

        d_AQE = {"train": AQEnet_train_losses, "val": AQEnet_val_losses}
        AQE_loss_df = pandas.DataFrame(d_AQE)
        # d_AQEC = {"train": AQECnet_train_losses, "val": AQECnet_val_losses}
        # AQEC_loss_df = pandas.DataFrame(d_AQEC)
        # d_AQET = {"train": AQETnet_train_losses, "val": AQETnet_val_losses}
        # AQET_loss_df = pandas.DataFrame(d_AQET)
        d_linQ = {"train": linQ_train_losses, "val": linQ_val_losses}
        linQ_loss_df = pandas.DataFrame(d_linQ)

        loss_file = "loss" + str(i) + ".csv"
        print("Saving losses to:", results_dir + "AQE_" + loss_file, flush=True)
        AQE_loss_df.to_csv(results_dir + "AQE_" + loss_file, sep='\t', encoding='utf-8', index=False, header=True)
        # print("Saving losses to:", results_dir + "AQEC_" + loss_file, flush=True)
        # AQEC_loss_df.to_csv(results_dir + "AQEC_" + loss_file, sep='\t', encoding='utf-8', index=False, header=True)
        # print("Saving losses to:", results_dir + "AQET_" + loss_file, flush=True)
        # AQET_loss_df.to_csv(results_dir + "AQET_" + loss_file, sep='\t', encoding='utf-8', index=False, header=True)
        print("Saving losses to:", results_dir + "linQ_" + loss_file, flush=True)
        linQ_loss_df.to_csv(results_dir + "linQ_" + loss_file, sep='\t', encoding='utf-8', index=False, header=True)

        R_opt, R_AQE, R_rand = AQEtrainer.evaluate(test_loader, trainparams)
        # R_opt, R_AQEC, R_rand = AQECtrainer.evaluate(test_loader, trainparams)
        # R_opt, R_AQET, R_rand = AQETtrainer.evaluate(test_loader, trainparams)
        R_opt, R_linQ, R_rand = linQtrainer.evaluate(test_loader, trainparams)

        print("-------------------------------------------------------------------------------------------------------")
        print("Training Model parameters:", flush=True)
        pprint.pprint(trainparams)
        print('Achievable Rate (bps/Hz) using RIS phase shifts with Transmit power SNR {:.0f} dB:'.format(trainparams['snr_dB']), flush=True)
        print('optimum: ', R_opt, flush=True)
        print('AQE net: ', R_AQE, flush=True)
        # print('AQEC:    ', R_AQEC, flush=True)
        # print('AQET:    ', R_AQET, flush=True)
        print('lin Q:   ', R_linQ, flush=True)
        print('random:  ', R_rand, flush=True)
        print("-------------------------------------------------------------------------------------------------------\n\n")
        R_opt_array[i] = R_opt
        R_AQE_array[i] = R_AQE
        # R_AQEC_array[i] = R_AQEC
        # R_AQET_array[i] = R_AQET
        R_linQ_array[i] = R_linQ
        R_rand_array[i] = R_rand

        # x_vals, soft_quant, hard_quant = linQ.quantizer_layer.plot_vals()
        # fig, ax = plt.subplots()
        # ax.plot(x_vals, soft_quant, label='Soft Quantizer')
        # ax.plot(x_vals, hard_quant, label='Hard Quantizer', linestyle='--')
        # ax.set_title("Quantizer Values: bits = " + str(bits))
        # ax.legend()
        # plt.show(block=True)
        # # plt.interactive(False)

        trainparamslist.append(deepcopy(trainparams))

    trainparams_df = pandas.DataFrame(trainparamslist)
    print(trainparams_df, flush=True)
    print('Saving parameters to:', results_dir + trainparams_file)
    trainparams_df.to_csv(results_dir + trainparams_file, sep='\t', encoding='utf-8', index=False, header=True)

    d = {'Nc': Nc_array,
         'R_opt': R_opt_array,
         'R_AQE': R_AQE_array,
         # 'R_AQEC': R_AQEC_array,
         # 'R_AQET': R_AQET_array,
         'R_linQ': R_linQ_array,
         'R_rand': R_rand_array}
    results_df = pandas.DataFrame(d)
    print('Bits per Quantizer:', trainparams['Q_bits'], flush=True)
    print(results_df, flush=True)
    print('Saving results to:', results_dir + results_file, flush=True)
    results_df.to_csv(results_dir + results_file, sep='\t', encoding='utf-8', index=False, header=True)

    # fig, ax = plt.subplots()
    # ax.plot(Nc_array, R_opt_array, label='P_opt')
    # ax.plot(Nc_array, R_AQE_array, label='P_AQE')
    # ax.plot(Nc_array, R_linQ_array, label='P_linQ')
    # ax.plot(Nc_array, R_rand_array, label='P_rand')
    # ax.set_xlabel('Nc')
    # ax.set_ylabel('Receive Power (dB)')
    # ax.set_xscale('log', base=2)
    # ax.legend()
    # plt.show(block=True)
    # # plt.interactive(False)


    ################################################################################################################
    # END PYTHON SCRIPT
    ################################################################################################################
    print('----------')
    print('End Script')
    print('----------')

    if path_dir == "/home/alex96/scratch/":
        sys.stdout = orig_stdout
        f_python_output.close()
        sys.stderr = orig_stderr