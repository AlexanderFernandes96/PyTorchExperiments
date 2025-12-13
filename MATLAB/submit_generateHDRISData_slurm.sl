#!/bin/bash -l
#SBATCH --account=def-psaromil
#SBATCH --time=02-00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --array=0-24
#SBATCH --output=/home/alex96/scratch/logs/slurm/MATLAB/job-%j.out
module load matlab/2024b.1
matlab -nojvm -batch "cd('cvx/'); cvx_startup; cd('../'); generateHDRISData"
