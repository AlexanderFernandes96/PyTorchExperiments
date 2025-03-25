from autoencoder_quantization import *

# Disable the loading bars:
DISABLE_TQDM = False
# DISABLE_TQDM = True

# Get cpu, gpu or mps device for training.
device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Detected {torch.cuda.device_count()} gpus, using {device} device,", flush=True)

if __name__ == "__main__":
    print('------------')
    print('Start Script')
    print('------------')

    path_dir = "/home/alex96/scratch/"
    # path_dir = "MATLAB/"
    results_dir = path_dir + "logs/SISO_AchievableRateExperiments/02/"

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


    Nc_array = 2**np.array(range(0,8))

    # Nc_array = [32]

    ####################################################################################################################
    # Load RIS data from .csv files
    ####################################################################################################################
    print('---------')
    print('Load Data')
    print('---------')
    dataset_dir = path_dir + "datasets/HDRISData/08/"
    # dataset_dir = path_dir + "datasets/HDRISData/04/"
    # dataset_dir = path_dir + "datasets/HDRISData/03/"
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
        # input = np.array([theta, np.real(Hra[i]), np.imag(Hra[i]), np.real(Hur[i]), np.imag(Hur[i])])
        input = np.array([theta, np.abs(Hra[i]), np.angle(Hra[i]), np.abs(Hur[i]), np.angle(Hur[i])])
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
        AQEnet = AutoQEncoder(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['Nw_RIS'], trainparams['Nh_RIS'], trainparams['C_code_words'], device)
        AQEnet = nn.DataParallel(AQEnet)
        linQ = LinearQuantizer(trainparams['N_RIS'], trainparams['Nc_RIS'], trainparams['C_code_words'], device)
        linQ = nn.DataParallel(linQ)
        AQEtrainer = Trainer(train_loader, trainparams, AQEnet, device)
        linQtrainer = Trainer(train_loader, trainparams, linQ, device)
        print(AQEtrainer.model, flush=True)
        total_params = sum(p.numel() for p in AQEtrainer.model.parameters())
        print('Number of parameters:', total_params, flush=True)
        print(linQtrainer.model, flush=True)
        total_params = sum(p.numel() for p in linQtrainer.model.parameters())
        print('Number of parameters:', total_params, flush=True)
        AQEnet, AQEnet_train_losses, AQEnet_val_losses, num_epochs = AQEtrainer.train(val_loader, trainparams)
        linQ, AQEnet_train_losses, AQEnet_val_losses, num_epochs = linQtrainer.train(val_loader, trainparams)

        R_opt, R_AQE, R_rand = AQEtrainer.evaluate(test_loader, sysmodelparams, trainparams)
        R_opt, R_linQ, R_rand = linQtrainer.evaluate(test_loader, sysmodelparams, trainparams)

        print("-------------------------------------------------------------------------------------------------------")
        print("Training Model parameters:", flush=True)
        pprint.pprint(trainparams)
        print('Achievable Rate (bps/Hz) using RIS phase shifts with Transmit power SNR {:.0f} dB:'.format(trainparams['snr_dB']), flush=True)
        print('optimum: ', R_opt, flush=True)
        print('AQE net: ', R_AQE, flush=True)
        print('lin Q:   ', R_linQ, flush=True)
        print('random:  ', R_rand, flush=True)
        print("-------------------------------------------------------------------------------------------------------\n\n")
        R_opt_array[i] = R_opt
        R_AQE_array[i] = R_AQE
        R_linQ_array[i] = R_linQ
        R_rand_array[i] = R_rand

    d = {'Nc': Nc_array, 'R_opt': R_opt_array, 'R_AQE': R_AQE_array, 'R_linQ': R_linQ_array, 'R_rand': R_rand_array}
    results_df = pandas.DataFrame(d)
    print('Total bits:', trainparams['overall_bits'], flush=True)
    print(results_df, flush=True)
    print('Saving to:', results_dir + results_file, flush=True)

    results_df.to_csv(results_dir + results_file, sep='\t', encoding='utf-8', index=False, header=True)

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