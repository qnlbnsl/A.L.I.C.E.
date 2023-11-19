import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh
from scipy.interpolate import interp1d
from scipy.signal import butter, lfilter

from matrix import set_leds

from enums import CHANNELS, CHUNK, RATE, mic_positions

from logger import logger
from utils import find_closest_mic_by_angle


# @profile
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


# DOA estimation parameters
freq = 3000  # Choose a frequency for DOA estimation, can be adapted
num_angles = 180
possible_thetas = np.linspace(0, 2 * np.pi, num_angles)  # 360 degrees
possible_phis = np.linspace((np.pi / 2) * (-1), np.pi / 2, num_angles)
steering_vectors = generate_steering_vectors(
    mic_positions, possible_thetas, possible_phis, freq
)

silent_waveform = np.zeros(CHUNK, dtype=np.int16)  # Using int16 for 16-bit audio
min_rms_threshold = np.finfo(
    float
).eps  # effectively 1e-15 # a default minimum rms threshold


# Bandpass filter function
def bandpass_filter(data: np.ndarray, fs: int, order: int = 5) -> np.ndarray:
    lowcut = 300
    highcut = 3400
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    filtered_data = np.asarray(lfilter(b, a, data))
    return filtered_data


def calculate_signal_strength(signal):
    # Calculate the RMS of the signal
    rms = np.sqrt(np.mean(signal**2))
    # rms = max(rms, min_rms_threshold)  # effectively max(rms, 1e-15)

    # Convert RMS to decibels
    ref = 32768  # Reference amplitude for 16-bit audio
    # Avoid log of zero by replacing zero with a very small number
    rms = np.finfo(float).eps if rms == 0 else rms
    strength_db = 20 * np.log10(rms / ref)
    if np.isnan(strength_db):
        strength_db = min_rms_threshold
    return strength_db


# @profile
def beamform_audio(audio_data: NDArray[np.int16]) -> NDArray[np.int16]:
    # Current shape of audio is interleaved 8 channels of block_duration * sample_rate
    # Reshape audio to an array of [CHANNEL][CHUNK]. This way each chunk is it's own channel.
    reshaped_audio_data = None
    try:
        reshaped_audio_data = np.reshape(
            audio_data, (CHUNK, CHANNELS)
        ).T  # shape will be (8, 2048)
        assert reshaped_audio_data.shape[0] == CHANNELS
        assert reshaped_audio_data.shape[1] == CHUNK
    except Exception as e:
        logger.error(f"Error in reshaping audio: {e}")
        reshaped_audio_data = audio_data
        # print(reshaped_audio_data.shape)  # Should print (8, 2048)

    # logger.debug("Estimating DOA")
    theta, phi = estimate_doa_with_music(audio_data=reshaped_audio_data)
    # no return
    delays = calculate_delays(mic_positions, theta, phi, speed_of_sound=343, fs=16000)
    beamformed_signal = delay_and_sum(reshaped_audio_data, delays, 16000)
    strength = calculate_signal_strength(beamformed_signal)
    # in db The higher the number, the louder the sound. 0 is the loudest. -45 is the threshold.
    if strength > -48:
        # Limit calculated strength to -45 dB
        find_closest_mic_by_angle(mic_positions, theta, phi, strength)
        filtered_signal = bandpass_filter(beamformed_signal, fs=RATE)
        set_leds(theta, strength)
        return filtered_signal.astype(np.int16)
    else:
        return silent_waveform


# @profile
def delay_and_sum(audio_data_2d, delays, fs):
    # Make sure audio_data_2d and delays have the same number of rows (channels)
    assert audio_data_2d.shape[0] == len(
        delays
    ), "Mismatch between number of channels and delays"

    # Initialize an array for the result; same length as one channel
    result = np.zeros(audio_data_2d.shape[1])
    t = (
        np.arange(audio_data_2d.shape[1]) / fs
    )  # Time vector based on the sampling frequency

    for i, delay in enumerate(delays):
        # Create an interpolation object for the current channel
        interpolator = interp1d(
            t, audio_data_2d[i, :], kind="linear", fill_value="extrapolate"  # type: ignore
        )

        # Calculate the new time points, considering the delay
        t_shifted = t - delay

        # Interpolate the signal at the new time points
        shifted_signal = interpolator(t_shifted)

        # Sum the interpolated signal to the result
        result += shifted_signal

    # Divide by the number of channels to average
    result /= len(delays)

    return result


# @profile
def delay_and_sum_bkp(audio_data_2d, delays):
    # Make sure audio_data_2d and delays have the same number of rows (channels)
    assert audio_data_2d.shape[0] == len(
        delays
    ), "Mismatch between number of channels and delays"

    # Initialize an array for the result with zeros; same length as one channel
    result = np.zeros(audio_data_2d.shape[1])

    for i in range(len(delays)):
        # Roll and sum each channel based on its corresponding delay
        result += np.roll(audio_data_2d[i, :], delays[i])

    # Divide by the number of channels to average
    result /= audio_data_2d.shape[0]

    return result


# @profile
def calculate_delays(mic_positions, theta, phi, speed_of_sound=343, fs=44100):
    # Convert angles to radians
    theta = np.radians(theta)
    phi = np.radians(phi)
    # Calculate the unit vector for the given angles
    unit_vector = np.array(
        [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    )
    # Calculate the delays in seconds
    delays_in_seconds = np.dot(mic_positions, unit_vector) / speed_of_sound
    # Normalize the delays to be relative to the first microphone
    delays_in_seconds -= delays_in_seconds[0]

    # return delays_in_samples
    return delays_in_seconds


# @profile
def music_algorithm(R, steering_vectors, num_sources, num_angles):
    _, V = eigh(R)
    noise_subspace = V[:, :-num_sources]
    pseudo_spectrum = []

    for a in range(num_angles):
        S_theta_phi = steering_vectors[:, a][:, np.newaxis]
        music_pseudo_value = 1 / np.linalg.norm(
            S_theta_phi.conj().T
            @ noise_subspace
            @ noise_subspace.conj().T
            @ S_theta_phi
        )
        pseudo_spectrum.append(music_pseudo_value)

    return np.array(pseudo_spectrum)


# @profile
def estimate_doa_with_music(audio_data):
    # Create the spatial covariance matrix
    R = audio_data @ audio_data.conj().T / audio_data.shape[1]

    # Run the MUSIC algorithm
    pseudo_spectrum = music_algorithm(R, steering_vectors, 1, num_angles)
    # Find the angles corresponding to the peak
    estimated_theta = possible_thetas[np.argmax(pseudo_spectrum)]
    estimated_phi = possible_phis[np.argmax(pseudo_spectrum)]

    return estimated_theta, estimated_phi
