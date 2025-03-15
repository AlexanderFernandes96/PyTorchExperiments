# PyTorchExperiments
This repository contains projects and experiments for the purposes of gaining familiarity involving PyTorch.

## Getting Started
This repository was created using [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) allowing to run PyTorchExperiments on a local computer.
In order to run on a local pc you will need to install the following libraries to the local Python environment.
(This will install to the .venv folder if using PyCharm IDE).

### Required
Run the following commands in the terminal to install PyTorch libraries to the local Python environment.
```sh
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install "ray[tune]" torch torchvision
pip install optuna
pip install numpy
pip install pandas
pip install tabulate
pip install tqdm
pip install matplotlib
```

### Test Run
To check if PyTorch installed correctly run: [quickstart.py](quickstart.py).

## Description
Descriptions of the Python projects, directories, and content included in this repository.

### MATLAB
MATLAB (version 2022a) is used to generate a dataset for a simulated RIS communication system model, i.e. channel matrices, pilots, receive signal, etc.
* [generateHDRISData.m](MATLAB/generateHDRISData.m)
  * Run this MATLAB script to generate data for a Half-Duplex RIS model
* [showChannels.m](MATLAB/showChannels.m)
  * show the channels and corresponding optimal RIS phase shifts as 2D images
* [src/](MATLAB/src/)
  * directory containing MATLAB scripts and functions to generate RIS data
  * To change the parameters of the system model change contents of: [src/systemModelParameters.m](MATLAB/src/systemModelParameters.m)
* [datasets/](MATLAB/datasets/)
  * directory to store the generated datasets.
  * for Python scripts use the .csv files from this directory to easily load the datasets into a numpy array.
  
### Quick Start
A simple autoencoder neural network classifier on MNIST data. 
Code was obtained from: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html. 
* Files included in project:
  * [quickstart.py](quickstart.py)

### SISO Convolutional Neural Network AutoEncoder with Quantization
Simple autoencoder to quantize optimal RIS phases into bits for phase shift feedback in a SISO RIS-assisted communication system model.
* Files included in project:
  * [autoencoder_quantization.py](autoencoder_quantization.py)