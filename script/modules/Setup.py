import argparse
import os
import shutil
from datetime import datetime

import modules.Environment as Environment
import modules.Bees as Bees
import modules.BeeKeeper as BeeKeeper

def config_options():
    class LoadFromFile(argparse.Action):
        def __call__(self, parser, namespace, values, option_sting=None):
            with values as f:
                parser.parse_args(f.read().split(), namespace)
                setattr(namespace, 'config_file', values.name)

    # Instantiate parser
    parser = argparse.ArgumentParser()

    # Setup arguments
    parser.add_argument("--verbose", type=bool, default=True)
    parser.add_argument("--random_seed", type=int, default=80)
    parser.add_argument("--x_min", type=float, default=-3)
    parser.add_argument("--x_max", type=float, default=3)
    parser.add_argument("--dx", type=float, default=0.01)
    parser.add_argument("--t_min", type=float, default=0)
    parser.add_argument("--t_max", type=float, default=10)
    parser.add_argument("--dt", type=float, default=0.05)
    parser.add_argument("--decay", type=float, default=18.0)
    parser.add_argument("--diffusion_coefficient", type=float, default=0.25)
    parser.add_argument("--queen_x", type=float, default=0)
    parser.add_argument("--queen_y", type=float, default=0)
    parser.add_argument("--queen_bias_scalar", type=float, default=0.0)
    parser.add_argument("--queen_emission_frequency", type=float, default=20)
    parser.add_argument("--queen_initial_concentration", type=float, default=0.15)
    parser.add_argument("--num_workers", type=int, default=70)
    parser.add_argument("--worker_threshold", type=float, default=0.010)
    parser.add_argument("--worker_bias_scalar", type=float, default=5.0)
    parser.add_argument("--worker_wait_period", type=int, default=20)
    parser.add_argument("--worker_step_size", type=float, default=0.05)
    parser.add_argument("--worker_initial_concentration", type=float, default=0.15)
    parser.add_argument("--worker_trans_prob", type=float, default=1.0)
    parser.add_argument("--culling_threshold", type=float, default=0.0001)
    parser.add_argument("--sensitivity_mode", type=str, default='none')
    parser.add_argument("--enable_probabilistic", type=bool, default=False)
    parser.add_argument("--space_constraint", type=float, default=0.85)
    parser.add_argument("--t_threshold", type=float, default=100)
    parser.add_argument("--measurements_on", type=bool, default=False)
    parser.add_argument("--file", type=open, action=LoadFromFile)

    # Separate
    parser.add_argument("--experiment_folder", type=str, default="experiments")

    # Read arguments from parser
    args = parser.parse_args()

    return args

def directory(config):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if not hasattr(config, 'config_file'):
        cfg_name = 'test'
    else:
        cfg_name = config.config_file.split(os.path.sep)[-1].replace('.cfg', '')

    # model_dir = os.path.join(config.experiment_folder, f"cfg__{cfg_name}__{timestamp}")
    # Show params on folder title
    Q = config.queen_initial_concentration
    W = config.worker_initial_concentration
    D = config.diffusion_coefficient
    T = config.worker_threshold
    wb = config.worker_bias_scalar
    decay = config.decay
    seed = config.random_seed
    params_name = f"Q{Q}_W{W}_D{D}_T{T:0.4f}_wb{wb}_decay{decay}_seed{seed}"
    model_dir = os.path.join(config.experiment_folder, f"{params_name}")

    os.makedirs(model_dir)

    # Add config file to model dir
    if hasattr(config, 'config_file'):
        shutil.copyfile(config.config_file, os.path.join(model_dir, f"{cfg_name}.cfg"))

    return model_dir

def world_parameters(cfg, model_dir):
    bee_keeper_params = {
        "bee_path"         : os.path.join(model_dir, "bee_hist.h5"),
        "environment_path" : os.path.join(model_dir, "envir_hist.h5"),
        "sleeping"         : not cfg.measurements_on
    }

    environment_params = {
        "x_min"      : cfg.x_min,
        "x_max"      : cfg.x_max,
        "dx"         : cfg.dx,
        "t_min"      : cfg.t_min,
        "t_max"      : cfg.t_max,
        "dt"         : cfg.dt,
        "D"          : cfg.diffusion_coefficient,
        "decay_rate" : cfg.decay,
        "culling_threshold" : cfg.culling_threshold
    }

    queen_params  = {
        "num"                : -1,
        "x"                  : cfg.queen_x,
        "y"                  : cfg.queen_y,
        "A"                  : cfg.queen_initial_concentration,
        "wb"                 : cfg.queen_bias_scalar,
        "emission_frequency" : cfg.queen_emission_frequency,
    }

    bee_params = {
        "x_min"            : cfg.x_min,
        "x_max"            : cfg.x_max,
        "init_stddev"      : cfg.space_constraint,
        "A"                : cfg.worker_initial_concentration,
        "threshold"        : cfg.worker_threshold,
        "wb"               : cfg.worker_bias_scalar,
        "wait_period"      : cfg.worker_wait_period,
        "step_size"        : cfg.worker_step_size,
        "probabilistic"    : cfg.enable_probabilistic,
        "trans_prob"       : cfg.worker_trans_prob,
        "sensitivity_mode" : cfg.sensitivity_mode
    }

    world_params = {
        "bee_keeper" : bee_keeper_params,
        "environment" : environment_params,
        "queen" : queen_params,
        "worker" : bee_params
    }

    return world_params

def create_bees(cfg, bee_params):
    bees = []
    for bee_i in range(cfg.num_workers):
        bee_params = bee_params
        bee_params["num"] = bee_i
        bee = Bees.Worker(bee_params)
        bees.append(bee)
    return bees

def world_objects(cfg_options, world_params):
    environment = Environment.Environment(world_params["environment"])
    queen_bee = Bees.Queen(world_params["queen"])
    bees = create_bees(cfg_options, world_params["worker"])
    bee_keeper = BeeKeeper.BeeKeeper(world_params["bee_keeper"])

    world_objs = {
        "environment" : environment,
        "queen_bee" : queen_bee,
        "bees" : bees,
        "bee_keeper" : bee_keeper
    }

    return world_objs
