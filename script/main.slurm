#!/bin/bash
#SBATCH -p short
#SBATCH --job-name=job_1
#SBATCH --mail-type=NONE
#SBATCH --mail-user=ding1018@colorado.edu
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --mem=500gb
#SBATCH --time=05:00:00
#SBATCH --output=/eofiles_distance/slurm_test_%j.out
#SBATCH --error=/eofiles_distance/slurm_test_%j.err
module load python/3.6.3
python grab_distance_data.py
