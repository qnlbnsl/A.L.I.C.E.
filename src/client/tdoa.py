from line_profiler import profile
import numpy as np
from numpy.typing import NDArray
from scipy.signal import find_peaks

from logger import logger
from enums import CHANNELS, mic_positions
from utils import calculate_mic_pair_angles

num_mics = mic_positions.shape[0]

mic_pair_angles = calculate_mic_pair_angles(mic_positions)


@profile
def estimate_tdoa(sig1, sig2, fs, threshold=0.1):
    """
    Estimate the Time Difference of Arrival (TDOA) between two signals.

    Parameters:
    sig1, sig2: The input signals (numpy arrays).
    fs: Sampling frequency of the signals.
    threshold: Threshold value for peak detection.

    Returns:
    tdoa: Estimated TDOA in seconds.
    """
    # Find first significant peak in each signal
    peaks1, _ = find_peaks(np.abs(sig1), height=threshold)
    peaks2, _ = find_peaks(np.abs(sig2), height=threshold)

    if len(peaks1) == 0 or len(peaks2) == 0:
        return None  # No significant peaks found

    # Get first peak locations
    peak1 = peaks1[0]
    peak2 = peaks2[0]

    # Calculate TDOA
    tdoa = (peak2 - peak1) / fs
    return tdoa


def estimate_tdoa_cross_correlation(sig1, sig2, fs):
    """
    Estimate the Time Difference of Arrival (TDOA) between two signals using cross-correlation.

    Parameters:
    sig1, sig2: The input signals (numpy arrays).
    fs: Sampling frequency of the signals.

    Returns:
    tdoa: Estimated TDOA in seconds.
    """
    # Perform cross-correlation between the two signals
    corr = np.correlate(sig1, sig2, "full")

    # Find the index of the maximum correlation
    max_corr_index = np.argmax(corr)

    # Calculate the lag in samples
    lag_samples = max_corr_index - len(sig1) + 1

    # Convert lag to time in seconds
    tdoa = lag_samples / fs

    return tdoa


@profile
def calculate_azimuth(tdoas, speed_of_sound=343.0) -> np.float64:
    """
    Estimate the azimuth angle using TDOA measurements and microphone positions.

    Parameters:
    tdoas: Array of TDOA measurements.
    mic_positions: Positions of the microphones in 2D.
    fs: Sampling frequency.
    speed_of_sound: Speed of sound in air (m/s).

    Returns:
    azimuth: Estimated azimuth angle in radians.
    """
    azimuth: np.float64 = np.float64(0)
    # Use precomputed mic_pair_angles
    distance_diffs = tdoas * speed_of_sound

    # Calculate angles from mic_pair_angles
    angles_to_source = mic_pair_angles + np.pi / 2
    angles_to_source[distance_diffs < 0] += np.pi

    # Normalize the angles
    angles_to_source = np.mod(angles_to_source, 2 * np.pi)

    # Filter out zero TDOAs
    valid_angles = angles_to_source[tdoas != 0]

    # Average the estimated azimuths
    if valid_angles.size > 0:
        azimuth = np.mean(valid_angles)

    return azimuth


@profile
def calculate_doa(audio_data: NDArray[np.int16], mic_positions, fs=16000) -> np.float64:
    # logger.debug("Retrieving audio shape")
    num_channels = CHANNELS
    half_channels = num_channels // 2  # 4
    # Initialize variables to store TDOA for each pair
    tdoas = np.zeros((num_channels, num_channels))

    # Calculate TDOA between each pair of microphones
    # use opposite pairs of microphones to calculate TDOA
    for i in range(half_channels):
        j = i + half_channels
        # logger.debug(f"Calculating TDOA for mic {i} and {j}")
        # tdoa1 = estimate_tdoa(audio_data[:, i], audio_data[:, j], fs)
        tdoa2 = estimate_tdoa_cross_correlation(audio_data[:, i], audio_data[:, j], fs)
        # if tdoa1 and tdoa2:
        # logger.debug(f"tdoa1: {tdoa1}, tdoa2: {tdoa2}, diff: {tdoa1 - tdoa2}")
        tdoa = tdoa2
        if tdoa is not None:
            tdoas[i, j] = tdoa
            tdoas[j, i] = -tdoa

    azimuth: np.float64 = calculate_azimuth(tdoas)

    return azimuth
