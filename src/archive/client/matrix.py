from matrix_lite import led

# from enums import mic_positions
from asyncio import Queue
import numpy as np
from client.logger import logger
import asyncio
import time
import matplotlib.pyplot as plt
from classes.theta import ThetaSmoother
from collections import defaultdict
from statistics import mean, median

MIC_QUEUE = Queue()
loop = asyncio.get_event_loop()
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
        MIC_QUEUE.put_nowait((theta, led_position, time.time()))
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


def get_led_position(theta, avg_theta):
    # Normalize avg_theta to be within the range of 0 to 2*pi
    normalized_theta = avg_theta % (2 * np.pi)

    # Calculate LED position in a clockwise manner
    # Since theta = 0 is around LED 17/18, adjust for this offset
    led_position = int(round((1 - normalized_theta / (2 * np.pi)) * led.length)) + 17

    # Correct for any negative values or values exceeding led.length
    led_position = (led_position + led.length) % led.length
    logger.debug(
        "LED position: {}".format(led_position)
        + " theta: {}".format(theta * 180 / np.pi)
        + " avg_theta: {}".format(avg_theta * 180 / np.pi)
    )
    return led_position


def clear_leds():
    led.set(default_everloop)


async def process_mic_data_for_plotting(queue):
    mic_stats = defaultdict(lambda: {"theta": [], "timestamps": [], "occurrences": 0})

    while not queue.empty():
        led_id, theta, timestamp = await queue.get()
        stats = mic_stats[led_id]
        stats["theta"].append(theta)
        stats["timestamps"].append(timestamp)
        stats["occurrences"] += 1

    return mic_stats


async def plot_led():
    plt.figure(figsize=(10, 6))
    mic_stats = await process_mic_data_for_plotting(MIC_QUEUE)
    for led_id, stats in mic_stats.items():
        plt.plot(stats["timestamps"], stats["theta"], label=f"LED {led_id}")

    plt.xlabel("Time (s)")
    plt.ylabel("Theta")
    plt.title("Microphone Strength Trajectory Over Time")
    plt.legend()
    plt.savefig("led.png")
