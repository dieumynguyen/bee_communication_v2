#!/bin/bash
#SBATCH -p short
#SBATCH --job-name=job_1
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ding1018@colorado.edu
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --mem=500gb
#SBATCH --time=05:00:00
#SBATCH --output=/scratch/Users/ding1018/sweet_5_optimalT/eofiles_main/slurm_test_%j.out
#SBATCH --error=/scratch/Users/ding1018/sweet_5_optimalT/eofiles_main/slurm_test_%j.err
module load python/3.6.3
python main.py --base_dir experiments\experiment_7__2019-01-16_16-03-30 --file config\files\exp_2.cfg
