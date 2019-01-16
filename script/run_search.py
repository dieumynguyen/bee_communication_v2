import glob2
from subprocess import call
from datetime import datetime
import argparse
import os

def setup_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=int, default=0, help='Debugging Mode')
    return parser.parse_args()

def create_experiment_dir(base_dir):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    num_experiments = len(glob2.glob(f"{base_dir}/*"))

    # create primary experiments dir
    current_experiment_parent_dir = os.path.join(base_dir, f"experiment_{num_experiments+1}__{timestamp}")
    os.makedirs(current_experiment_parent_dir)

    return current_experiment_parent_dir

def run_cfg_generator():
    call(["python", "make_config_files.py"])

def create_slurm_script(cfg_i, experiment_dir, config_file_path):

    slurm_path = "main.slurm"
    job_name = f"job_{cfg_i}"
    num_nodes = 1
    num_tasks = 48
    mail_type = "FAIL"
    email_address = "ding1018@colorado.edu"
    runtime = "05:00:00"
    partition = "short"
    memory_limit = "500gb"
    outfile_path = "/scratch/Users/ding1018/sweet_5_optimalT/eofiles_main/slurm_test_%j.out"
    errfile_path = "/scratch/Users/ding1018/sweet_5_optimalT/eofiles_main/slurm_test_%j.err"

    with open(slurm_path, "w") as outfile:
        outfile.write("#!/bin/bash\n")
        outfile.write(f"#SBATCH -p {partition}\n") # Partition to submit to
        outfile.write(f"#SBATCH --job-name={job_name}\n") # Job's name
        outfile.write(f"#SBATCH --mail-type={mail_type}\n") # Mail type
        outfile.write(f"#SBATCH --mail-user={email_address}\n") # Email
        outfile.write(f"#SBATCH --nodes={num_nodes}\n") # Number of nodes
        outfile.write(f"#SBATCH --ntasks={num_tasks}\n") # Number of tasks
        outfile.write(f"#SBATCH --mem={memory_limit}\n") # Memory per cpu in MB (see also --mem)
        outfile.write(f"#SBATCH --time={runtime}\n") # Runtime
        outfile.write(f"#SBATCH --output={outfile_path}\n") # stddout path
        outfile.write(f"#SBATCH --error={errfile_path}\n") # stderr file path

        outfile.write(f"module load python/3.6.3\n") #
        outfile.write(f"python main.py --base_dir {experiment_dir} --file {config_file_path}\n") #

    return slurm_path

def run_search(cfg_file_dir, py_file, experiment_dir, opts):
    cfg_files = glob2.glob(f"{cfg_file_dir}/*")

    if opts.d:
        print("** Debugging Mode **")
        cfg_files = cfg_files[:2]

    for cfg_i, cfg_file in enumerate(cfg_files):
        slurm_path = create_slurm_script(cfg_i, experiment_dir, cfg_file)
        #call(["sbatch", slurm_path])
        call(["python", f"{py_file}", "--save_folder", f"{experiment_dir}", "--file", f"{cfg_file}"])

if __name__ == '__main__':
    # Use argparse to check if debugging mode enabled
    opts = setup_opts()

    cfg_file_dir = "experiment_cfg_files"
    py_file = "main.py"
    base_dir = "experiments"

    # Create cfg files
    run_cfg_generator()

    # Create experiment directory
    experiment_dir = create_experiment_dir(base_dir)
    try:
        run_search(cfg_file_dir, py_file, experiment_dir, opts)
    except KeyboardInterrupt:
        print("\nCancelling experiments.")
    except Exception as e:
        print("\n ** Exception Occurred")
        print(e)
