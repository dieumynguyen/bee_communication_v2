import warnings
warnings.filterwarnings("ignore")
import os
import sys
import numpy as np
import glob2
import h5py
import matplotlib.pyplot as plt
import cv2
plt.rcParams["font.family"] = "Arial"

experiment_path = "experiment_1__2019-02-18_11-20-18"
trial_path = "Q0.15_W0.15_D0.6_T0.02500_wb0.0_decay18.0_seed24"
base_exp_dir = f"experiments/{experiment_path}/{trial_path}"

############# Functions
def read_config(base_exp_dir):
    cfg_path = glob2.glob(f"config/files/*.cfg")[4]
    cfg_path, os.path.exists(cfg_path)

    with open(cfg_path, "r") as infile:
        lines = [line.split() for line in infile]
        cfg_opts = {}
        for key, val in lines:
            key = key.replace('--', '')

            try:
                val = float(val)
            except:
                try:
                    val = int(val)
                except:
                    if val.startswith("T"):
                        val = True
                    elif val.startswith("F"):
                        val = False
                    pass
            cfg_opts[key] = val
    return cfg_opts


def imgs2vid(imgs, outpath, fps=4):
    height, width, layers = imgs[0].shape
    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    video = cv2.VideoWriter(outpath, fourcc, fps, (width, height), True)

    for img in imgs:
        video.write(img)

    cv2.destroyAllWindows()
    video.release()

############# Run
script_config = read_config(base_exp_dir)
X_MIN = script_config['x_min']
X_MAX = script_config['x_max']
DX = script_config['dx']
GRID_SIZE = np.arange(X_MIN, X_MAX+DX, DX).shape[0]
convert_xy_to_index = lambda xy: ((xy - X_MIN) / (X_MAX - X_MIN)) * GRID_SIZE

ipynb_dev_config = False
if not ipynb_dev_config:
    env_path = os.path.join(base_exp_dir, "envir_hist.h5")
    bee_path = os.path.join(base_exp_dir, "bee_hist.h5")
    print(os.path.exists(env_path), os.path.exists(bee_path), env_path)
else:
    base_exp_dir = "./"
    env_path = os.path.join(base_exp_dir, "envir_hist.h5")
    bee_path = os.path.join(base_exp_dir, "bee_hist.h5")
    print(os.path.exists(env_path), os.path.exists(bee_path), env_path)

# Concentration maps
with h5py.File(env_path, 'r') as infile:
    cmaps = np.array(infile['concentration'])

# Min and max concentrations for heatmap
min_c = np.min(cmaps[:])
max_c = np.max(cmaps[:]) * 0.8

# Bee measurements
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

# Make frames
colors = ["red", "gray", "#479030", "orange", "blue"]
color_decoder = {
    0: colors[1],
    1: colors[2],
    2: colors[2],
    3: colors[3],
    4: colors[4]
}
TIME = cmaps.shape[0]
savepath = ""
for frame_i in range(cmaps.shape[0]):
    sys.stdout.write(f"\rFrame {frame_i+1}/{TIME}")
    sys.stdout.flush()

    # CONCENTRATION
    cmap = cmaps[frame_i]
    plt.imshow(cmap, cmap='Greens', vmin=min_c, vmax=max_c)
    plt.colorbar(shrink=0.8, format='%.2f')

    # QUEEN
    queen = convert_xy_to_index(0)
    plt.scatter(queen, queen, c="red", s=100, edgecolors='black', marker='o')

    # WORKERS
    for bee_key, bee_vals in bees.items():
        x = bee_vals['x'][frame_i]
        y = bee_vals['y'][frame_i]
        state = bee_vals['state'][frame_i]
        color = color_decoder[state]
        plt.scatter(convert_xy_to_index(x), convert_xy_to_index(y),
                    color=color, s=30, edgecolors='black')

    # FORMATTING
    texts = ["Queen", "Random walk pre-scenting", "Scenting", "Directed walk", "Random walk post-scenting"]
    patches = [ plt.plot([],[], marker="o", ms=5, ls="", mec=None, color=colors[i],
                markeredgecolor="black", label="{:s}".format(texts[i]) )[0]  for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(0.5, -0.22),
               loc='center', ncol=2, numpoints=1, labelspacing=0.3,
               fontsize='small', fancybox="True",
               handletextpad=0, columnspacing=0)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.xlim(0, 600)
    plt.ylim(600, 0)

    if ipynb_dev_config:
        plt.title(f"Q{QUEEN_BEE_A}_W{WORKER_BEE_A}_D{D}_T{THRESHOLD}_wb{WB}_decay{DECAY}_seed{SEED} \n t: {frame_i+1}/{TIME-1}")
    else:
        num_timesteps = np.arange(script_config['t_min'], script_config['t_max']+script_config['dt'], script_config['dt']).shape[0]
        Q = script_config['queen_initial_concentration']
        W = script_config['worker_initial_concentration']
        D = script_config['diffusion_coefficient']
        T = script_config['worker_threshold']
        wb = int(script_config['worker_bias_scalar'])
        decay = int(script_config['decay'])
        seed = int(script_config['random_seed'])
        title = f"Q{Q}_W{W}_D{D}_T{T:0.5f}_wb{wb}_decay{decay}"
        savepath = f"{title}_seed{seed}.mp4"
        plt.title(f"{title} \n t: {frame_i+1}/{TIME}")

    # SAVING FRAMES
    file_path = f't{frame_i+1:04d}.png'
    filename = f'movie_frames/{file_path}'
    plt.savefig(filename, bbox_inches='tight', dpi=100)
    plt.close()

####### Stitching FRAMES
all_img_paths = np.sort(glob2.glob("movie_frames/*.png"))
all_imgs = np.array([cv2.imread(img) for img in all_img_paths])

savepath = f"movie_frames/{savepath}"
imgs2vid(all_imgs, savepath)
