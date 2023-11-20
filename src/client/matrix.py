from matrix_lite import led
from enums import mic_positions
from asyncio import Queue
import numpy as np
from logger import logger
import asyncio

MIC_QUEUE = Queue()
loop = asyncio.get_event_loop()
default_everloop = ["black"] * led.length


class ThetaSmoother:
    def __init__(self, size=20):
        self.size = size
        self.thetas = []

    def add_theta(self, theta):
        self.thetas.append(theta)
        if len(self.thetas) > self.size:
            self.thetas.pop(0)

    def get_average_theta(self):
        return sum(self.thetas) / len(self.thetas) if self.thetas else 0


# Instantiate the smoother
theta_smoother = ThetaSmoother(
    size=20
)  # Size can be adjusted based on desired smoothing


def scale_strength(strength, min_strength=-45, max_strength=0):
    """
    Scales the strength from a range of -45 dB (or lower) to 0 dB into a range of 0 to 1.
    :param strength: The original strength value in dB.
    :param min_strength: The minimum strength value in dB, corresponding to 0 in the new scale.
    :param max_strength: The maximum strength value in dB, corresponding to 1 in the new scale.
    :return: Scaled strength between 0 and 1.
    """
    # If strength is below the minimum, set it to the minimum
    if strength < min_strength:
        strength = min_strength

    # Scale the strength
    scaled_strength = (strength - min_strength) / (max_strength - min_strength)
    return scaled_strength


def set_leds(theta, strength):
    scaled_strength = scale_strength(strength)
    theta_smoother.add_theta(theta)
    avg_theta = theta_smoother.get_average_theta()
    everloop = default_everloop.copy()
    led_position = get_led_position(avg_theta)
    max_color_value = 255
    led_count = led.length
    try:
        for i in range(led_position - 3, led_position + 4):
            # Handle wrapping around
            index = i % led_count

            # Distance from the central LED
            distance = abs(i - led_position)

            # Calculate the reduction percentage (10% per distance unit)
            reduction_percentage = 0.1 * distance

            # Calculate the color value, adjusting for strength and distance
            color = int(
                (max_color_value - max_color_value * reduction_percentage)
                * scaled_strength
            )

            everloop[index] = {"b": color}
        # logger.debug("Setting LEDs")
        led.set(everloop)
    except Exception as e:
        logger.error(e)


def get_led_position(theta):
    # Normalize theta to be within the range of 0 to 2*pi
    normalized_theta = theta % (2 * np.pi)

    # Scale theta to match the LED range (0 to 35)
    # Since theta = 0 is around LED 17/18, we adjust for this offset
    offset = 17.5  # Adjust this value as needed for precise alignment
    led_position = int(round(led.length * normalized_theta / (2 * np.pi) + offset))

    # Wrap around if the position exceeds 35
    led_position = led_position % led.length

    return led_position


def clear_leds():
    led.set(default_everloop)
