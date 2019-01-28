import h5py
import numpy as np
import glob2
import os
import itertools
import json

# All params
Q_list = [0.15]
W_list = [0.15]
D_list = [0.6]
T_list = [0.0001, 0.001, 0.01, 0.1, 1.0]
wb_list = [5.0]
decay_list = [18.0]
seed_list = [0, 5, 10, 15, 20]

param_sets = list(itertools.product(Q_list, W_list, D_list, T_list, wb_list, decay_list))

base_exp_dir = "experiments/experiment_2__2019-01-27_23-22-55/"

distance_data = {}
for param in param_sets:
    Q = param[0]
    W = param[1]
    D = param[2]
    T = param[3]
    wb = param[4]
    decay = param[5]
    param_dir = f"Q{Q}_W{W}_D{D}_T{T:0.4f}_wb{wb}_decay{decay}"

    distance_data[param_dir] = {}
    for trial in seed_list:
        bee_path = os.path.join(base_exp_dir, f"{param_dir}_seed{trial}", "bee_hist.h5")

        # Get distance data
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
            bias = bee_data['wx'][idxs], bee_data['wy'][idxs]
            bees[bee_num] = {"x" : bee_x, "y" : bee_y, "state": bee_state,
                            "distance": distance, "grads" : bee_grads}
        # Extract distance
        num_bees = np.unique(bee_data['bee_i']).shape[0]
        distances_per_t = bee_data['distance_from_queen'].reshape(-1, num_bees)
        median_distances = list(np.mean(distances_per_t, axis=1))

        distance_data[param_dir][trial] = median_distances

# Write dictionary to file
with open('distance_data.json', 'w') as fp:
    json.dump(distance_data, fp)
