import numpy as np

from logger import logger


def find_closest_mic_by_angle(mic_positions, theta, phi, strength):
    # Convert theta and phi to a direction vector
    direction_vector = np.array(
        [
            np.cos(phi) * np.cos(theta),  # x-component
            np.cos(phi) * np.sin(theta),  # y-component
            np.sin(phi),  # z-component (optional, if using 3D coordinates)
        ]
    )

    # Normalize the direction vector
    direction_vector /= np.linalg.norm(direction_vector)

    closest_mic = None
    min_angle = np.inf  # Initialize with a large number

    # Iterate through each microphone position
    for i, mic_pos in enumerate(mic_positions):
        # Get the microphone position vector (assuming it's already a unit vector)
        mic_vector = mic_pos[:2]  # Use only x and y for 2D
        mic_vector = np.append(mic_vector, 0)  # Add z-component for 3D vector
        mic_vector /= np.linalg.norm(mic_vector)

        # Calculate the angle between the direction vector and the microphone position vector
        angle = np.arccos(np.clip(np.dot(direction_vector, mic_vector), -1.0, 1.0))

        # Update the closest microphone if this angle is smaller
        if angle < min_angle:
            min_angle = angle
            closest_mic = i + 1  # Add 1 if mics are numbered from 1 to 8
    logger.debug(
        f"Estimated DOA: theta={theta}, phi={phi} -> closest_mic={closest_mic} with a strength of {strength}"
    )
