import numpy as np
from enums import CHANNELS, CHUNK
from logger import logger
from numpy.typing import NDArray

from enums import mic_positions_2d


def fft_cross_correlate(signal_a, signal_b):
    # Compute Fourier transforms
    A = np.fft.rfft(signal_a, n=signal_a.size + signal_b.size - 1)
    B = np.fft.rfft(signal_b, n=signal_a.size + signal_b.size - 1)

    # Perform complex conjugate multiplication in the frequency domain
    C = A * np.conj(B)

    # Compute the inverse Fourier transform to get the cross-correlation
    corr = np.fft.irfft(C)

    return corr


def calculate_doa(
    audio_data,
    # mic_positions: NDArray[np.float64] = mic_positions,
    fs=16000,
    speed_of_sound=343,
):
    num_samples, num_channels = audio_data.shape
    max_tof = 6  # Maximum time-of-flight between microphone pairs

    # Initialize variables
    current_mag = np.zeros(num_channels // 2)
    current_index = np.zeros(num_channels // 2, dtype=int)
    theta = 0  # Azimuthal angle in the horizontal plane
    phi = 0  # Elevation angle from the horizontal plane

    # Calculate cross-correlation and find the indices of maximum correlation
    for channel in range(num_channels // 2):
        correlation = fft_cross_correlate(
            audio_data[:, channel], audio_data[:, channel + 4]
        )
        mid_point = len(correlation) // 2
        max_index = np.argmax(correlation[mid_point - max_tof : mid_point + max_tof])
        current_index[channel] = max_index + mid_point - max_tof
        current_mag[channel] = correlation[current_index[channel]]

    # Find the perpendicular microphone pair
    perp_pair_index = np.argmin(np.abs(current_index - num_samples // 2))
    perp_pair = (perp_pair_index, perp_pair_index + 4)

    # Determine direction (mic index) and calculate physical angles
    dir_index = (perp_pair_index + 2) % 4
    if current_index[dir_index] > num_samples // 2:
        dir_index += 4

    # Checking the shape of the array
    mic_direction = dir_index
    theta = np.arctan2(
        mic_positions_2d[mic_direction][1], mic_positions_2d[mic_direction][0]
    )
    phi = np.abs(current_index[perp_pair_index]) * np.pi / 2.0 / (max_tof - 1)
    return theta, phi
