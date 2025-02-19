from copy import deepcopy
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim
from tqdm import tqdm

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
            nn.Linear(N_RIS, Nc_RIS_compressed),
            nn.ReLU(),
            nn.Linear(Nc_RIS_compressed, Nc_RIS_compressed)
        ).double()

    def forward(self, theta):
        theta_enc = self.linear_encoder(theta)
        return theta_enc


class QuantizerLayer(nn.Module):
    def __init__(self, M_code_words):
        super(QuantizerLayer, self).__init__()
        # a = amplitude, b = shift, c = slope
        # for i = 0 to M_code_words-1:
        #   z += a[i] * tanh( c[i] * (theta_n - b[i]) )
        # where theta_n is a scalar value: [-pi, +pi) and z is the quantized theta_n
        self.a = torch.nn.Parameter(
            data=torch.from_numpy(
                np.ones(M_code_words) * np.pi / M_code_words
            ), requires_grad=False)
        self.b = torch.nn.Parameter(
            data=torch.from_numpy(
                np.linspace(-1, 1, M_code_words - 1) * np.pi * 15/16),
            requires_grad=True)
        if len(self.b) > 1:
            self.c = torch.nn.Parameter(
                data=torch.from_numpy(
                    (15 / np.mean(np.diff(self.b.data.numpy()))) * np.ones(M_code_words - 1)
                ), requires_grad=False)
        else:
            self.c = torch.nn.Parameter(data=torch.from_numpy(15 / int(self.b.data) * np.ones(M_code_words - 1)),
                                        requires_grad=False)
        self.M_code_words = M_code_words

    def forward(self, theta_enc):
        # theta_enc = matrix (number of samples of train/test dataset, Nc_RIS_compressed), in the range: [-pi, +pi)
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).double().double().to(device)
        for i in range(self.M_code_words - 1):
            theta_qnt += self.a[i] * torch.tanh(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class HardQuantizerLayer(nn.Module):
    def __init__(self, a, b, c, M_code_words):
        super(HardQuantizerLayer, self).__init__()
        self.a = a
        self.b = b
        self.c = c
        self.M_code_words = M_code_words

    def forward(self, theta_enc):
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).double().double().to(device)
        for i in range(self.M_code_words - 1):
            theta_qnt += self.a[i] * torch.sign(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class DecoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(DecoderLayer, self).__init__()
        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS_compressed, N_RIS),
            nn.ReLU(),
            nn.Linear(N_RIS, N_RIS)
        ).double()

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        return theta_dec

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed, M_code_words):
        super(AutoQEncoder, self).__init__()
        self.encoder_layer = EncoderLayer(N_RIS, Nc_RIS_compressed).to(device)
        self.quantizer_layer = QuantizerLayer(M_code_words).to(device)
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

def expMSE(x, y):
    dist = torch.abs(torch.exp(1j*x) - torch.exp(1j*y))
    return torch.mean(torch.square(dist))

class Trainer(object):
    def __init__(self, train_loader):
        self.train_loader = train_loader

    def train(self, val_loader, parameters):
        N_RIS = parameters['N_RIS']
        Nc_RIS_compressed = int(N_RIS * parameters['Nc_RIS_compressed_ratio'])
        M_code_words = parameters['M_code_words']
        print('N RIS elements:', N_RIS)
        print('Nc RIS compressed:', Nc_RIS_compressed)
        print('M quantization code words:', M_code_words)
        overall_bits = Nc_RIS_compressed * int(round(np.log2(M_code_words)))
        print('overall bits:', overall_bits)

        AQEnet = AutoQEncoder(N_RIS, Nc_RIS_compressed, M_code_words).to(device)
        # criterion = nn.MSELoss()
        criterion = expMSE
        optimizer = optim.Adam(AQEnet.parameters(), lr=parameters['lr'])

        val_loss_min = np.Inf
        AQEnet_validated = deepcopy(AQEnet) # if val loss does not decrease, return the copy of AQEnet before training

        for epoch in tqdm(range(parameters['epochs'])):
            train_loss = 0.0
            val_loss = 0.0

            # Train the model
            AQEnet.train()
            for i, data in (enumerate(self.train_loader)):
                inputs, labels = data
                inputs = inputs.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()                                   # clear gradients of all variables to optimize
                outputs = AQEnet(inputs)                                # forward pass inputs into AQE network
                loss = criterion(outputs, labels)                       # calculate batch loss
                loss.backward()                                         # back propagate gradients through AQE network
                optimizer.step()                                        # single optimization step to update variables
                train_loss += loss.item() * parameters['batch_size']    # update training loss


            # Validate the model
            AQEnet_val = AQEnet
            AQEnet_val.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                AQEnet_val.quantizer_layer = HardQuantizerLayer(AQEnet_val.quantizer_layer.a,
                                                                AQEnet_val.quantizer_layer.b,
                                                                AQEnet_val.quantizer_layer.c,
                                                                M_code_words)
                for i, data in (enumerate(val_loader)):
                    inputs, labels = data
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = AQEnet(inputs)                            # forward pass inputs into AQE network
                    loss = criterion(outputs, labels)                   # calculate batch loss
                    val_loss += loss.item() * parameters['batch_size']  # update validation loss

                if epoch % 50 == 0:
                    print('\n\nEpoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
                        epoch, train_loss, val_loss))

                # save model if validation loss has decreased
                if val_loss <= val_loss_min:
                    if epoch % 50 == 0:
                        print('Validation loss decreased ({:.6f} --> {:.6f}). Saving model ...'.format(
                            val_loss_min, val_loss))
                    AQEnet_validated = AQEnet
                    val_loss_min = val_loss

        return AQEnet_validated



if __name__ == "__main__":
    # Training Parameters
    parameters = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'batch_size': 128,
                  'Nc_RIS_compressed_ratio': 0.7,
                  'M_code_words': 2**4, # 2 to the power of number of bits
                  'lr': 0.001, # optimizer learning rate
                  'epochs': 200
                  }
    print(parameters)

    # Load RIS data from .csv files
    dataset_dir = "MATLAB/datasets/HDRISData/00/"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')

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
            train_set.append([theta, theta])
        elif i >= num_train_val:
            test_set.append([theta, theta])
        else:
            val_set.append([theta, theta])
    train_set = LoadData(train_set)
    test_set = LoadData(test_set)
    val_set = LoadData(val_set)
    train_loader = DataLoader(train_set, batch_size=parameters['batch_size'])
    test_loader = DataLoader(test_set, batch_size=parameters['batch_size'])
    val_loader = DataLoader(val_set, batch_size=parameters['batch_size'])

    # Train model
    trainer = Trainer(train_loader)
    AQEnet = trainer.train(val_loader, parameters)