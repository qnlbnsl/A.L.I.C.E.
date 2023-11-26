import numpy as np
from numpy.typing import NDArray
from scipy.signal import find_peaks


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


@profile
def calculate_azimuth(tdoas, mic_positions, fs, speed_of_sound=343.0):
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
    num_mics = mic_positions.shape[0]
    azimuths = []

    for i in range(num_mics):
        for j in range(i + 1, num_mics):
            # Skip if no TDOA is calculated
            if tdoas[i, j] == 0:
                continue

            # Calculate the distance difference based on TDOA
            distance_diff = tdoas[i, j] * speed_of_sound

            # Positions of the two microphones
            mic1 = mic_positions[i]
            mic2 = mic_positions[j]

            # Calculate the midpoint between two microphones
            midpoint = (mic1 + mic2) / 2

            # Calculate the angle of the line connecting two microphones
            angle_mics = np.arctan2(mic2[1] - mic1[1], mic2[0] - mic1[0])

            # Calculate the angle from the midpoint to the sound source
            # Assumption: Sound source is far enough for linear approximation
            angle_to_source = (
                angle_mics + np.pi / 2
            )  # Perpendicular to the line connecting mics

            # Adjust the angle based on the sign of the TDOA
            if distance_diff < 0:
                angle_to_source += np.pi

            # Normalize the angle
            angle_to_source = np.mod(angle_to_source, 2 * np.pi)

            azimuths.append(angle_to_source)

    # Average the estimated azimuths
    if azimuths:
        azimuth = np.mean(azimuths)
    else:
        azimuth = 0  # No valid azimuth estimation

    return azimuth


@profile
def calculate_doa(audio_data: NDArray[np.int16], mic_positions, fs=16000):
    num_samples, num_channels = audio_data.shape
    half_channels = num_channels // 2
    # Initialize variables to store TDOA for each pair
    tdoas = np.zeros((num_channels, num_channels))

    # Calculate TDOA between each pair of microphones
    # use opposite pairs of microphones to calculate TDOA
    for i in range(half_channels):
        for j in range(i + 4, num_channels):
            tdoa = estimate_tdoa(audio_data[:, i], audio_data[:, j], fs)
            if tdoa is not None:
                tdoas[i, j] = tdoa
                tdoas[j, i] = -tdoa

    azimuth = calculate_azimuth(tdoas, mic_positions, fs)

    return azimuth