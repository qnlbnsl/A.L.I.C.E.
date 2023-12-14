import numpy as np


def calculate_mic_pair_angles(mic_positions):
    # Expand mic_positions to enable broadcasting
    mic1_positions = mic_positions[:, np.newaxis, :]
    mic2_positions = mic_positions[np.newaxis, :, :]

    # Calculate differences between all pairs of microphones
    deltas = mic2_positions - mic1_positions

    # Calculate angles using arctan2, handling the delta in y and delta in x
    angles = np.arctan2(deltas[:, :, 1], deltas[:, :, 0])

    return angles
