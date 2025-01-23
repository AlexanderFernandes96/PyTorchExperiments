# PyTorchExperiments
This repository contains projects and experiments for the purposes of gaining familiarity involving PyTorch.

## Getting Started
This repository was created using [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) allowing to run PyTorchExperiments on a local computer.
In order to run on a local pc you will need to install the following libraries to the local Python environment.
(This will install to [.venv](.venv) if using PyCharm IDE).

### Required
Run the following command in the terminal to install PyTorch to the local Python environment .
```sh
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Test Run
To check if PyTorch installed correctly run: [quickstart.py](quickstart.py).

## Description
Descriptions of the Python Projects included in this repository.

### Quick Start
A simple autoencoder neural network classifier on MNIST data. 
Code was obtained from: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html. 
* Files included in project:
  * [quickstart.py](quickstart.py)

### Neural Network with Quantization
Simple autoencoder that implements quantization on the encoded latent variables.
* Files included in project:
  * [autoencoder_quantization.py](autoencoder_quantization.py)
* TODO: implement quantization