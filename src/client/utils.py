import asyncio
import time

import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt

from collections import defaultdict
from statistics import mean, median

from enums import mic_positions_2d

from logger import logger

mic_strength_queue = asyncio.Queue()

mic_angles: NDArray = np.arctan2(mic_positions_2d[:, 1], mic_positions_2d[:, 0])
print(mic_angles)


def find_closest_mic_by_angle(theta, strength):
    # Convert theta to radians and ensure it is in the range [-π, π]
    theta_rad = np.arctan2(np.sin(theta), np.cos(theta))

    # Calculate angular differences
    angle_diffs = mic_angles - theta_rad

    # Account for angular wrap-around at -π and π
    angle_diffs = np.where(angle_diffs > np.pi, angle_diffs - 2 * np.pi, angle_diffs)
    angle_diffs = np.where(angle_diffs < -np.pi, angle_diffs + 2 * np.pi, angle_diffs)

    # Find the index of the microphone with the minimum absolute angular difference
    closest_mic_index = np.argmin(np.abs(angle_diffs))
    closest_mic = (
        closest_mic_index + 1
    )  # Assuming microphones are numbered starting from 1

    logger.debug(
        f"Estimated DOA: theta={theta}, -> closest_mic={closest_mic} with an angle of {mic_angles[closest_mic_index]} and a strength of {strength}"
    )
    mic_strength_queue.put_nowait((closest_mic, strength, time.time()))

    return closest_mic


def generate_steering_vectors(mic_positions, thetas, phis, freq, speed_of_sound=343):
    k = 2 * np.pi * freq / speed_of_sound
    steering_vectors = np.exp(
        1j
        * k
        * (
            mic_positions
            @ np.array(
                [
                    np.sin(phis) * np.cos(thetas),
                    np.sin(phis) * np.sin(thetas),
                    np.cos(phis),
                ]
            )
        )
    )
    return steering_vectors


async def process_and_print_mic_data(queue):
    mic_stats = defaultdict(lambda: {"strengths": [], "occurrences": 0})

    # Process all items in the queue
    while not queue.empty():
        mic_id, strength = await queue.get()
        stats = mic_stats[mic_id]
        stats["strengths"].append(strength)
        stats["occurrences"] += 1

    # Prepare and print the statistics in a table format
    print(
        "{:<8} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
            "Mic ID", "Min", "Max", "Mean", "Median", "Occurrences", "Total Strength"
        )
    )

    for mic_id, stats in mic_stats.items():
        strengths = stats["strengths"]
        if strengths:
            min_strength = min(strengths)
            max_strength = max(strengths)
            avg_strength = mean(strengths)
            median_strength = median(strengths)
            total_strength = sum(strengths)
            occurrences = stats["occurrences"]

            print(
                "{:<8} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    mic_id,
                    min_strength,
                    max_strength,
                    f"{avg_strength:.2f}",
                    f"{median_strength:.2f}",
                    occurrences,
                    total_strength,
                )
            )

    print("Data processing complete.")


async def process_mic_data_for_plotting(queue):
    mic_stats = defaultdict(
        lambda: {"strengths": [], "timestamps": [], "occurrences": 0}
    )

    while not queue.empty():
        mic_id, strength, timestamp = await queue.get()
        stats = mic_stats[mic_id]
        stats["strengths"].append(strength)
        stats["timestamps"].append(timestamp)
        stats["occurrences"] += 1

    return mic_stats


async def plot_mic_strengths():
    plt.figure(figsize=(10, 6))
    mic_stats = await process_mic_data_for_plotting(mic_strength_queue)
    for mic_id, stats in mic_stats.items():
        plt.plot(stats["timestamps"], stats["strengths"], label=f"Mic {mic_id}")

    plt.xlabel("Time (s)")
    plt.ylabel("Strength")
    plt.title("Microphone Strength Trajectory Over Time")
    plt.legend()
    plt.savefig("mic_strengths.png")
