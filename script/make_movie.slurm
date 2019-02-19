#!/bin/bash
#SBATCH -p short
#SBATCH --job-name=honeybee_movie
#SBATCH --mail-type=NONE
#SBATCH --mail-user=ding1018@colorado.edu
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --mem=500gb
#SBATCH --time=24:00:00
#SBATCH --output=/scratch/Users/ding1018/bee_model_3/eofiles_movie/slurm_test_%j.out
#SBATCH --error=/scratch/Users/ding1018/bee_model_3/eofiles_movie/slurm_test_%j.err

pwd; hostname; date

module load python/3.6.3

python /scratch/Users/ding1018/bee_model_3/make_movie.py

date
