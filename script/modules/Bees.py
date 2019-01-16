import numpy as np

class Queen(object):
    def __init__(self, params):
        self.__set_params(params)
        self.state = "emit"
        self.timestep = 0
        self.wx = 0
        self.wy = 0
        self.gradient_x = 0
        self.gradient_y = 0

    def __set_params(self, params):
        for key, val in params.items():
            self.__dict__[key] = val

    def update(self):
        self.state = "emit" if self.timestep % self.emission_frequency == 0 else "wait"

    def step(self):
        self.timestep += 1

class Worker(object):
    def __init__(self, params):
        self.__set_params(params)
        self.__init_position()
        self.__init_conditions()

    def __set_params(self, params):
        for key, val in params.items():
            self.__dict__[key] = val

    def __init_position(self):
        lower_bound = self.x_min*self.init_stddev
        upper_bound = self.x_max*self.init_stddev

        self.x = np.random.uniform(lower_bound, upper_bound)
        self.y = np.random.uniform(lower_bound, upper_bound)

    def __init_conditions(self):
        # Counters
        self.timestep = 0
        self.wait_timestep = 0

        # Grads
        self.gradient_x = 0
        self.gradient_y = 0

        self.sensations = []

        self.wx = 0
        self.wy = 0

        # Flags
        self.threshold_met = False

        # State
        self.state = "random_walk"

    def __normalize_gradient(self):
        d = np.linalg.norm([self.gradient_x, self.gradient_y])
        self.gradient_x = self.gradient_x / (d + 1e-9)
        self.gradient_y = self.gradient_y / (d + 1e-9)

    def sense_environment(self, t_i, environment, pheromone_src, pheromone_src_C):
        # Calculate Gradient
        # ------------------------------------------------------------------------
        grad = environment.calculate_gradient(t_i, self.x, self.y, pheromone_src)
        # ------------------------------------------------------------------------

        # Calculate concentration at bee.x, bee.y given individual pheromone src
        # ------------------------------------------------------------------------
        x_bee = environment.convert_xy_to_index(self.x)
        y_bee = environment.convert_xy_to_index(self.y)
        concentration_at_bee = pheromone_src_C[int(x_bee), int(y_bee)]
        # ------------------------------------------------------------------------

        # Update bee's sensation
        sensation = {"bee_i" : pheromone_src['bee_i'], "C" : concentration_at_bee, "grad" : grad}
        self.sensations.append(sensation)

    def __update_gradient(self, grad):
        grad_x, grad_y = grad
        self.gradient_x += grad_x
        self.gradient_y += grad_y

    def __update_bias(self):
        self.wx = -self.gradient_x
        self.wy = -self.gradient_y

    def __check_arena_boundary(self, environment, dim):
        return environment.x_min < dim < environment.x_max

    def __update_movement(self, dx, dy, environment):
        next_x = self.x + self.step_size * dx
        next_y = self.y + self.step_size * dy

        move_in_x = self.__check_arena_boundary(environment, next_x)
        move_in_y = self.__check_arena_boundary(environment, next_y)

        if move_in_x:
            self.x = next_x

        if move_in_y:
            self.y = next_y

    def __check_threshold_met(self):
        if self.total_C > self.threshold:
            self.threshold_met = True
            self.__update_gradient(self.total_grads)
            self.__normalize_gradient()
            self.__update_bias()
        else:
            self.threshold_met = False

    def update(self):
        """
            Three modes:
                1. No distinction between any bees (e.g., pheromones from queen are treated equal to workers)
                2. Distinction between queen and workers
                3. Distinction between queen and workers, as well as distinction between workers
        """
        if self.sensitivity_mode == 'none':
            self.__determine_sensation_effects__mode_1()
        elif self.sensitivity_mode == 'queen_worker':
            # 2. Distinction between queen and workers
            self.__determine_sensation_effects__mode_2()
        elif self.sensitivity_mode == 'all':
            # 3. Distinction between queen and workers, as well as distinction between workers
            self.__determine_sensation_effects__mode_3()

        self.__check_threshold_met()

        self.__update_state()

    def __determine_sensation_effects__mode_1(self):
        """
            # 1. No distinction between any bees (e.g., pheromones from queen are treated equal to workers)
        """
        self.total_C = 0
        self.total_grads = np.array([0.0, 0.0])
        for sensation in self.sensations:
            self.total_C += sensation['C']
            self.total_grads += np.array(sensation['grad'])

    def __determine_sensation_effects__mode_2(self):
        """
            2. Distinction between queen and workers
               - A. Check queen concentration - if > threshold,
        """
        queen_C = 0
        queen_grads = np.array([0.0, 0.0])

        worker_C = 0
        worker_grads = np.array([0.0, 0.0])
        for sensation in self.sensations:
            bee_i = sensation['bee_i']

            # Queen
            if bee_i == -1:
                queen_C += sensation['C']
                queen_grads += np.array(sensation['grads'])
            # Workers
            else:
                worker_C += sensation['C']
                worker_grads += np.array(sensation['grads'])

        self.total_C = 0
        self.total_grads = np.array([0.0, 0.0])

        # Queen
        if queen_C > self.threshold:
            self.total_C += queen_C
            self.total_grads += queen_grads
        if worker_C > self.threshold:
            self.total_C += worker_C
            self.total_grads += worker_grads

    def __determine_sensation_effects__mode_3(self):
        """
            3. Distinction between queen and workers, as well as distinction between workers
        """
        combined_sensations = {}
        for sensation in self.sensations:
            bee_i = sensation['bee_i']
            if bee_i in combined_sensations:
                combined_sensations[bee_i]['C'] += sensation['C']
                combined_sensations[bee_i]['grads'] += np.array(sensation['grads'])
            else:
                combined_sensations[bee_i] = {
                    "C"     : sensation['C'],
                    "grads" : np.array(sensation['grads'])
                }

        self.total_C = 0
        self.total_grads = np.array([0.0, 0.0])
        for sensation in combined_sensations.values():
            if sensation['C'] > self.threshold:
                self.total_C += sensation['C']
                self.total_grads += np.array(sensation['grads'])

    def __update_state(self):
        self.next_state = None
        if self.state == "random_walk":
            if self.threshold_met:
                self.next_state = "wait"
                self.wait_timestep = 0

        elif self.state == "wait":
            if self.wait_timestep == 0:
                self.next_state = "emit"
            elif self.wait_timestep > self.wait_period:
                self.next_state = "directed_walk"
            self.wait_timestep +=1

        elif self.state == "emit":
            if self.wait_timestep > self.wait_period:
                self.next_state = "directed_walk"
            elif 0 < self.wait_timestep <= self.wait_period:
                self.next_state = "wait"
            self.wait_timestep += 1

        elif self.state == "directed_walk":
            if self.threshold_met:
                if self.probabilistic:
                    random_draw = np.random.uniform(0, 1)
                    if random_draw < self.trans_prob:
                        self.next_state = "wait"
                        self.wait_timestep = 0
                else:
                    self.next_state = "wait"
                    self.wait_timestep = 0

        # Check for case where state hasnt't changed
        if self.next_state is None:
            self.next_state = self.state

    def __clear(self):
        self.gradient_x = 0
        self.gradient_y = 0
        self.sensations = []

    def step(self, environment):
        self.state = self.next_state

        if self.state == "random_walk":
            random_sign_x = np.random.choice([-1, 0, 1])
            random_sign_y = np.random.choice([-1, 0, 1])

            # Update movement
            self.__update_movement(random_sign_x, random_sign_y, environment)

        elif self.state == "directed_walk":
            self.__update_movement(self.gradient_x, self.gradient_y, environment)

        # Normalize and clear out gradient for timestep
        self.__clear()

        self.timestep += 1
