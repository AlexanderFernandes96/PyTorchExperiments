#!/bin/bash
#SBATCH --account=def-psaromil
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --array=0-24
#SBATCH --time=01-00:00 # days-hours:minutes
#SBATCH --output=/home/alex96/scratch/logs/slurm/job-%j.out
#SBATCH --error=/home/alex96/scratch/logs/slurm/job-%j.out
#SBATCH --mail-user=alexander.fernandes@mail.mcgill.ca
#SBATCH --mail-type=ALL
printf "%s\n" "-----------------------------------"
printf "%s\n" "running generateHDRISData.m"
printf "%s\n" "-----------------------------------"
module load matlab/2024b.1
matlab -batch "generateHDRISData"
printf "%s\n" "--------"
printf "%s\n" "finished"
printf "%s\n" "--------"

