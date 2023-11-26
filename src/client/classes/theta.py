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
        # # Convert to numpy array for ease of calculation
        # theta_array = np.array(self.thetas)

        # # Calculate mean and standard deviation
        # mean_theta = np.mean(theta_array)
        # std_theta = np.std(theta_array)

        # # Filter out values that are more than 2 standard deviations from the mean
        # filtered_thetas = theta_array[np.abs(theta_array - mean_theta) < 20]

        # # Return the average of the filtered values
        # return np.mean(filtered_thetas) if len(filtered_thetas) > 0 else mean_theta
