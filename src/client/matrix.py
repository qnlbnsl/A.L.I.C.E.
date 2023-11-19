from matrix_lite import led
from enums import mic_positions
from asyncio import Queue
import numpy as np
from logger import logger
import asyncio

MIC_QUEUE = Queue()
loop = asyncio.get_event_loop()


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


def set_leds(theta, strength):
    everloop = ["black"] * led.length
    theta_smoother.add_theta(theta)
    avg_theta = theta_smoother.get_average_theta()

    led_position = get_led_position(avg_theta)
    try:
        for i in range(led_position - 3, led_position + 4):
            # Handle wrapping around
            index = i % 35
            # Adjust brightness based on distance from the central LED
            color = int((100 - abs(i - led_position) * 10) * strength / 100)
            # logger.debug(f"LED {index} - {color}")
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
    led_position = int(round(35 * normalized_theta / (2 * np.pi) + offset))

    # Wrap around if the position exceeds 35
    led_position = led_position % 35

    return led_position
