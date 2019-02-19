import numpy as np
import h5py

class BeeKeeper(object):
    def __init__(self, params):
        self.__set_params(params)

        self.environment_history = []
        self.bee_history = {
            "t"                  : [],
            "bee_i"              : [],
            "x"                  : [],
            "y"                  : [],
            "state"              : [],
            "gradient_x"         : [],
            "gradient_y"         : [],
            "wx"                 : [],
            "wy"                 : [],
            "distance_from_queen": [],
            "concentration"      : [],
            "threshold_met"      : []
        }

        states = ["random_walk_pre", "emit", "wait", "directed_walk", "random_walk_post"]
        self.state_encoding = { state : i for i, state in enumerate(states) }

    def __set_params(self, params):
        for key, val in params.items():
            self.__dict__[key] = val

    def measure_environment(self, environment):
        if self.sleeping:
            return
        self.environment_history.append(environment.concentration_map)

    def measure_bees(self, bee, queen, global_i):
        if self.sleeping:
            return

        dist = np.sqrt( (bee.x - queen.x)**2 + (bee.y - queen.y)**2 )
        bee_info = {
            "t"                  : global_i,
            "bee_i"              : bee.num,
            "x"                  : bee.x,
            "y"                  : bee.y,
            "state"              : self.state_encoding[bee.state],
            "gradient_x"         : bee.gradient_x,
            "gradient_y"         : bee.gradient_y,
            "wx"                 : bee.wx,
            "wy"                 : bee.wy,
            "distance_from_queen": dist,
            "concentration"      : bee.total_C,
            "threshold_met"      : bee.threshold_met
        }
        self.__update_bee_history(bee_info)

    def __update_bee_history(self, bee_info):
        for key, val in bee_info.items():
            self.bee_history[key].append(val)

    def __write_environment_data(self):
        with h5py.File(self.environment_path, 'w') as outfile:
            outfile.create_dataset("concentration", data=self.environment_history)

    def __write_bee_data(self):
        with h5py.File(self.bee_path, 'w') as outfile:
            for key, val in self.bee_history.items():
                outfile.create_dataset(key, data=val)

    def log_data_to_handy_dandy_notebook(self):
        if self.sleeping:
            return

        self.__write_environment_data()
        self.__write_bee_data()
