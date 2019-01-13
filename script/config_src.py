import numpy as np

config_opts = {
    "verbose"     : True,
    "random_seed" : 80,
    ### ENVIRONMENT PARAMS ###
    "x_min" : -3,
    "x_max" : 3,
    "dx" : 0.01,
    "t_min" : 0,
    "t_max" : 1,    # 10 for dt=0.05
    "dt" : 0.05,
    "decay" : [18.0],
    "diffusion_coefficient" : [0.25, 0.5, 0.60, 1.0],

    ### QUEEN PARAMS ###
    "queen_x" : 0,
    "queen_y" : 0,
    "queen_bias_scalar" : 0.0,
    "queen_emission_frequency" : 20,
    "queen_initial_concentration" : 0.15,

    ### WORKER PARAMS ###
    "num_workers" : 70,
    "worker_threshold" : [0.010],
    "worker_bias_scalar" : [5.0],
    "worker_wait_period" : 20,
    "worker_step_size" : 0.05,
    "worker_initial_concentration" : [0.15],
    "worker_trans_prob" : 1.0,
    "enable_probabilistic" : False,

    "space_constraint" : 0.85,
    "t_threshold" : 100,

    "save_folder" : "experiments",
    "measurements_on" : True
}
