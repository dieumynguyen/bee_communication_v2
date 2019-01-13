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

def run_search(cfg_file_dir, py_file, experiment_dir, opts):
    cfg_files = glob2.glob(f"{cfg_file_dir}/*")

    if opts.d:
        print("** Debugging Mode **")
        cfg_files = cfg_files[:2]

    for cfg_file in cfg_files:
        call(["python", f"{py_file}", "--base_dir", f"{experiment_dir}", "--file", f"{cfg_file}"])

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
