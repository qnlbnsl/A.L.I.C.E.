import numpy as np


class ThetaSmoother:
    def __init__(self, size=10):
        self.size = size
        self.thetas = []

    def add_theta(self, theta):
        # discard values that are more than 20 degrees from the mean. Allow all values if there are less than 10 values.
        if np.abs(np.mean(self.thetas) - theta) <= 20 or len(self.thetas) < 10:
            self.thetas.append(theta)
        if len(self.thetas) > self.size:
            self.thetas.pop(0)

    def get_theta(self):
        if not self.thetas:
            return 0
        return np.mean(self.thetas)

