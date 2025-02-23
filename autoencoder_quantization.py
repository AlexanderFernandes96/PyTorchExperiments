from copy import deepcopy
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim
from tqdm import tqdm
import pandas as pd

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
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(EncoderLayer, self).__init__()
        self.linear_encoder = nn.Sequential(
            nn.Linear(N_RIS, int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed) ),
            nn.SELU(),
            nn.Linear(int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
            nn.SELU(),
            nn.Linear(int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), Nc_RIS_compressed)
        ).double()

    def forward(self, theta):
        theta_enc = self.linear_encoder(theta)
        return theta_enc


class QuantizerLayer(nn.Module):
    def __init__(self, C_code_words):
        super(QuantizerLayer, self).__init__()
        # a = amplitude, b = shift, c = slope
        # for i = 0 to C_code_words-1:
        #   z += a[i] * tanh( c[i] * (theta_n - b[i]) )
        # where theta_n is a scalar value: [-pi, +pi) and z is the quantized theta_n
        self.a = torch.nn.Parameter(
            data=torch.from_numpy(
                np.ones(C_code_words) * np.pi / C_code_words
            ), requires_grad=False)
        self.b = torch.nn.Parameter(
            data=torch.from_numpy(
                np.linspace(-1, 1, C_code_words - 1) * np.pi * 15/16),
            requires_grad=True)
        if len(self.b) > 1:
            self.c = torch.nn.Parameter(
                data=torch.from_numpy(
                    (15 / np.mean(np.diff(self.b.data.numpy()))) * np.ones(C_code_words - 1)
                ), requires_grad=False)
        else:
            self.c = torch.nn.Parameter(data=torch.from_numpy(15 / int(self.b.data) * np.ones(C_code_words - 1)),
                                        requires_grad=False)
        self.C_code_words = C_code_words

    def forward(self, theta_enc):
        # theta_enc = matrix (number of samples of train/test dataset, Nc_RIS_compressed), in the range: [-pi, +pi)
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).double().double().to(device)
        for i in range(self.C_code_words - 1):
            theta_qnt += self.a[i] * torch.tanh(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class HardQuantizerLayer(nn.Module):
    def __init__(self, a, b, c, C_code_words):
        super(HardQuantizerLayer, self).__init__()
        self.a = a
        self.b = b
        self.c = c
        self.C_code_words = C_code_words

    def forward(self, theta_enc):
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).double().double().to(device)
        for i in range(self.C_code_words - 1):
            theta_qnt += self.a[i] * torch.sign(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class DecoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(DecoderLayer, self).__init__()
        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS_compressed, int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
            nn.SELU(),
            nn.Linear(int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
            nn.SELU(),
            nn.Linear(int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), N_RIS)
        ).double()

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        return theta_dec

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed, C_code_words):
        super(AutoQEncoder, self).__init__()
        self.encoder_layer = EncoderLayer(N_RIS, Nc_RIS_compressed).to(device)
        self.quantizer_layer = QuantizerLayer(C_code_words).to(device)
        self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS_compressed).to(device)

    def forward(self, theta):
        theta_enc = self.encoder_layer(theta)
        theta_qnt = self.quantizer_layer(theta_enc)
        theta_dec = self.decoder_layer(theta_qnt)
        return theta_dec

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
    return torch.mean(dist)

def Loss2(x, y):
    dist = torch.abs(torch.exp(1j*x) - torch.exp(1j*y))
    return torch.mean(torch.square(dist))

def Loss3(x, y):
    dist = torch.abs(x - y)
    return torch.mean(torch.square(dist))

class Trainer(object):
    def __init__(self, train_loader):
        self.train_loader = train_loader

    def train(self, val_loader, parameters):
        N_RIS = parameters['N_RIS']
        Nc_RIS_compressed = int(N_RIS * parameters['Nc_RIS_compressed_ratio'])
        C_code_words = parameters['C_code_words']
        print('N RIS elements:', N_RIS)
        print('Nc RIS compressed:', Nc_RIS_compressed)
        print('C quantization code words:', C_code_words)
        overall_bits = Nc_RIS_compressed * int(round(np.log2(C_code_words)))
        print('overall bits per transmission:', overall_bits)

        AQEnet = AutoQEncoder(N_RIS, Nc_RIS_compressed, C_code_words).to(device)
        # criterion = nn.MSELoss()
        # optimizer = optim.Adam(AQEnet.parameters(), lr=parameters['lr'])
        optimizer = optim.AdamW(AQEnet.parameters(), lr=parameters['lr'])

        val_loss_min = np.Inf
        AQEnet_validated = deepcopy(AQEnet) # if val loss does not decrease, return the copy of AQEnet before training

        train_losses = []
        val_losses = []
        for epoch in tqdm(range(parameters['epochs'])):
            train_loss = 0.0
            val_loss = 0.0

            # Train the model
            AQEnet.train()
            for i, data in (enumerate(self.train_loader)):
                inputs, labels, hua, hra, hur = data
                hua = hua.to(device)
                hra = hra.to(device)
                hur = hur.to(device)
                inputs = inputs.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()                                   # clear gradients of all variables to optimize
                outputs = AQEnet(inputs)                                # forward pass inputs into AQE network
                loss = Loss1(outputs, labels, hra, hur)                 # calculate batch loss
                # loss = Loss3(outputs, labels)                           # calculate batch loss
                loss.backward()                                         # back propagate gradients through AQE network
                optimizer.step()                                        # single optimization step to update variables
                train_loss += loss.item() * parameters['batch_size']    # update training loss
                train_loss /= len(train_loader.dataset)                 # normalize training loss


            # Validate the model
            AQEnet_val = AQEnet
            AQEnet_val.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                AQEnet_val.quantizer_layer = HardQuantizerLayer(AQEnet_val.quantizer_layer.a,
                                                                AQEnet_val.quantizer_layer.b,
                                                                AQEnet_val.quantizer_layer.c,
                                                                C_code_words)
                for i, data in (enumerate(val_loader)):
                    inputs, labels, hua, hra, hur = data
                    hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = AQEnet(inputs)                            # forward pass inputs into AQE network
                    loss = Loss1(outputs, labels, hra, hur)             # calculate batch loss
                    # loss = Loss3(outputs, labels)                       # calculate batch loss
                    val_loss += loss.item() * parameters['batch_size']  # update validation loss
                    val_loss /= len(val_loader.dataset)                 # normalize validation loss

                if epoch % 50 == 0 or epoch == parameters['epochs']-1:
                    print('\n\nEpoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
                        epoch, train_loss, val_loss))

                # save model if validation loss has decreased
                if val_loss <= val_loss_min:
                    if epoch % 50 == 0 or epoch == parameters['epochs']-1:
                        print('Validation loss decreased ({:.6f} --> {:.6f}). Saving model ...'.format(
                            val_loss_min, val_loss))
                    AQEnet_validated = AQEnet
                    val_loss_min = val_loss

                train_losses.append(train_loss)
                val_losses.append(val_loss)

        return AQEnet_validated, train_losses, val_losses

    def evaluate(self, test_loader, smp, parameters, AQEnet):
        N_RIS = parameters['N_RIS']
        C_code_words = parameters['C_code_words']
        AQEnet.eval()
        with torch.no_grad():
            # replace trainable tanh quantization layer with proper quantization layer
            AQEnet.quantizer_layer = HardQuantizerLayer(AQEnet.quantizer_layer.a,
                                                        AQEnet.quantizer_layer.b,
                                                        AQEnet.quantizer_layer.c,
                                                        C_code_words)
            y_opt = []
            y_AQE = []
            y_rand = []
            for i, data in (enumerate(test_loader)):
                inputs, theta_opt, hua, hra, hur = data
                inputs = inputs.to(device)
                # theta_opt = theta_opt.to(device)
                # hua = hua.to(device)
                # hra = hra.to(device)
                # hur = hur.to(device)
                theta_AQE = AQEnet(inputs).cpu()  # forward pass inputs into AQE network
                theta_rand = np.random.uniform(low=-np.pi, high=+np.pi, size=(len(hua),N_RIS))

                # Transmit data with RIS phases
                if smp['K'] == 1 & smp['M'] == 1: # SISO
                    for b in range(len(hua)):
                        hua_np = np.array(hua[b])
                        hra_np = np.array(hra[b])
                        hur_np = np.array(hur[b])
                        theta_opt_np = np.array(theta_opt[b])
                        theta_AQE_np = np.array(theta_AQE[b])
                        awgn = np.random.randn(1,2).view(np.complex_)[0,0]
                        y_opt_b = (hua_np + hra_np.T @ np.diag(theta_opt_np) @ hur_np) * np.power(10, parameters['snr_dB']/10) + awgn
                        y_AQE_b = (hua_np + hra_np.T @ np.diag(theta_AQE_np) @ hur_np) * np.power(10, parameters['snr_dB']/10) + awgn
                        y_rand_b = (hua_np + hra_np.T @ np.diag(theta_rand[b]) @ hur_np) * np.power(10, parameters['snr_dB']/10) + awgn
                        y_opt.append(y_opt_b)
                        y_AQE.append(y_AQE_b)
                        y_rand.append(y_rand_b)
            y_opt = np.matrix(y_opt, dtype=np.complex_)
            y_AQE = np.matrix(y_AQE, dtype=np.complex_)
            y_rand = np.matrix(y_rand, dtype=np.complex_)

        return y_opt, y_AQE, y_rand




if __name__ == "__main__":
    # Training Parameters
    parameters = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'batch_size': 1000,
                  'Nc_RIS_compressed_ratio': 0.2,
                  'C_code_words': 2**8, # 2 to the power of number of bits
                  'lr': 0.001, # optimizer learning rate
                  'epochs': 500,
                  'snr_dB': 5
                  }
    print(parameters)

    # Load RIS data from .csv files
    dataset_dir = "MATLAB/datasets/HDRISData/01/"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')
    smp = pd.read_csv(dataset_dir + "systemModelParameters.csv").iloc[0]


    # Create the Torch Dataset
    parameters['mc_runs'] = RISopt.shape[0]
    parameters['N_RIS'] = RISopt.shape[1]
    num_train_val = int(parameters['train_test_split'] * parameters['mc_runs'])
    num_test = parameters['mc_runs'] - num_train_val
    num_train = int(parameters['train_val_split'] * num_train_val)
    num_val = num_train_val - num_train
    train_set = [] # [[sample0, label0], [sample0, label0], ... ]
    test_set = []
    val_set = []
    for i in range(0, parameters['mc_runs']):
        theta = RISopt[i]
        if i < num_train:
            train_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
        elif i >= num_train_val:
            test_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
        else:
            val_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
    train_set = LoadData(train_set)
    test_set = LoadData(test_set)
    val_set = LoadData(val_set)
    train_loader = DataLoader(train_set, batch_size=parameters['batch_size'])
    test_loader = DataLoader(test_set, batch_size=parameters['batch_size'])
    val_loader = DataLoader(val_set, batch_size=parameters['batch_size'])

    # Train model
    trainer = Trainer(train_loader)
    AQEnet, train_losses, val_losses = trainer.train(val_loader, parameters)
    print(AQEnet)

    # Test model
    print('System Model Parameters:', smp, sep='\n')
    for snr_dB in [-20, -10, -5, 0, 5, 10, 20]:
        parameters['snr_dB'] = snr_dB
        y_opt, y_AQE, y_rand = trainer.evaluate(test_loader, smp, parameters, AQEnet)

        print('Receive power using RIS phase shifts with SNR {:.0f} dB:'.format(snr_dB))
        print('optimum: {:.6f}'.format(np.abs(y_opt @ y_opt.H)[0, 0] / y_opt.size))
        print('AQE net: {:.6f}'.format(np.abs(y_AQE @ y_AQE.H)[0, 0] / y_AQE.size))
        print('random:  {:.6f}'.format(np.abs(y_rand @ y_rand.H)[0, 0] / y_rand.size))