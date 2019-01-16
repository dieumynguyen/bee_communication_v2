import glob
from subprocess import call
from datetime import datetime
import argparse
import os

BASE_DIRS = {
    "local"  : "",
    "server" : "/scratch/Users/ding1018/bee_model"
}

CFG_FILE_DIR = "experiment_cfg_files"
PY_FILE = "main.py"
BASE_EXPERIMENT_DIR = "experiments"

def setup_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=int, default=0, help='Debugging Mode')
    parser.add_argument('--location', type=str, default='local', help='local or server')
    parser.add_argument('--nodes', type=int, default=1, help='num nodes')
    parser.add_argument('--ntasks', type=int, default=48, help='num tasks')
    parser.add_argument('--mem', type=int, default=500, help='memory limit (GB)')
    parser.add_argument('--time', type=int, default=5, help='time limit (hrs)')
    parser.add_argument('--partition', type=str, default="short", help='partition type')
    return parser.parse_args()

def create_experiment_dir(base_dir):
    experiment_dir = os.path.join(base_dir, BASE_EXPERIMENT_DIR)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    num_experiments = len(glob.glob(f"{experiment_dir}/*"))

    # create primary experiments dir
    current_experiment_parent_dir = os.path.join(experiment_dir, f"experiment_{num_experiments+1}__{timestamp}")
    os.makedirs(current_experiment_parent_dir)

    return current_experiment_parent_dir

def run_cfg_generator(base_dir):
    cfg_files_dir = os.path.join(base_dir, "config", "files")
    script_path = os.path.join(base_dir, "config", "make_config_files.py")
    call(["python", script_path, "--config_dir", cfg_files_dir])

    return cfg_files_dir

def create_slurm_script(base_dir, cfg_i, experiment_dir, config_file_path, opts):

    slurm_output_file_dir = os.path.join(base_dir, "eofiles_main")
    if not os.path.exists(slurm_output_file_dir):
        os.makedirs(slurm_output_file_dir)

    slurm_path = os.path.join(base_dir, "main.slurm")
    job_name = f"job_{cfg_i}"
    num_nodes = opts.nodes
    num_tasks = opts.ntasks
    memory_limit = "{opts.mem}gb"
    runtime = f"{opts.time:02d}:00:00"
    partition = opts.partition

    mail_type = "FAIL"
    email_address = "ding1018@colorado.edu"

    outfile_path = os.path.join(slurm_output_file_dir, "/slurm_test_%j.out")
    errfile_path = os.path.join(slurm_output_file_dir, "/slurm_test_%j.err")

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

def run_search(base_dir, cfg_files_dir, experiment_dir, opts):

    cfg_files = glob.glob(f"{cfg_files_dir}/*")

    if opts.d:
        print("** Debugging Mode **")
        cfg_files = cfg_files[:2]

    for cfg_i, cfg_file in enumerate(cfg_files):
        print(f"\n{cfg_file}\n")

        if opts.location == 'local':
            call(["python", f"{PY_FILE}", "--save_folder", f"{experiment_dir}", "--file", f"{cfg_file}"])
        elif opts.location == 'server':
            slurm_path = create_slurm_script(base_dir, cfg_i, experiment_dir, cfg_file, opts)
            call(["sbatch", slurm_path])

if __name__ == '__main__':
    # Use argparse to check if debugging mode enabled
    opts = setup_opts()

    # Set base dir
    base_dir = BASE_DIRS[opts.location]

    # Create cfg files
    cfg_files_dir = run_cfg_generator(base_dir)

    # Create experiment directory
    experiment_dir = create_experiment_dir(base_dir)

    try:
        run_search(base_dir, cfg_files_dir, experiment_dir, opts)
    except KeyboardInterrupt:
        print("\nCancelling experiments.")
    except Exception as e:
        print("\n ** Exception Occurred")
        print(e)
