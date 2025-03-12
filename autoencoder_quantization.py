from copy import deepcopy
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim
from tqdm import tqdm
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import torch
from ray import tune
from ray.tune.search.optuna import OptunaSearch
from ray.tune.schedulers import ASHAScheduler
import pprint

# DISABLE_TQDM = False
DISABLE_TQDM = True

# Get cpu, gpu or mps device for training.
device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {device} device")

def load_complex(dataset_dir, variable_name_real, variable_name_imag):
    return (np.loadtxt(dataset_dir + variable_name_real + ".csv", delimiter=',') +
            1j * np.loadtxt(dataset_dir + variable_name_imag + ".csv", delimiter=','))

class EncoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS):
        super(EncoderLayer, self).__init__()
        self.cnn_layer = nn.Sequential(
            nn.Conv2d(5, N_RIS,8, padding=5, padding_mode='circular'),
            nn.BatchNorm2d(N_RIS),
            nn.SELU(),
            nn.Conv2d(N_RIS, 2*N_RIS,5, padding=2, padding_mode='zeros'),
            nn.BatchNorm2d(2*N_RIS),
            nn.SELU(),
            nn.Conv2d(2*N_RIS, 3*N_RIS,5, padding=2, padding_mode='zeros'),
            nn.BatchNorm2d(3*N_RIS),
            nn.SELU(),
            nn.Conv2d(3*N_RIS, 4*N_RIS,5, padding=2, padding_mode='zeros'),
            nn.BatchNorm2d(4*N_RIS),
            nn.SELU(),
            nn.Conv2d(4*N_RIS, 5*N_RIS,5),
            nn.BatchNorm2d(5*N_RIS),
            nn.SELU(),
            nn.Conv2d(5*N_RIS, 5*N_RIS,2),
            nn.BatchNorm2d(5*N_RIS),
            nn.SELU(),
            nn.MaxPool2d(5,5),
        )


        self.drop_layer = nn.Sequential(
            nn.Linear(5*N_RIS, 5*N_RIS),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(5*N_RIS, 5*N_RIS),
            nn.ReLU(),
        )

        self.linear_encoder = nn.Sequential(
            nn.Linear(5*N_RIS, int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS), Nc_RIS)
        )

    def forward(self, x):
        x_cnn = self.cnn_layer(x)
        x_flat = torch.flatten(x_cnn, start_dim=1)
        x_drop = (self.drop_layer(x_flat))
        x_skip = x_drop + torch.flatten(x, start_dim=1) # addition is a skip connection
        x_enc = self.linear_encoder(x_skip)
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
                np.ones(C_code_words-1)
            ), requires_grad=False)
        spacing = np.linspace(-1, 1, C_code_words + 1) * np.pi
        self.b = torch.nn.Parameter(
            data=torch.from_numpy(
                np.delete(spacing,[0,-1])
                # np.random.rand(C_code_words - 1, 1) * 2 * np.pi - 3 * np.pi),
            ), requires_grad=True)
        if len(self.b) > 1:
            self.c = torch.nn.Parameter(
                # data=torch.from_numpy((15 / np.mean(np.diff(self.b.data.numpy()))) * np.ones(C_code_words - 1)),
                data=torch.from_numpy((0.9 * 2 * np.pi / np.mean(np.diff(self.b.data.numpy())) ) * np.ones(C_code_words - 1)),
                # data=torch.from_numpy(0.9 * np.ones(C_code_words - 1)),
            requires_grad = True)
        else:
            self.b = torch.nn.Parameter(data=torch.from_numpy(np.zeros(C_code_words - 1)), requires_grad=True)
            self.c = torch.nn.Parameter(
                data=torch.from_numpy(0.9 * np.ones(C_code_words - 1)),
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
        print(a,b,c)
        if len(b) > 1:
            bdiff = np.max(np.diff(b))
            x_vals = np.linspace(np.min(b) - bdiff, np.max(b) + bdiff, 1000)
        else:
            x_vals = np.linspace(np.min(b) - np.pi, np.max(b) + np.pi, 1000)
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
            nn.Linear(Nc_RIS, int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(1*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(2*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(3*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(4*(N_RIS - Nc_RIS)/6 + Nc_RIS), int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS)),
            nn.LeakyReLU(),
            nn.Linear(int(5*(N_RIS - Nc_RIS)/6 + Nc_RIS), N_RIS),
            nn.LeakyReLU(),
        )
        self.cnn_layer = nn.Sequential(
            # nn.Unflatten(1, unflattened_size=torch.Size([N_RIS, Nw_RIS, Nh_RIS])),
            nn.ConvTranspose2d(1, 1, 5, padding=2),
            nn.ReLU(),
        )
        self.out_layer = nn.Sequential(
            nn.Linear(N_RIS, N_RIS),
            nn.Tanh(),
        )
        self.reshape_dim = (1, Nw_RIS, Nh_RIS)

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        theta_cnn = self.cnn_layer(theta_dec.view(theta_dec.size(0), *self.reshape_dim))
        theta_out = self.out_layer(torch.flatten(theta_cnn, start_dim=1) + theta_dec) # skip connection over cnn
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
        # if self.quantizer_layer.hardQ: # Quantization forward
        #     theta_qnt = self.quantizer_layer(theta_enc)
        # else: # During Training add a residual skip over the Quantization layer
        #     theta_qnt = self.quantizer_layer(theta_enc) + theta_enc
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
        dist += torch.square(torch.abs(hra[:,n]*hur[:,n])) * torch.square(torch.abs(torch.exp(1j*x[:,n]) - torch.exp(1j*y[:,n])))
        # dist += torch.square(hra[:,n]*hur[:,n] * (torch.exp(1j*x[:,n]) - torch.exp(1j*y[:,n])))
    return torch.abs(torch.mean(dist))

def Loss2(x, y):
    dist = torch.abs(torch.exp(1j*x) - torch.exp(1j*y))
    return torch.mean(torch.square(dist))

def Loss3(x, y):
    dist = torch.abs(x - y)
    return torch.mean(torch.square(dist))

def Loss4(x, y, hra, hur):
    hra_hur = torch.mul(hra, hur)
    dist = torch.abs(torch.matmul(hra_hur.transpose(0,1), torch.exp(1j*x) - torch.exp(1j*y)))
    return torch.mean(dist)

class Trainer(object):
    def __init__(self, train_loader, trainparams):
        self.train_loader = train_loader
        self.N_RIS = trainparams['N_RIS']
        self.Nc_RIS = int(self.N_RIS * trainparams['Nc_RIS_compressed_ratio'])
        self.C_code_words = trainparams['C_code_words']
        # print('N RIS elements:', self.N_RIS)
        # print('Nc RIS compressed:', self.Nc_RIS)
        # print('C quantization code words:', self.C_code_words)
        # overall_bits = self.Nc_RIS * int(round(np.log2(self.C_code_words)))
        # print('overall bits per transmission:', overall_bits)
        self.AQEnet = AutoQEncoder(self.N_RIS, self.Nc_RIS, trainparams['Nw_RIS'], trainparams['Nh_RIS'], self.C_code_words).to(device)
        # self.optimizer = optim.Adam(self.AQEnet.parameters(), lr=trainparams['lr'], amsgrad=True)
        self.optimizer = optim.SGD(self.AQEnet.parameters(), lr=trainparams['lr'], momentum=trainparams['momentum'])
        self.scheduler = torch.optim.lr_scheduler.OneCycleLR(self.optimizer, max_lr=1e-1, steps_per_epoch=len(train_loader), epochs=trainparams['epochs']*trainparams['training_iterations'])

    def train(self, val_loader, trainparams):

        val_loss_min = np.Inf
        val_loss_min_earlystop = np.Inf

        AQEnet_validated = deepcopy(self.AQEnet)  # if val loss does not decrease, return the copy of AQEnet before training
        train_losses = []
        val_losses = []
        num_epochs = 0
        for epoch in tqdm(range(trainparams['epochs']), disable=DISABLE_TQDM):
            train_loss = 0.0
            val_loss = 0.0

            # Train the model
            self.AQEnet.train()
            with torch.enable_grad():
                self.AQEnet.quantizer_layer.hardQ = False
                for i, data in (enumerate(self.train_loader)):
                    inputs, labels, hua, hra, hur = data
                    # hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    self.optimizer.zero_grad()                              # clear gradients of all variables to optimize
                    outputs = self.AQEnet(inputs)                           # forward pass inputs into AQE network
                    # loss = Loss1(outputs, labels, hra, hur)                 # calculate batch loss
                    # loss = Loss3(outputs, labels)                           # calculate batch loss
                    loss = Loss4(outputs, labels, hra, hur)                 # calculate batch loss
                    loss.backward()                                         # back propagate gradients through AQE network
                    self.optimizer.step()                                   # single optimization step to update variables
                    self.scheduler.step()                                   # adjust learning rate each step
                    train_loss += loss.item() * trainparams['batch_size']   # update training loss
                    train_loss /= len(self.train_loader.dataset)            # normalize training loss


            # Validate the model
            self.AQEnet.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                self.AQEnet.quantizer_layer.hardQ = True

                for i, data in (enumerate(val_loader)):
                    inputs, labels, hua, hra, hur = data
                    # hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = self.AQEnet(inputs)                       # forward pass inputs into AQE network
                    # loss = Loss1(outputs, labels, hra, hur)             # calculate batch loss
                    # loss = Loss3(outputs, labels)                       # calculate batch loss
                    loss = Loss4(outputs, labels, hra, hur)             # calculate batch loss
                    val_loss += loss.item() * trainparams['batch_size']  # update validation loss
                    val_loss /= len(val_loader.dataset)                 # normalize validation loss


                if trainparams['epoch_echo']:
                    print('\nEpoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
                        epoch, train_loss, val_loss))

                # save model if validation loss has decreased
                if val_loss <= val_loss_min:
                    if trainparams['epoch_echo']:
                        print('Validation loss same/decreased ({:.6f} --> {:.6f})... saving model.'.format(
                            val_loss_min, val_loss))
                    val_loss_min = val_loss
                    AQEnet_validated = deepcopy(self.AQEnet) # if val loss does not decrease, return the copy of AQEnet before training
                # else:
                #     self.AQEnet = AQEnet_not_trained
                if epoch % trainparams['epoch_val'] == 0:
                    if val_loss < val_loss_min_earlystop:
                        if trainparams['epoch_echo']:
                            print('Validation early stop loss decreased ({:.6f} --> {:.6f}).'.format(
                                val_loss_min_earlystop, val_loss))
                        val_loss_min_earlystop = val_loss
                    else:
                        if trainparams['epoch_echo']:
                            print('No Validation early stop loss decrease ({:.6f} --> {:.6f}). Early Stopping'.format(
                            val_loss_min_earlystop, val_loss))
                        break

                train_losses.append(train_loss)
                val_losses.append(val_loss)
            num_epochs += 1
        self.AQEnet = AQEnet_validated
        return self.AQEnet, train_losses, val_losses, num_epochs

    def evaluate(self, test_loader, sysmodelparams, trainparams):
        N_RIS = trainparams['N_RIS']
        self.AQEnet.eval()
        with torch.no_grad():
            # replace trainable tanh quantization layer with proper quantization layer
            self.AQEnet.quantizer_layer.hardQ = True

            test_size = len(test_loader.dataset.data)
            y_opt = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            y_AQE = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            y_rand = torch.view_as_complex(torch.zeros(test_size,2)).to(device)
            test_i = 0
            for i, data in (enumerate(test_loader)):
                inputs, theta_opt, hua, hra, hur = data
                inputs = inputs.to(device)
                theta_opt = theta_opt.to(device)
                hua = hua.to(device)
                hra = hra.to(device)
                hur = hur.to(device)
                len_hua = len(hua)
                theta_AQE = self.AQEnet(inputs)  # forward pass inputs into AQE network
                theta_rand = torch.rand(size=(len_hua,N_RIS), dtype=torch.double) * 2*torch.pi - torch.pi
                theta_rand = theta_rand.to(device)
                x = torch.pow(10*torch.ones(1), trainparams['snr_dB']/10)
                x = x.to(device)
                # Transmit data with RIS phases
                if sysmodelparams['K'] == 1 & sysmodelparams['M'] == 1: # SISO
                    for b in range(len_hua):
                        hra_hur = torch.matmul(hra[b], torch.diag(hur[b]))
                        awgn = torch.view_as_complex(torch.randn(1,2)).to(device)
                        y_opt[test_i] = (hua[b] + torch.matmul(hra_hur, torch.exp(1j*theta_opt[b]))) * x + awgn
                        y_AQE[test_i] = (hua[b] + torch.matmul(hra_hur, torch.exp(1j*theta_AQE[b]))) * x + awgn
                        y_rand[test_i] = (hua[b] + torch.matmul(hra_hur, torch.exp(1j*theta_rand[b]))) * x + awgn
                        test_i += 1

        P_opt = 10*torch.log10(torch.abs(torch.dot(y_opt, torch.conj(y_opt))) / test_size)
        P_AQE = 10*torch.log10(torch.abs(torch.dot(y_AQE, torch.conj(y_AQE))) / test_size)
        P_rand = 10*torch.log10(torch.abs(torch.dot(y_rand, torch.conj(y_rand))) / test_size)
        P_AQE = torch.nan_to_num(P_AQE, nan=trainparams['snr_dB'])
        return P_opt.item(), P_AQE.item(), P_rand.item()



if __name__ == "__main__":
    ####################################################################################################################
    # Training trainparams
    ####################################################################################################################
    trainparams = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'lr': 0.0001, # optimizer learning rate
                  'momentum': 0.9, # optimizer momentum for SGD
                  'batch_size': 1024, # batch training size
                  'epochs': 10, # total training duration
                  'snr_dB': -5, # transmit power to receive noise power
                  'epoch_val': 10, # validate early stop every epoch number
                  'epoch_echo': False, # flag to display epoch print losses
                  'trials': 25, # number of Ray tune trials
                  'training_iterations': 50, # number of Ray tune training iterations
                  'grace_period': 10, # min number of training iterations
                  'trials_per_device': 5, # number of trials per cpu/gpu resource
                  'Nc_RIS': 64, # number of quantizers, values that N is compresses/encoded into
                  'step_size': 10, # step size for scheduler optimizer
                  }
    search_space = { # Ray Tune Hyper parameter search space
        # "lr": tune.loguniform(1e-6, 1e-1),
        # "momentum": tune.uniform(0.01, 0.99),
        "batch_size": tune.choice([8, 16, 32, 64, 128, 256, 512, 1024]),
        # "step_size": tune.randint(5, 50),
    }

    # dataset_dir = "MATLAB/datasets/HDRISData/00/" N = 25, K = 1, M = 1
    # | bits | Optimum |     AQE |  Random | Epochs |
    # |   16 | 23.5741 | 17.4593 | 15.4874 |    640 | {'lr': 0.0010559272708640594, 'momentum': 0.44726446330961234, 'batch_size': 64}
    # |   32 | 23.5728 | 17.8364 | 15.3691 |   1625 | {'lr': 3.4809106969702625e-05, 'momentum': 0.7435784695410956, 'batch_size': 64}

    ####################################################################################################################
    # Load RIS data from .csv files
    ####################################################################################################################
    dataset_dir = "MATLAB/datasets/HDRISData/03/"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')
    sysmodelparams = pd.read_csv(dataset_dir + "systemModelParameters.csv").iloc[0]
    trainparams['mc_runs'] = RISopt.shape[0]
    trainparams['N_RIS'] = RISopt.shape[1]
    trainparams['Nw_RIS'] = sysmodelparams['Nw']
    trainparams['Nh_RIS'] = sysmodelparams['Nh']

    print('System Model parameters:', sysmodelparams, sep='\n')

    # max_bits = 1
    # bits_list = range(1,max_bits+1)
    # bits_list = [1, 2]
    # P_opt = np.zeros(len(bits_list))
    # P_AQE = np.zeros(len(bits_list))
    # P_rand = np.zeros(len(bits_list))
    # for b, bits in enumerate(bits_list):
    # print(b, bits)

    bits = 1 # bits per Quantizer
    trainparams['C_code_words'] = 2**bits
    trainparams['Nc_RIS_compressed_ratio'] = trainparams['Nc_RIS'] / trainparams['N_RIS']
    trainparams['overall_bits'] = trainparams['Nc_RIS'] * int(round(np.log2(trainparams['C_code_words'])))

    print("Training Model parameters:")
    pprint.pprint(trainparams)

    ################################################################################################################
    # Create the Torch Dataset
    ################################################################################################################
    num_train_val = int(trainparams['train_test_split'] * trainparams['mc_runs'])
    num_test = trainparams['mc_runs'] - num_train_val
    num_train = int(trainparams['train_val_split'] * num_train_val)
    num_val = num_train_val - num_train
    train_set = [] # [[sample0, label0], [sample0, label0], ... ]
    test_set = []
    val_set = []
    for i in range(0, trainparams['mc_runs']):
        theta = RISopt[i]
        thetaIn = np.reshape(theta, (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        HraIn = np.reshape(Hra[i], (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        HurIn = np.reshape(Hur[i], (sysmodelparams["Nw"], sysmodelparams["Nh"]))
        input = np.array([thetaIn, np.abs(HraIn), np.angle(HraIn), np.abs(HurIn), np.angle(HurIn)])
        if i < num_train:
            train_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
        elif i >= num_train_val:
            test_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
        else:
            val_set.append([input, theta, Hua[i], Hra[i], Hur[i]])
    train_set = LoadData(train_set)
    test_set = LoadData(test_set)
    val_set = LoadData(val_set)

    # ################################################################################################################
    # # Train & Test model with specific hyperparameters
    # ################################################################################################################
    # train_loader = DataLoader(train_set, batch_size=trainparams['batch_size'])
    # test_loader = DataLoader(test_set, batch_size=trainparams['batch_size'])
    # val_loader = DataLoader(val_set, batch_size=trainparams['batch_size'])
    # trainer = Trainer(train_loader, trainparams)
    # AQEnet, train_losses, val_losses, num_epochs = trainer.train(val_loader, trainparams)
    # x_vals, soft_quant, hard_quant = AQEnet.quantizer_layer.plot_vals()
    # print(AQEnet)
    # fig, ax = plt.subplots()
    # ax.plot(x_vals, soft_quant, label='Soft Quantizer')
    # ax.plot(x_vals, hard_quant, label='Hard Quantizer', linestyle='--')
    # ax.set_title("Quantizer Values: bits = " + str(bits))
    # ax.legend()
    # # for snr_dB in [-20, -10, -5, 0, 5, 10, 20]:
    # #     trainparams['snr_dB'] = snr_dB
    # P_opt, P_AQE, P_rand = trainer.evaluate(test_loader, sysmodelparams, trainparams)
    #
    # print("Training Model parameters:")
    # pprint.pprint(trainparams)
    # print('Receive power (dB) using RIS phase shifts with Transmit power SNR {:.0f} dB:'.format(trainparams['snr_dB']))
    # print('optimum: ', P_opt)
    # print('AQE net: ', P_AQE)
    # print('random:  ', P_rand)
    # plt.show(block=True)
    # # plt.interactive(False)

    ################################################################################################################
    # Ray Tune: Hyperparameter Tuning
    ################################################################################################################

    def objective(config):
        # trainparams['lr'] = config['lr']
        # trainparams['momentum'] = config['momentum']
        trainparams['batch_size'] = config['batch_size']
        # trainparams['step_size'] = config['step_size']
        train_loader = DataLoader(train_set, batch_size=int(config["batch_size"]))
        test_loader = DataLoader(test_set, batch_size=int(config["batch_size"]))
        val_loader = DataLoader(val_set, batch_size=int(config["batch_size"]))
        trainer = Trainer(train_loader, trainparams)
        total_epochs = 0
        while True:
            AQEnet, train_losses, val_losses, num_epochs = trainer.train(val_loader, trainparams)  # Train the model
            P_opt, P_AQE, P_rand = trainer.evaluate(test_loader, sysmodelparams, trainparams)  # Compute test results
            total_epochs += num_epochs
            tune.report({"Optimum": P_opt, "AQE": P_AQE, "Random": P_rand, "Epochs": total_epochs})  # Report to Tune

    algo = OptunaSearch()  # ②
    scheduler = ASHAScheduler(
        max_t= trainparams['training_iterations'],
        grace_period=trainparams['grace_period'],
    )
    tuner = tune.Tuner(  # ③
        tune.with_resources(
        objective,
        resources={"cpu": 24/trainparams['trials_per_device'], "gpu": 1/trainparams['trials_per_device']}
            # fraction means trials per device: fraction = device/trial,
            # My setup: CPU has 24 cores, 1 GPU
    ),
        tune_config=tune.TuneConfig(
            metric="AQE",
            mode="max",
            search_alg=algo,
            scheduler=scheduler,
            num_samples=trainparams['trials']
        ),
        run_config=tune.RunConfig(
            stop={"training_iterations": trainparams['training_iterations']},
        ),
        param_space=search_space,
    )
    results = tuner.fit()
    results_df = results.get_dataframe().sort_values('AQE',ascending=False)
    best_result = results.get_best_result("AQE", "max")

    print('System Model parameters:', sysmodelparams, sep='\n')
    print("Training Model parameters:")
    pprint.pprint(trainparams)

    print("Best trial config: {}".format(best_result.config))
    print("Best trial final Rx Power: {}".format(
        best_result.metrics["AQE"]))
    print(tabulate(results_df, headers='keys', tablefmt='psql'))