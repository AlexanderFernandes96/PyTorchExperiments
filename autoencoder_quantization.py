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
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(EncoderLayer, self).__init__()
        # self.linear_encoder = nn.Sequential(
        #     nn.Linear(N_RIS, int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed) ),
        #     # nn.SELU(),
        #     nn.ReLU(),
        #     nn.Linear(int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
        #     # nn.SELU(),
        #     nn.ReLU(),
        #     nn.Linear(int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), Nc_RIS_compressed)
        # )

        self.linear_encoder = nn.Sequential(
            nn.Linear(N_RIS, Nc_RIS_compressed),
            # nn.SELU(),
            nn.ReLU(),
            nn.Linear(Nc_RIS_compressed, Nc_RIS_compressed)
        )

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
                np.ones(C_code_words-1) * np.pi / (C_code_words - 1)
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

    def forward(self, theta_enc):
        # theta_enc = matrix (number of samples of train/test dataset, Nc_RIS_compressed), in the range: [-pi, +pi)
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).to(device)
        for i in range(self.C_code_words - 1):
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


class HardQuantizerLayer(nn.Module):
    def __init__(self, a, b, c, C_code_words):
        super(HardQuantizerLayer, self).__init__()
        self.a = a
        self.b = b
        self.c = c
        self.C_code_words = C_code_words

    def forward(self, theta_enc):
        theta_qnt = torch.zeros(theta_enc.shape[0], theta_enc.shape[1]).to(device)
        for i in range(self.C_code_words - 1):
            theta_qnt += self.a[i] * torch.sign(self.c[i] * (theta_enc - self.b[i]))
        return theta_qnt

class DecoderLayer(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed):
        super(DecoderLayer, self).__init__()
        # self.linear_decoder = nn.Sequential(
        #     nn.Linear(Nc_RIS_compressed, int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
        #     # nn.SELU(),
        #     nn.ReLU(),
        #     nn.Linear(int(1*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed)),
        #     # nn.SELU(),
        #     nn.ReLU(),
        #     nn.Linear(int(2*(N_RIS - Nc_RIS_compressed)/3 + Nc_RIS_compressed), N_RIS)
        # )

        self.linear_decoder = nn.Sequential(
            nn.Linear(Nc_RIS_compressed, N_RIS),
            # nn.SELU(),
            nn.ReLU(),
            nn.Linear(N_RIS, N_RIS)
        )

    def forward(self, theta_qnt):
        theta_dec = self.linear_decoder(theta_qnt)
        return torch.fmod(theta_dec, np.pi)

# Inspired by: N. Shlezinger and Y. C. Eldar, “Deep task-based quantization,” Entropy, vol. 23, no. 1, pp. 1–18, Jan.
# 2021, doi: 10.3390/e23010104.
# Code: https://github.com/arielamar123/ADC-Learning-hyperopt
class AutoQEncoder(nn.Module):
    def __init__(self, N_RIS, Nc_RIS_compressed, C_code_words):
        super(AutoQEncoder, self).__init__()
        self.encoder_layer = EncoderLayer(N_RIS, Nc_RIS_compressed).to(device)
        self.quantizer_layer = QuantizerLayer(C_code_words).to(device)
        self.decoder_layer = DecoderLayer(N_RIS, Nc_RIS_compressed).to(device)
        self.quantizer_layer_plot = self.quantizer_layer

    def forward(self, theta):
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
        dist += torch.square(torch.abs(hra[:,n]*hur[:,n])) * torch.square(torch.abs(torch.exp(1j*x[:,n]) - torch.exp(1j*y[:,n])))
    return torch.mean(dist)

def Loss2(x, y):
    dist = torch.abs(torch.exp(1j*x) - torch.exp(1j*y))
    return torch.mean(torch.square(dist))

def Loss3(x, y):
    dist = torch.abs(x - y)
    return torch.mean(torch.square(dist))

class Trainer(object):
    def __init__(self, train_loader, trainparams):
        self.train_loader = train_loader
        self.N_RIS = trainparams['N_RIS']
        self.Nc_RIS_compressed = int(self.N_RIS * trainparams['Nc_RIS_compressed_ratio'])
        self.C_code_words = trainparams['C_code_words']
        # print('N RIS elements:', self.N_RIS)
        # print('Nc RIS compressed:', self.Nc_RIS_compressed)
        # print('C quantization code words:', self.C_code_words)
        # overall_bits = self.Nc_RIS_compressed * int(round(np.log2(self.C_code_words)))
        # print('overall bits per transmission:', overall_bits)
        self.AQEnet = AutoQEncoder(self.N_RIS, self.Nc_RIS_compressed, self.C_code_words).to(device)
        self.optimizer = optim.Adam(self.AQEnet.parameters(), lr=trainparams['lr'])

    def train(self, val_loader, trainparams):

        val_loss_min = np.Inf
        AQEnet_validated = deepcopy(self.AQEnet) # if val loss does not decrease, return the copy of AQEnet before training

        train_losses = []
        val_losses = []
        for epoch in tqdm(range(trainparams['epochs']), disable=DISABLE_TQDM):
            train_loss = 0.0
            val_loss = 0.0

            # Train the model
            self.AQEnet.train()
            for i, data in (enumerate(self.train_loader)):
                inputs, labels, hua, hra, hur = data
                hua = hua.to(device)
                hra = hra.to(device)
                hur = hur.to(device)
                inputs = inputs.to(device)
                labels = labels.to(device)
                self.optimizer.zero_grad()                                   # clear gradients of all variables to optimize
                outputs = self.AQEnet(inputs)                                # forward pass inputs into AQE network
                loss = Loss1(outputs, labels, hra, hur)                 # calculate batch loss
                # loss = Loss3(outputs, labels)                           # calculate batch loss
                loss.backward()                                         # back propagate gradients through AQE network
                self.optimizer.step()                                        # single optimization step to update variables
                train_loss += loss.item() * trainparams['batch_size']    # update training loss
                train_loss /= len(self.train_loader.dataset)                 # normalize training loss


            # Validate the model
            AQEnet_val = self.AQEnet
            AQEnet_val.eval()
            with torch.no_grad():
                # replace trainable tanh quantization layer with proper quantization layer
                AQEnet_val.quantizer_layer = HardQuantizerLayer(AQEnet_val.quantizer_layer.a,
                                                                AQEnet_val.quantizer_layer.b,
                                                                AQEnet_val.quantizer_layer.c,
                                                                self.C_code_words)
                for i, data in (enumerate(val_loader)):
                    inputs, labels, hua, hra, hur = data
                    hua = hua.to(device)
                    hra = hra.to(device)
                    hur = hur.to(device)
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    outputs = self.AQEnet(inputs)                            # forward pass inputs into AQE network
                    loss = Loss1(outputs, labels, hra, hur)             # calculate batch loss
                    # loss = Loss3(outputs, labels)                       # calculate batch loss
                    val_loss += loss.item() * trainparams['batch_size']  # update validation loss
                    val_loss /= len(val_loader.dataset)                 # normalize validation loss


                if (epoch % trainparams['epoch_print'] == 0 or epoch == trainparams['epochs']-1) and trainparams['epoch_echo']:
                    print('\nEpoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
                        epoch, train_loss, val_loss))

                # save model if validation loss has decreased
                if val_loss <= val_loss_min:
                    if (epoch % trainparams['epoch_print'] == 0 or epoch == trainparams['epochs']-1) and trainparams['epoch_echo']:
                        print('Validation loss decreased ({:.6f} --> {:.6f}). Saving model ...'.format(
                            val_loss_min, val_loss))
                    AQEnet_validated = self.AQEnet
                    val_loss_min = val_loss

                train_losses.append(train_loss)
                val_losses.append(val_loss)

        self.AQEnet = AQEnet_validated
        return AQEnet_validated, train_losses, val_losses

    def evaluate(self, test_loader, sysmodelparams, trainparams):
        N_RIS = trainparams['N_RIS']
        C_code_words = trainparams['C_code_words']
        self.AQEnet.eval()
        with torch.no_grad():
            # replace trainable tanh quantization layer with proper quantization layer
            self.AQEnet.quantizer_layer = HardQuantizerLayer(self.AQEnet.quantizer_layer.a,
                                                        self.AQEnet.quantizer_layer.b,
                                                        self.AQEnet.quantizer_layer.c,
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
                theta_AQE = self.AQEnet(inputs).cpu()  # forward pass inputs into AQE network
                theta_rand = np.random.uniform(low=-np.pi, high=+np.pi, size=(len(hua),N_RIS))

                # Transmit data with RIS phases
                if sysmodelparams['K'] == 1 & sysmodelparams['M'] == 1: # SISO
                    for b in range(len(hua)):
                        hua_np = np.array(hua[b])
                        hra_np = np.array(hra[b])
                        hur_np = np.array(hur[b])
                        theta_opt_np = np.array(theta_opt[b])
                        theta_AQE_np = np.array(theta_AQE[b])

                        T = 100 # transmissions
                        awgn = np.random.randn(1,2).view(np.complex_)[0,0]
                        y_opt_b = (hua_np + hra_np.T @ np.diag(theta_opt_np) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                        y_AQE_b = (hua_np + hra_np.T @ np.diag(theta_AQE_np) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                        y_rand_b = (hua_np + hra_np.T @ np.diag(theta_rand[b]) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                        for t in range(T-1):
                            awgn = np.random.randn(1,2).view(np.complex_)[0,0]
                            y_opt_b += (hua_np + hra_np.T @ np.diag(theta_opt_np) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                            y_AQE_b += (hua_np + hra_np.T @ np.diag(theta_AQE_np) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                            y_rand_b += (hua_np + hra_np.T @ np.diag(theta_rand[b]) @ hur_np) * np.power(10, trainparams['snr_dB']/10) + awgn
                        y_opt.append(y_opt_b/T)
                        y_AQE.append(y_AQE_b/T)
                        y_rand.append(y_rand_b/T)
            y_opt = np.matrix(y_opt, dtype=np.complex_)
            y_AQE = np.matrix(y_AQE, dtype=np.complex_)
            y_rand = np.matrix(y_rand, dtype=np.complex_)

        P_opt = 10*np.log10(np.abs(y_opt @ y_opt.H)[0, 0] / y_opt.size)
        P_AQE = 10*np.log10(np.abs(y_AQE @ y_AQE.H)[0, 0] / y_AQE.size)
        P_rand = 10*np.log10(np.abs(y_rand @ y_rand.H)[0, 0] / y_rand.size)
        return P_opt, P_AQE, P_rand



if __name__ == "__main__":
    ####################################################################################################################
    # Training trainparams
    ####################################################################################################################
    trainparams = {'train_test_split': 0.8, # split between train/test data
                  'train_val_split': 0.8,  # after the train/test split, split train data into train/val data
                  'batch_size': 64,
                  'lr': 1, # optimizer learning rate
                  'epochs': 500, # total training duration
                  'snr_dB': -5,
                  'epoch_print': 5, # print losses on every epoch number
                  'epoch_echo': False, # flag to display epoch print losses
                  'trials': 50 # number of Raylet trials
                  }

    ####################################################################################################################
    # Load RIS data from .csv files
    ####################################################################################################################
    dataset_dir = "MATLAB/datasets/HDRISData/00/"
    Hua = load_complex(dataset_dir, "Hua_r", "Hua_i")
    Hra = load_complex(dataset_dir, "Hra_r", "Hra_i")
    Hur = load_complex(dataset_dir, "Hur_r", "Hur_i")
    RISopt = np.loadtxt(dataset_dir + "RISopt.csv", delimiter=',')
    sysmodelparams = pd.read_csv(dataset_dir + "systemModelParameters.csv").iloc[0]
    trainparams['mc_runs'] = RISopt.shape[0]
    trainparams['N_RIS'] = RISopt.shape[1]

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
    trainparams['Nc_RIS'] = 10
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
        if i < num_train:
            train_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
        elif i >= num_train_val:
            test_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
        else:
            val_set.append([theta, theta, Hua[i], Hra[i], Hur[i]])
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
    # AQEnet, train_losses, val_losses = trainer.train(val_loader, trainparams)
    # x_vals, soft_quant, hard_quant = AQEnet.quantizer_layer_plot.plot_vals()
    # # print(AQEnet)
    # fig, ax = plt.subplots()
    # ax.plot(x_vals, soft_quant, label='Soft Quantizer')
    # ax.plot(x_vals, hard_quant, label='Hard Quantizer', linestyle='--')
    # ax.set_title("Quantizer Values: bits = " + str(bits))
    # ax.legend()
    # # for snr_dB in [-20, -10, -5, 0, 5, 10, 20]:
    # #     trainparams['snr_dB'] = snr_dB
    # P_opt, P_AQE, P_rand = trainer.evaluate(test_loader, sysmodelparams, trainparams)
    #
    # print('C code words:', 2**bits)
    # print('Receive power (dB) using RIS phase shifts with Transmit power SNR {:.0f} dB:'.format(trainparams['snr_dB']))
    # print('optimum: ', P_opt)
    # print('AQE net: ', P_AQE)
    # print('random:  ', P_rand)
    # plt.show(block=True)
    # plt.interactive(False)

    ################################################################################################################
    # Ray Tune: Hyperparameter Tuning
    ################################################################################################################
    search_space = {
        "lr": tune.loguniform(1e-4, 1e-2),
        "batch_size": tune.choice([64, 128, 256, 512, 1024]),
    }

    def objective(config):
        trainparams['batch_size'] = config['batch_size']
        trainparams['lr'] = config['lr']
        train_loader = DataLoader(train_set, batch_size=int(config["batch_size"]))
        test_loader = DataLoader(test_set, batch_size=int(config["batch_size"]))
        val_loader = DataLoader(val_set, batch_size=int(config["batch_size"]))
        trainer = Trainer(train_loader, trainparams)
        model = trainer.AQEnet
        optimizer = torch.optim.Adam(  # Tune the optimizer
            model.parameters(), lr=config["lr"]
        )
        trainer.optimizer = optimizer
        while True:
            AQEnet, train_losses, val_losses = trainer.train(val_loader, trainparams)  # Train the model
            P_opt, P_AQE, P_rand = trainer.evaluate(test_loader, sysmodelparams, trainparams)  # Compute test results
            tune.report({"Optimum Rx": P_opt, "AQE Rx": P_AQE, "Random Rx": P_rand})  # Report to Tune

    algo = OptunaSearch()  # ②
    scheduler = ASHAScheduler(
        max_t=10,
        grace_period=2,
    )

    tuner = tune.Tuner(  # ③
        tune.with_resources(
        objective,
        resources={"gpu": 1/20} # fraction means shared between trials
    ),
        tune_config=tune.TuneConfig(
            metric="AQE Rx",
            mode="max",
            search_alg=algo,
            scheduler=scheduler,
            num_samples=trainparams['trials']
        ),
        run_config=tune.RunConfig(
            stop={"training_iteration": 5},
        ),
        param_space=search_space,
    )
    results = tuner.fit()
    results_df = results.get_dataframe().sort_values('AQE Rx',ascending=False)
    best_result = results.get_best_result("AQE Rx", "max")

    print('System Model parameters:', sysmodelparams, sep='\n')
    print("Training Model parameters:")
    pprint.pprint(trainparams)

    print("Best trial config: {}".format(best_result.config))
    print("Best trial final Rx Power: {}".format(
        best_result.metrics["AQE Rx"]))
    print(tabulate(results_df, headers='keys', tablefmt='psql'))