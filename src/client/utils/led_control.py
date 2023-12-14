import math
from matrix_lite import led

# from enums import mic_positions
import numpy as np
import time

from logger import logger


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


default_everloop = ["black"] * led.length

# Angular span for each LED
angular_span = 2 * np.pi / led.length

# Instantiate the smoother
theta_smoother = ThetaSmoother(
    size=10
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

    everloop = default_everloop.copy()
    led_position = map_theta_to_led(theta)
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
        # MIC_QUEUE.put_nowait((theta, led_position, time.time()))
        led.set(everloop)
    except Exception as e:
        logger.error(e)


def map_theta_to_led(theta):
    # Normalize theta to [0, 2π] range
    theta_normalized = theta % (2 * np.pi)

    # Calculate the LED number
    # Since LED 35 is at π, we adjust the range to [-π, π] before mapping
    led_number = int(((theta_normalized - np.pi) + angular_span / 2) // angular_span)

    # Adjust for LED numbering
    led_number = (led_number + led.length) % led.length + 1

    return led_number


def clear_leds():
    led.set(default_everloop)


def retry_connection_led(retry_delay=5):
    # clear_leds()
    everloop = default_everloop.copy()
    steps = 100  # Number of steps in the animation

    for i in range(steps):
        # Calculate the strength using a sine wave for the breathing effect
        # Sine wave completes a half cycle (0 to pi) over the steps
        strength = math.sin(i / steps * math.pi)  # Ranges from 0 to 1

        everloop = [{"r": int(160 * strength)}] * led.length
        led.set(everloop)
        time.sleep(retry_delay / steps)  # Delay before changing color
