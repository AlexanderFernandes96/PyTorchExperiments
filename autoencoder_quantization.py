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

# path_dir = "/home/alex96/scratch/"
path_dir = "MATLAB/"

Path(path_dir).mkdir(parents=True, exist_ok=True)
results_dir = path_dir + "logs/SISO_AchievableRateExperiments/00/"
Path(results_dir).mkdir(parents=True, exist_ok=True)

# Make print statements go to file instead of stdout:
if path_dir == "/home/alex96/scratch/":
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    f_python_output = open(results_dir + "python_log.out", 'w')
    sys.stdout = f_python_output
    sys.stderr = f_python_output


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

class EncoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS):
        super(EncoderLayer, self).__init__()

        # N = 100
        self.reshape_dim = (5,10,10)
        self.cnn_layer1 = nn.Sequential(
            nn.Conv2d(5, 32, 5, padding=1, padding_mode='circular'),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, 5, stride=1, padding=0, padding_mode='zeros'),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=1, padding=0, padding_mode='zeros'),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            # nn.Conv2d(128, 128, 3, stride=1, padding=0, padding_mode='zeros'),
            # nn.BatchNorm2d(128),
            # nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.cnn_layer2 = nn.Sequential(
            nn.Conv2d(5, 32, 8, padding=2, padding_mode='circular'),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=1, padding=0, padding_mode='zeros'),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=1, padding=0, padding_mode='zeros'),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.linear_encoder = nn.Sequential(
            nn.Dropout(0.7),
            # nn.Linear(128, 128),
            # nn.LeakyReLU(),
            nn.Linear(128, N_RIS),
            nn.LeakyReLU(),
            nn.Linear(N_RIS, N_RIS),
            nn.LeakyReLU(),
            nn.Linear(N_RIS, Nc_RIS),
            nn.LeakyReLU(),
        )

        # # N = 64
        # self.reshape_dim = (5,8,8)
        # self.cnn_layer = nn.Sequential(
        #     nn.Conv2d(5, 28, 3, stride=1, padding=0, padding_mode='circular'),
        #     nn.BatchNorm2d(28),
        #     nn.LeakyReLU(),
        #     nn.Conv2d(28, 32, 3, stride=1, padding=1, padding_mode='zeros'),
        #     nn.BatchNorm2d(32),
        #     nn.LeakyReLU(),
        #     nn.Conv2d(32, 64, 3, stride=1, padding=1, padding_mode='zeros'),
        #     nn.BatchNorm2d(64),
        #     nn.LeakyReLU(),
        #     # nn.Conv2d(64, 64, 3, stride=1, padding=1, padding_mode='zeros'),
        #     # nn.BatchNorm2d(64),
        #     # nn.LeakyReLU(),
        #     nn.MaxPool2d(4, 4),
        # )
        #
        # self.linear_encoder = nn.Sequential(
        #     # nn.Dropout(0.5),
        #     nn.Linear(64, 64),
        #     nn.LeakyReLU(),
        #     nn.Linear(64, 64),
        #     nn.LeakyReLU(),
        #     nn.Linear(64, N_RIS),
        #     nn.LeakyReLU(),
        #     nn.Linear(N_RIS, Nc_RIS),
        #     nn.LeakyReLU(),
        # )


        # # N = 25
        # self.reshape_dim = (5,5,5)
        # self.cnn_layer = nn.Sequential(
        #     nn.Conv2d(5, 64, 3, padding=1, padding_mode='circular'),
        #     nn.BatchNorm2d(64),
        #     nn.LeakyReLU(),
        #     nn.MaxPool2d(4, 4),
        # )

        # self.residual_layer1 = nn.Sequential(
        #     nn.Conv2d(32, 32, 3, padding=2, padding_mode='zeros'),
        #     nn.BatchNorm2d(32),
        #     nn.SELU(),
        #     nn.Conv2d(32, 32, 3, padding=2, padding_mode='zeros'),
        #     nn.BatchNorm2d(32),
        #     nn.SELU(),
        #     nn.MaxPool2d(4, 4),
        # )

        # self.linear_encoder = nn.Sequential(
        #     nn.Dropout(0.5),
        #     nn.Linear(64, Nc_RIS),
        #     nn.LeakyReLU(),
        # )

    def forward(self, x):
        x_cnn1 = self.cnn_layer1(x.view(x.size(0), *self.reshape_dim))
        x_cnn2 = self.cnn_layer2(x.view(x.size(0), *self.reshape_dim))
        x_flat = torch.flatten(x_cnn1 + x_cnn2, start_dim=1)
        x_enc = self.linear_encoder(x_flat)
        return x_enc

    #     self.linear_encoder = nn.Sequential(
    #         nn.Linear(N_RIS, int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
    #         nn.LeakyReLU(),
    #         nn.Linear(int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
    #         nn.LeakyReLU(),
    #         nn.Linear(int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
    #         nn.LeakyReLU(),
    #         nn.Linear(int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
    #         nn.LeakyReLU(),
    #         nn.Linear(int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
    #         nn.LeakyReLU(),
    #         nn.Linear(int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS), Nc_RIS)
    #     )
    #
    # def forward(self, theta):
    #     theta_flat = torch.flatten(theta, start_dim=1)
    #     theta_enc = self.linear_encoder(theta_flat)
    #     return theta_enc


class QuantizerLayer(nn.Module):
    def __init__(self, C_code_words):
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

    def forward(self, theta_enc):
        # theta_enc = matrix (number of samples of train/test dataset, Nc_RIS), in the range: [-pi, +pi)
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).to(device)
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
    def __init__(self, N_RIS, Nc_RIS, Nw_RIS, Nh_RIS):
        super(DecoderLayer, self).__init__()
        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS, N_RIS),
            nn.LeakyReLU(),
            nn.Linear(N_RIS, N_RIS),
            nn.LeakyReLU(),
            nn.Linear(N_RIS, 128),
            nn.LeakyReLU(),
            # nn.Linear(128, 128),
            # nn.LeakyReLU(),
            # nn.Tanh(),
        )
        self.cnn_layer = nn.Sequential(
            nn.Upsample(scale_factor=2),
            # nn.ConvTranspose2d(64, 64, 3, padding=1),
            # nn.ReLU(),
            # nn.BatchNorm2d(64),
            # nn.ConvTranspose2d(128, 128, 3, padding=1),
            # nn.ReLU(),
            # nn.BatchNorm2d(128),
            # nn.ConvTranspose2d(128, 128, 3, padding=1),
            # nn.ReLU(),
            # nn.BatchNorm2d(128),
            nn.ConvTranspose2d(128, 64, 3, padding=0),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.ConvTranspose2d(64, 32, 5, padding=0),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.ConvTranspose2d(32, 1, 5, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(1),
        )
        self.reshape_dim = (128, 1, 1)

        # self.cnn_layer = nn.Sequential(
        #     nn.Conv2d(5, 28, 3, stride=1, padding=0, padding_mode='circular'),
        #     nn.BatchNorm2d(28),
        #     nn.LeakyReLU(),
        #     nn.Conv2d(28, 32, 3, stride=1, padding=0, padding_mode='circular'),
        #     nn.BatchNorm2d(32),
        #     nn.LeakyReLU(),
        #     nn.MaxPool2d(4, 4),
        # )

        self.out_layer = nn.Sequential(
            nn.Linear(100, N_RIS),
            # nn.LeakyReLU(),
            nn.Tanh(),
        )

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        theta_cnn = self.cnn_layer(theta_dec.view(theta_dec.size(0), *self.reshape_dim))
        theta_cnn = torch.flatten(theta_cnn, start_dim=1)
        theta_out = self.out_layer(theta_cnn)
        return theta_out
        # return torch.angle(torch.exp(1j * theta_out))

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, N_RIS, Nc_RIS, Nw_RIS, Nh_RIS, C_code_words):
        super(AutoQEncoder, self).__init__()
        self.encoder_layer = EncoderLayer(N_RIS, Nc_RIS).to(device)
        self.quantizer_layer = QuantizerLayer(C_code_words).to(device)
        self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS, Nw_RIS, Nh_RIS).to(device)

    def forward(self, theta):
        theta_enc = self.encoder_layer(theta.float())
        theta_qnt = self.quantizer_layer(theta_enc)
        theta_dec = self.decoder_layer(theta_qnt)
        return theta_dec.double()

class LinearQuantizer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS, C_code_words):
        super(LinearQuantizer, self).__init__()
        self.encoder_layer = nn.Linear(N_RIS, Nc_RIS).to(device)
        self.quantizer_layer = QuantizerLayer(C_code_words).to(device)
        self.decoder_layer = nn.Linear(Nc_RIS, N_RIS).to(device)
        # self.encoder_layer = nn.Identity(N_RIS, Nc_RIS).to(device)
        # self.quantizer_layer = QuantizerLayer(C_code_words).to(device)
        # self.decoder_layer = nn.Identity(Nc_RIS, N_RIS).to(device)

    def forward(self, theta):
        # theta = torch.flatten(theta[:,0,:,:], start_dim=1) # get only the theta values
        theta = theta[:,0,:] # get only the theta values
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

def Loss1(x, y, hra, hur):
    dist = torch.zeros(x.shape[0]).to(device)
    for n in range(x.shape[1]):
        # dist += torch.square(torch.abs(hra[:,n]*hur[:,n])) * torch.square(torch.abs(torch.exp(1j*x[:,n]) - torch.exp(1j*y[:,n])))
        dist += torch.square(torch.abs(hra[:,n] * (torch.exp(1j*x[:,n]) - torch.exp(1j*y[:,n])) * hur[:,n]))
    return torch.mean(dist)

def Loss2(x, y):
    dist = torch.abs(torch.exp(1j*x) - torch.exp(1j*y))
    return torch.mean(torch.square(dist))

def Loss3(x, y):
    dist = torch.abs(x - y)
    return torch.mean(torch.square(dist))

def Loss4(x, y, hra, hur):
    diff = torch.exp(1j*x) - torch.exp(1j*y)
    mul = hra * diff * hur
    dist = torch.sum(torch.square(torch.abs(mul)), 1)
    return torch.mean(dist)

def Loss5(x, y, hra, hur, hua):
    hra_hur = torch.mul(hra, hur)
    # x_rec = torch.square(torch.abs(hua + torch.matmul(hra_hur, torch.exp(1j*x.transpose(0,1)))))
    # y_rec = torch.square(torch.abs(hua + torch.matmul(hra_hur, torch.exp(1j*y.transpose(0,1)))))
    # return -torch.mean(torch.log2(1 + x_rec))
    x = torch.exp(1j*x)
    # R = torch.zeros(x.size(0)).to(device)
    # for b in range(x.size(0)):
    #     R[b] = torch.dot(hra_hur[b], x[b])
    R = torch.matmul(hra_hur, x.transpose(0,1))
    R = torch.log2( 1 + torch.square(torch.abs(hua + R )) )
    dist = torch.abs(torch.angle(torch.exp(1j * x)) - torch.angle(torch.exp(1j * y)))
    return torch.mean(torch.square(dist)) - torch.mean(R)

class Trainer(object):
    def __init__(self, train_loader, trainparams, model):
        self.train_loader = train_loader
        self.N_RIS = trainparams['N_RIS']
        self.Nc_RIS = int(self.N_RIS * trainparams['Nc_RIS_compressed_ratio'])
        self.C_code_words = trainparams['C_code_words']
        # print('N RIS elements:', self.N_RIS, flush=True)
        # print('Nc RIS compressed:', self.Nc_RIS, flush=True)
        # print('C quantization code words:', self.C_code_words, flush=True)
        # overall_bits = self.Nc_RIS * int(round(np.log2(self.C_code_words)))
        # print('overall bits per transmission:', overall_bits, flush=True)
        self.model = model.to(device)
        # self.optimizer = optim.Adam(self.model.parameters(), lr=trainparams['lr'], amsgrad=True)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=trainparams['lr'], amsgrad=True)
        # self.optimizer = optim.SGD(self.model.parameters(), lr=trainparams['lr'], momentum=trainparams['momentum'])
        # self.scheduler = torch.optim.lr_scheduler.OneCycleLR(self.optimizer, max_lr=0.01, steps_per_epoch=len(train_loader),
        #                                                      pct_start=0.1, epochs=trainparams['epochs']*trainparams['grace_period'])
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, 'min', patience=int(trainparams['epoch_val']/2))

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
                self.model.quantizer_layer.hardQ = False
                for i, data in (enumerate(self.train_loader)):
                    inputs, labels, hua, hra, hur = data
                    hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    self.optimizer.zero_grad()                              # clear gradients of all variables to optimize
                    outputs = self.model(inputs)                           # forward pass inputs into AQE network
                    # loss = Loss1(outputs, labels, hra, hur)                 # calculate batch loss
                    # loss = Loss3(outputs, labels)                           # calculate batch loss
                    # loss = Loss4(outputs, labels, hra, hur)                 # calculate batch loss
                    loss = Loss5(outputs, labels, hra, hur, hua)                 # calculate batch loss
                    loss.backward()                                         # back propagate gradients through AQE network
                    self.optimizer.step()                                   # single optimization step to update variables
                    # self.scheduler.step()                                   # adjust learning rate each step
                    train_loss += loss.item() * trainparams['batch_size']   # update training loss
                    train_loss /= len(self.train_loader.dataset)            # normalize training loss


            # Validate the model
            self.model.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                self.model.quantizer_layer.hardQ = True

                for i, data in (enumerate(val_loader)):
                    inputs, labels, hua, hra, hur = data
                    hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = self.model(inputs)                       # forward pass inputs into AQE network
                    # loss = Loss1(outputs, labels, hra, hur)             # calculate batch loss
                    # loss = Loss3(outputs, labels)                       # calculate batch loss
                    # loss = Loss4(outputs, labels, hra, hur)             # calculate batch loss
                    loss = Loss5(outputs, labels, hra, hur, hua)             # calculate batch loss
                    val_loss += loss.item() * trainparams['batch_size']  # update validation loss
                    val_loss /= len(val_loader.dataset)                 # normalize validation loss

                before_lr = self.optimizer.param_groups[0]['lr']
                self.scheduler.step(val_loss)                                   # adjust learning rate each step
                after_lr = self.optimizer.param_groups[0]['lr']
                print('\n', before_lr, '->', after_lr, flush=True)

                if trainparams['epoch_echo']:
                    print('\nEpoch: {} \tTraining Loss: {:.10f} \tValidation Loss: {:.10f}'.format(
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

    def evaluate(self, test_loader, sysmodelparams, trainparams):
        N_RIS = trainparams['N_RIS']
        self.model.eval()
        with torch.no_grad():
            # replace trainable tanh quantization layer with proper quantization layer
            self.model.quantizer_layer.hardQ = True

            test_size = len(test_loader.dataset.data)
            # y_opt = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            # y = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            # y_rand = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            R_opt = torch.zeros(test_size).to(device)
            R = torch.zeros(test_size).to(device)
            R_rand = torch.zeros(test_size).to(device)
            test_i = 0
            for i, data in (enumerate(test_loader)):
                inputs, theta_opt, hua, hra, hur = data
                inputs = inputs.to(device)
                theta_opt = theta_opt.to(device)
                hua = hua.to(device)
                hra = hra.to(device)
                hur = hur.to(device)
                len_hua = len(hua)
                theta_model = self.model(inputs)  # forward pass inputs into AQE network
                theta_rand = torch.rand(size=(len_hua,N_RIS), dtype=torch.double) * 2*torch.pi - torch.pi
                theta_rand = theta_rand.to(device)
                x = torch.pow(10*torch.ones(1), trainparams['snr_dB']/10)
                x = x.to(device)
                hra_hur = torch.mul(hra, hur)
                # Transmit data with RIS phases
                if sysmodelparams['K'] == 1 & sysmodelparams['M'] == 1: # SISO
                    for b in range(len_hua):

                        # # Power
                        # awgn = torch.view_as_complex(torch.randn(1,2)).to(device)
                        # y_opt[test_i]  = (hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_opt[b])))  * x + awgn
                        # y[test_i]      = (hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_model[b])))  * x + awgn
                        # y_rand[test_i] = (hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_rand[b]))) * x + awgn

                        # Achievable Rate
                        R_opt[test_i]  = torch.log2( 1 + torch.square(torch.abs(hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_opt[b])))) * x )
                        R[test_i]      = torch.log2( 1 + torch.square(torch.abs(hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_model[b])))) * x )
                        R_rand[test_i] = torch.log2( 1 + torch.square(torch.abs(hua[b] + torch.dot(hra_hur[b], torch.exp(1j*theta_rand[b])))) * x )
                        test_i += 1

        # Power
        # P_opt = 10*torch.log10(torch.abs(torch.dot(y_opt, torch.conj(y_opt))) / test_size)
        # P = 10*torch.log10(torch.abs(torch.dot(y_AQE, torch.conj(y_AQE))) / test_size)
        # P_rand = 10*torch.log10(torch.abs(torch.dot(y_rand, torch.conj(y_rand))) / test_size)
        # P_AQE = torch.nan_to_num(P_AQE, nan=trainparams['snr_dB'])
        # return P_opt.item(), P.item(), P_rand.item()

        # Achievable Rate
        R_opt = torch.mean(R_opt)
        R = torch.mean(R)
        R_rand = torch.mean(R_rand)
        R = torch.nan_to_num(R, nan=trainparams['snr_dB'])
        return R_opt.item(), R.item(), R_rand.item()



if __name__ == "__main__":
    print('------------')
    print('Start Script')
    print('------------')
    ####################################################################################################################
    # Training trainparams
    ####################################################################################################################
    trainparams = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'lr': 0.0001, # optimizer learning rate
                  'momentum': 0.9, # optimizer momentum for SGD
                  'batch_size': 512, # batch training size
                  'epochs': 500,  # total training duration
                  'snr_dB': -5, # transmit power to receive noise power
                  'epoch_val': 100, # validate early stop every epoch number
                  'epoch_echo': True, # flag to display epoch print losses
                  # 'trials': 500, # number of Ray tune trials
                  # 'training_iterations': 50, # number of Ray tune training iterations
                  # 'grace_period': 20, # min number of training iterations
                  # 'trials_per_device': 5, # number of trials per cpu/gpu resource
                  'step_size': 10, # step size for scheduler optimizer
                  'Nc_RIS': 100, # number of quantizers, values that N is compressed/encoded into
                  'Q_bits': 3, # number of bits of a quantizer
                  }

    # search_space = { # Ray Tune Hyper parameter search space
    #     "lr": tune.loguniform(1e-5, 1e-1),
    #     "momentum": tune.uniform(0.1, 0.99),
    #     "batch_size": tune.choice([16, 32, 64, 128, 256, 512]),
    #     # "Nc_RIS": tune.randint(5, 100),
    #     # "step_size": tune.randint(5, 50),
    #     # 'Q_bits': tune.choice([1, 2, 3, 4, 5, 6]),
    # }

    Nc_array = 2**np.array(range(7,8))

    # Nc_array = [32]


    # dataset_dir = "MATLAB/datasets/HDRISData/03/" N = 100, K = 1, M = 1
    # | total bits | Optimum |     AQE |  Random | Epochs |   config/lr |   config/momentum |   config/batch_size |
    # |         16 | 35.1036 | 20.0867 | 16.2269 |   1030 | 1.00502e-06 |         0.154168  |                   8 |


    ####################################################################################################################
    # Load RIS data from .csv files
    ####################################################################################################################
    print('---------')
    print('Load Data')
    print('---------')
    # dataset_dir = path_dir + "datasets/HDRISData/08/"
    dataset_dir = path_dir + "datasets/HDRISData/03/"
    results_file = "results.csv"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')
    sysmodelparams = pd.read_csv(dataset_dir + "systemModelParameters.csv").iloc[0]
    trainparams['mc_runs'] = RISopt.shape[0]
    trainparams['N_RIS'] = RISopt.shape[1]
    trainparams['Nw_RIS'] = sysmodelparams['Nw']
    trainparams['Nh_RIS'] = sysmodelparams['Nh']

    print('System Model parameters:', sysmodelparams, sep='\n', flush=True)

    print("Training Model parameters:", flush=True)
    pprint.pprint(trainparams)

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
    train_set = [] # [[sample0, label0], [sample0, label0], ... ]
    test_set = []
    val_set = []
    for i in range(0, trainparams['mc_runs']):
        theta = RISopt[i]
        # thetaIn = np.reshape(theta, (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        # ft = np.fft.ifftshift(thetaIn)
        # ft = np.fft.fft2(ft)
        # thetaInfft = np.fft.fftshift(ft)
        # HraIn = np.reshape(Hra[i], (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        # HurIn = np.reshape(Hur[i], (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        # input = np.array([thetaIn, np.abs(thetaInfft), np.angle(thetaInfft), np.abs(HraIn), np.angle(HraIn), np.abs(HurIn), np.angle(HurIn)])
        # input = np.array([thetaIn, np.real(HraIn), np.imag(HraIn), np.real(HurIn), np.imag(HurIn)])
        input = np.array([theta, np.real(Hra[i]), np.imag(Hra[i]), np.real(Hur[i]), np.imag(Hur[i])])
        if i < num_train:
            train_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
        elif i >= num_train_val:
            test_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
        else:
            val_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
    train_set = LoadData(train_set)
    test_set = LoadData(test_set)
    val_set = LoadData(val_set)

    ################################################################################################################
    # Train & Test model with specific hyperparameters
    ################################################################################################################
    print('------------')
    print('Train & Test')
    print('------------')

    # bits_array = np.array([1, 2, 3, 4])
    R_opt_array = np.zeros(len(Nc_array))
    R_AQE_array = np.zeros(len(Nc_array))
    R_linQ_array = np.zeros(len(Nc_array))
    R_rand_array = np.zeros(len(Nc_array))
    for i in range(len(Nc_array)):
        trainparams['Nc_RIS'] = Nc_array[i]
        bits = trainparams['Q_bits'] # bits per Quantizer
        trainparams['C_code_words'] = 2**bits
        trainparams['Nc_RIS_compressed_ratio'] = trainparams['Nc_RIS'] / trainparams['N_RIS']
        trainparams['overall_bits'] = trainparams['Nc_RIS'] * bits
        train_loader = DataLoader(train_set, batch_size=trainparams['batch_size'])
        test_loader = DataLoader(test_set, batch_size=trainparams['batch_size'])
        val_loader = DataLoader(val_set, batch_size=trainparams['batch_size'])
        AQEnet = AutoQEncoder(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], trainparams['Nh_RIS'], trainparams['C_code_words'])
        linQ = LinearQuantizer(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['C_code_words'])
        AQEtrainer = Trainer(train_loader, trainparams, AQEnet)
        linQtrainer = Trainer(train_loader, trainparams, linQ)
        print(AQEtrainer.model, flush=True)
        total_params = sum(p.numel() for p in AQEtrainer.model.parameters())
        print('Number of parameters:', total_params, flush=True)
        print(linQtrainer.model, flush=True)
        total_params = sum(p.numel() for p in linQtrainer.model.parameters())
        print('Number of parameters:', total_params, flush=True)
        AQEnet, AQEnet_train_losses, AQEnet_val_losses, num_epochs = AQEtrainer.train(val_loader, trainparams)
        linQ, AQEnet_train_losses, AQEnet_val_losses, num_epochs = linQtrainer.train(val_loader, trainparams)
        print(AQEnet, flush=True)
        total_params = sum(p.numel() for p in AQEnet.parameters())
        print('Number of parameters:', total_params, flush=True)


        R_opt, R_AQE, R_rand = AQEtrainer.evaluate(test_loader, sysmodelparams, trainparams)
        R_opt, R_linQ, R_rand = linQtrainer.evaluate(test_loader, sysmodelparams, trainparams)


        print("Training Model parameters:", flush=True)
        pprint.pprint(trainparams)
        print('Achievable Rate (bps/Hz) using RIS phase shifts with Transmit power SNR {:.0f} dB:'.format(trainparams['snr_dB']), flush=True)
        print('optimum: ', R_opt, flush=True)
        print('AQE net: ', R_AQE, flush=True)
        print('lin Q:   ', R_linQ, flush=True)
        print('random:  ', R_rand, flush=True)
        R_opt_array[i] = R_opt
        R_AQE_array[i] = R_AQE
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

    d = {'Nc': Nc_array, 'R_opt': R_opt_array, 'R_AQE': R_AQE_array, 'R_linQ': R_linQ_array, 'R_rand': R_rand_array}
    results_df = pandas.DataFrame(d)
    print('Total bits:', trainparams['overall_bits'], flush=True)
    print(results_df, flush=True)
    print('Saving to:', results_dir + results_file, flush=True)

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


    # ################################################################################################################
    # # Ray Tune: Hyperparameter Tuning
    # ################################################################################################################
    #
    # def objective(config):
    #     trainparams['lr'] = config['lr']
    #     trainparams['momentum'] = config['momentum']
    #     trainparams['batch_size'] = config['batch_size']
    #     # trainparams['Nc_RIS'] = config['Nc_RIS']
    #     # trainparams['step_size'] = config['step_size']
    #     # trainparams['Q_bits'] = config['Q_bits']
    #
    #     bits = trainparams['Q_bits']  # bits per Quantizer
    #     trainparams['C_code_words'] = 2 ** bits
    #     trainparams['Nc_RIS_compressed_ratio'] = trainparams['Nc_RIS'] / trainparams['N_RIS']
    #     overall_bits = trainparams['Nc_RIS'] * bits
    #     trainparams['overall_bits'] = overall_bits
    #
    #     train_loader = DataLoader(train_set, batch_size=int(config["batch_size"]))
    #     test_loader = DataLoader(test_set, batch_size=int(config["batch_size"]))
    #     val_loader = DataLoader(val_set, batch_size=int(config["batch_size"]))
    #     AQEnet = AutoQEncoder(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], trainparams['Nh_RIS'], trainparams['C_code_words'])
    #     linQ = LinearQuantizer(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['C_code_words'])
    #     AQEtrainer = Trainer(train_loader, trainparams, AQEnet)
    #     linQtrainer = Trainer(train_loader, trainparams, linQ)
    #     total_epochs = 0
    #     while True:
    #         AQEnet, train_losses, val_losses, num_epochs = AQEtrainer.train(val_loader, trainparams)  # Train the model
    #         P_opt, P_AQE, P_rand = AQEtrainer.evaluate(test_loader, sysmodelparams, trainparams)  # Compute test results
    #         linQ, train_losses, val_losses, num_epochs = linQtrainer.train(val_loader, trainparams)  # Train the model
    #         P_opt, P_linQ, P_rand = linQtrainer.evaluate(test_loader, sysmodelparams, trainparams)  # Compute test results
    #         total_epochs += num_epochs
    #         tune.report({"Optimum": P_opt, "AQE": P_AQE, "Lin Q": P_linQ, "Random": P_rand, "Epochs": total_epochs, "Total bits": overall_bits})  # Report to Tune
    #
    # algo = OptunaSearch()
    # scheduler = ASHAScheduler(
    #     max_t= trainparams['training_iterations'],
    #     grace_period=trainparams['grace_period'],
    # )
    # tuner = tune.Tuner(
    #     tune.with_resources(
    #     objective,
    #     resources={"cpu": 24/trainparams['trials_per_device'], "gpu": 1/trainparams['trials_per_device']}
    #         # fraction means trials per device: fraction = device/trial,
    #         # My setup: CPU has 24 cores, 1 GPU
    # ),
    #     tune_config=tune.TuneConfig(
    #         metric="AQE",
    #         mode="max",
    #         search_alg=algo,
    #         scheduler=scheduler,
    #         num_samples=trainparams['trials']
    #     ),
    #     run_config=tune.RunConfig(
    #         stop={"training_iteration": trainparams['training_iterations']},
    #     ),
    #     param_space=search_space,
    # )
    # results = tuner.fit()
    # results_df = results.get_dataframe().sort_values('AQE',ascending=False)
    # best_result = results.get_best_result("AQE", "max")
    #
    # print('System Model parameters:', sysmodelparams, sep='\n', flush=True)
    # print("Training Model parameters:", flush=True)
    # pprint.pprint(trainparams)
    #
    # print("Best trial config: {}".format(best_result.config), flush=True)
    # print("Best trial final Rx Power: {}".format(
    #     best_result.metrics["AQE"]), flush=True)
    # print(tabulate(results_df, headers='keys', tablefmt='psql'), flush=True)

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