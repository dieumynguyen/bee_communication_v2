import h5py
import numpy as np
import glob2
import os
import itertools
import json
from itertools import islice

# All params
Q_list = [0.15]
W_list = [0.15]
D_list = [0.6]
T_list = [0.00001, 0.0001, 0.001, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0]
wb_list = [0.0]
decay_list = [18.0]
seed_list = list(np.arange(0, 25))
n_workers = 140

param_sets = list(itertools.product(Q_list, W_list, D_list, T_list, wb_list, decay_list))

base_exp_dir = "experiments/experiment_0__2019-02-28_10-40-26_n=140"

# Grouping simulation times
sim_time = 8000
time_array = np.arange(0, sim_time)
time_groups = [500, 500, 1000, 2000, 2000, 2000]
it = iter(time_array)
sliced = [list(islice(it, 0, i)) for i in time_groups]

# Grab data
concentration_data = {}
for param in param_sets:
    Q = param[0]
    W = param[1]
    D = param[2]
    T = param[3]
    wb = param[4]
    decay = param[5]
    param_dir = f"Q{Q}_W{W}_D{D}_T{T:0.4f}_wb{wb}_decay{decay}"

    concentration_data[param_dir] = {}
    for trial in seed_list:
        bee_path = os.path.join(base_exp_dir, f"{param_dir}_seed{trial}", "bee_hist.h5")

        print(f"bee_path: {bee_path} \n")

        # Get bee history data
        bee_data = {}
        with h5py.File(bee_path, 'r') as infile:
            for key, val in infile.items():
                bee_data[key] = np.array(val)

        bee_nums = np.unique(bee_data['bee_i'])
        bees = {}
        for bee_num in bee_nums:
            idxs = np.where(bee_data['bee_i']==bee_num)
            bee_x = bee_data['x'][idxs]
            bee_y = bee_data['y'][idxs]
            bee_state = bee_data['state'][idxs]
            distance = bee_data['distance_from_queen'][idxs]
            bee_grads = bee_data['gradient_x'][idxs], bee_data['gradient_y'][idxs]
            concentration = bee_data['concentration'][idxs]
            threshold_met = bee_data['threshold_met'][idxs]
            bias = bee_data['wx'][idxs], bee_data['wy'][idxs]
            bees[bee_num] = {"x" : bee_x, "y" : bee_y, "state": bee_state,
                            "distance": distance, "grads" : bee_grads,
                            "concentration": concentration,
                            "threshold_met" : threshold_met}

        # Extract concentration bee_data
        total_concentration_dict = {}
        for bee_i, bee in enumerate(bees):
            single_bee = bees[bee_i]
            single_bee_state = single_bee['state']
            single_bee_concentration = single_bee['concentration']

            timegroup_dict = {}
            for g_i, g in enumerate(sliced):
                # Filter scenting bees
                state_mask = single_bee_state[g] == 1

                # Accumulate the concentrations - this length will vary
                scenting_concentrations = single_bee_concentration[g][state_mask]

                # Make dictionary of concentrations for a single bee
                timegroup_dict[f'timegroup_{g_i}'] = list(scenting_concentrations)

            total_concentration_dict[f'bee_{bee_i}'] = timegroup_dict

        # Append each trial's data
        trial_str = str(trial)
        concentration_data[param_dir][trial_str] = total_concentration_dict

# Write dictionary to file
with open(f'concentration_data_wb{wb_list[0]}_n{n_workers}.json', 'w') as fp:
    json.dump(concentration_data, fp)
