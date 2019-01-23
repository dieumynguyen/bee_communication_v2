import numpy as np

config_opts = {
    "verbose"     : True,
    "random_seed" : [1,2,3,4,5],
    ### ENVIRONMENT PARAMS ###
    "x_min" : -3,
    "x_max" : 3,
    "dx" : 0.01,
    "t_min" : 0,
    "t_max" : 15,    # 10 for dt=0.05
    "dt" : 0.05,
    "decay" : [18.0],
    "diffusion_coefficient" : [0.6],

    ### QUEEN PARAMS ###
    "queen_x" : 0,
    "queen_y" : 0,
    "queen_bias_scalar" : 0.0,
    "queen_emission_frequency" : 4,
    "queen_initial_concentration" : 0.15,

    ### WORKER PARAMS ###
    "num_workers" : 70,
    "worker_threshold" : [0.01],
    "worker_bias_scalar" : [5.0],
    "worker_wait_period" : 4,
    "worker_step_size" : 0.05,
    "worker_initial_concentration" : [0.15],
    "worker_trans_prob" : 0.5,
    "enable_probabilistic" : True,
    "sensitivity_mode"  : "none",

    "space_constraint" : 0.85,
    "t_threshold" : 100,

    "measurements_on" : True
}
