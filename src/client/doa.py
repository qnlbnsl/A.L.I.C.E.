import numpy as np
from numpy.typing import NDArray
from enums import mic_positions_2d
from gpu_fft import fft, ifft
from logger import logger

max_tof = 6  # Maximum time-of-flight between microphone pairs
pairwise_distances = np.sqrt(
    np.sum((mic_positions_2d[:, np.newaxis] - mic_positions_2d) ** 2, axis=2)
)
# Find the maximum distance
d_max = np.max(pairwise_distances)

# Speed of sound in air (m/s)
speed_of_sound = 343

# Calculate expected delay in seconds
expected_delay = d_max / speed_of_sound

# Convert expected delay to milliseconds
expected_delay_ms = expected_delay * 1000


# @profile
# def fft_cross_correlate(signal_a, signal_b):
#     n = 2 ** np.ceil(np.log2(signal_a.size + signal_b.size - 1)).astype(int)

#     # Initialize input arrays for FFT
#     fft_input_a = np.zeros(n, dtype=np.float32)
#     fft_input_b = np.zeros(n, dtype=np.float32)

#     # Assign inputs
#     fft_input_a[: signal_a.size] = signal_a
#     fft_input_b[: signal_b.size] = signal_b

#     # Perform FFT
#     fft_result_a = fftn(fft_input_a, ndim=1)
#     fft_result_b = fftn(fft_input_b, ndim=1)

#     # Perform element-wise multiplication
#     result = fft_result_a * np.conj(fft_result_b)

#     # Perform IFFT
#     ifft_result = ifftn(result, ndim=1)
#     logger.debug(f"ifft_result: {ifft_result}")
#     return ifft_result  # Since the result is expected to be real


def fft_cross_correlate(signal_a, signal_b):
    n = 2 ** np.ceil(np.log2(signal_a.size + signal_b.size - 1)).astype(int)
    fft_input_a = np.zeros(n, dtype=np.float32)
    fft_input_b = np.zeros(n, dtype=np.float32)

    fft_input_a[: signal_a.size] = signal_a
    fft_input_b[: signal_b.size] = signal_b

    # Transfer data to GPU and perform FFT
    fft_result_a = fft(fft_input_a)  # Adjust based on actual library function
    fft_result_b = fft(fft_input_b)

    result = fft_result_a * np.conj(fft_result_b)

    # Perform IFFT and transfer data back from GPU
    ifft_result = ifft(result)  # Adjust based on actual library function

    return ifft_result.real  # Assuming result is real


# @profile
def calculate_doa(audio_data: NDArray[np.int16]):
    num_samples, num_channels = audio_data.shape
    # logger.debug(f"num_samples: {num_samples}, num_channels: {num_channels}")
    half_channels = num_channels // 2
    # Initialize variables
    current_mag = np.zeros(half_channels)
    current_index = np.zeros(half_channels, dtype=int)

    # Calculate cross-correlation and find the indices of maximum correlation
    for channel in range(half_channels):
        correlation = fft_cross_correlate(
            audio_data[:, channel], audio_data[:, channel + 4]
        )
        mid_point = len(correlation) // 2
        max_index = np.argmax(correlation[mid_point - max_tof : mid_point + max_tof])
        current_index[channel] = max_index + mid_point - max_tof
        current_mag[channel] = correlation[current_index[channel]]

    # Find the perpendicular microphone pair
    perp_pair_index = np.argmin(np.abs(current_index - num_samples // 2))
    dir_index = (perp_pair_index + 2) % 4
    if current_index[dir_index] > num_samples // 2:
        dir_index += 4

    mic_direction = dir_index
    theta = np.arctan2(
        mic_positions_2d[mic_direction][1], mic_positions_2d[mic_direction][0]
    )
    phi = np.abs(current_index[perp_pair_index]) * np.pi / 2.0 / (max_tof - 1)

    return theta, phi
