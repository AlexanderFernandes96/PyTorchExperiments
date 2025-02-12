import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

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
        super(EncoderLayer).__init__()
        self.linear_encoder = nn.Sequential(
            nn.Linear(N_RIS, Nc_RIS_compressed),
            nn.ReLU(),
            nn.Linear(Nc_RIS_compressed, Nc_RIS_compressed)
        )

    def forward(self, theta):
        theta_enc = self.linear_encoder(theta)
        return theta_enc


class QuantizerLayer(nn.Module):
    def __init__(self, M_code_words):
        super(QuantizerLayer).__init__()
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
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).double().to(device)
        for i in range(self.M_code_words - 1):
            theta_qnt += self.a[i] * torch.tanh(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class DecoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(DecoderLayer).__init__()
        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS_compressed, N_RIS),
            nn.ReLU(),
            nn.Linear(N_RIS, N_RIS)
        )

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        return theta_dec

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed, M_code_words):
        super(AutoQEncoder).__init__()
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

if __name__ == "__main__":
    # parameters
    param_batch_size = 64


    # Load RIS data from .csv files
    dataset_dir = "MATLAB/datasets/HDRISData/00/"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')

    # Create the Torch Dataset
    mc_runs = RISopt.shape[0]
    train_test_ratio = 0.8
    num_train = int(train_test_ratio * mc_runs)
    num_test = mc_runs - num_train # first split is train data and remaining is test, in future randomize this
    training_set = [] # [[sample0, label0], [sample0, label0], ... ]
    for i in range(num_train):
        theta = RISopt[i]
        training_set.append([theta, theta])
    training_set = LoadData(training_set)
    testing_set = []
    for i in range(num_test):
        theta = RISopt[i+num_train]
        testing_set.append([theta, theta])
    testing_set = LoadData(testing_set)

    # Train model

    train_loader = DataLoader(training_set, batch_size=param_batch_size)
