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

    def update_gradient(self, grad):
        grad_x, grad_y = grad
        self.gradient_x += grad_x
        self.gradient_y += grad_y

    def __update_bias(self):
        self.wx = -self.gradient_x
        self.wy = -self.gradient_y

    def check_threshold(self, environment):
        x_bee = environment.convert_xy_to_index(self.x)
        y_bee = environment.convert_xy_to_index(self.y)

        concentration_at_bee = environment.concentration_map[int(x_bee), int(y_bee)]
        self.threshold_met = concentration_at_bee > self.threshold

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

    def __generate_random_movement(self):
        return np.random.choice([-1, 0, 1])

    def __clear_gradient(self):
        self.gradient_x = 0
        self.gradient_y = 0

    def update(self):
        self.next_state = None

        # Normalize gradient and update bias
        self.__normalize_gradient()
        self.__update_bias()

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

    def step(self, environment):
        self.state = self.next_state

        if self.state == "random_walk":
            random_sign_x = self.__generate_random_movement()
            random_sign_y = self.__generate_random_movement()

            # Update movement
            self.__update_movement(random_sign_x, random_sign_y, environment)

        elif self.state == "directed_walk":
            self.__update_movement(self.gradient_x, self.gradient_y, environment)

        # Normalize and clear out gradient for timestep
        self.__clear_gradient()

        self.timestep += 1
