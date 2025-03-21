#!/bin/bash
#SBATCH --account=def-psaromil
#SBATCH --nodes=1
#SBATCH --gpus-per-node=4
#SBATCH --mem=64G
#SBATCH --time=01-00:00 # days-hours:minutes
#SBATCH --output=/home/alex96/scratch/logs/slurm/job-%j.out
#SBATCH --error=/home/alex96/scratch/logs/slurm/job-%j.out
#SBATCH --mail-user=alexander.fernandes@mail.mcgill.ca
#SBATCH --mail-type=ALL

printf "%s\n" "-----------------------"
printf "%s\n" "load python, gcc, arrow"
printf "%s\n" "-----------------------"
module purge
module load python/3.11
module load gcc arrow/19.0.1
export PYTHONUNBUFFERED=TRUE
sleep 1
printf "%s\n" "----------"
printf "%s\n" "virtualenv"
printf "%s\n" "----------"
virtualenv --no-download --python=python3.11 $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
#virtualenv -v --no-download ~/scratch/env
#source ~/scratch/env/bin/activate
sleep 1
printf "%s\n" "-------------------------"
printf "%s\n" "pip install --upgrade pip"
printf "%s\n" "-------------------------"
pip install --no-index --upgrade pip
sleep 1
printf "%s\n" "------------------------------"
printf "%s\n" "installing python requirements"
printf "%s\n" "------------------------------"
cat requirements.txt
pip install --no-index -r requirements.txt
sleep 1
printf "%s\n" "-----------------------------------"
printf "%s\n" "running autoencoder_quantization.py"
printf "%s\n" "-----------------------------------"
srun python -u autoencoder_quantization.py
printf "%s\n" "--------"
printf "%s\n" "finished"
printf "%s\n" "--------"

