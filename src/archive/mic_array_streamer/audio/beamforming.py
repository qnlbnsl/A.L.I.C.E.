import numpy as np
from scipy.signal import correlate
from scipy.fftpack import fft, ifft
from scipy.linalg import eigh
from scipy.interpolate import interp1d

def delay_and_sum(audio_data_2d, delays, fs):
    # Make sure audio_data_2d and delays have the same number of rows (channels)
    assert audio_data_2d.shape[0] == len(delays), "Mismatch between number of channels and delays"

    # Initialize an array for the result; same length as one channel
    result = np.zeros(audio_data_2d.shape[1])
    t = np.arange(audio_data_2d.shape[1]) / fs  # Time vector based on the sampling frequency

    for i, delay in enumerate(delays):
        # Create an interpolation object for the current channel
        interpolator = interp1d(t, audio_data_2d[i, :], kind='linear', fill_value="extrapolate")

        # Calculate the new time points, considering the delay
        t_shifted = t - delay

        # Interpolate the signal at the new time points
        shifted_signal = interpolator(t_shifted)

        # Sum the interpolated signal to the result
        result += shifted_signal

    # Divide by the number of channels to average
    result /= len(delays)

    return result


def delay_and_sum_bkp(audio_data_2d, delays):
    # Make sure audio_data_2d and delays have the same number of rows (channels)
    assert audio_data_2d.shape[0] == len(delays), "Mismatch between number of channels and delays"

    # Initialize an array for the result with zeros; same length as one channel
    result = np.zeros(audio_data_2d.shape[1])

    for i in range(len(delays)):
        # Roll and sum each channel based on its corresponding delay
        result += np.roll(audio_data_2d[i, :], delays[i])

    # Divide by the number of channels to average
    result /= audio_data_2d.shape[0]

    return result

def calculate_delays(mic_positions, theta, phi, speed_of_sound=343, fs=44100):
    # Convert angles to radians
    theta = np.radians(theta)
    phi = np.radians(phi)

    # Calculate the unit vector for the given angles
    unit_vector = np.array([
        np.sin(theta) * np.cos(phi),
        np.sin(theta) * np.sin(phi),
        np.cos(theta)
    ])

    # Calculate the delays in seconds
    delays_in_seconds = np.dot(mic_positions, unit_vector) / speed_of_sound

    # Normalize the delays to be relative to the first microphone
    delays_in_seconds -= delays_in_seconds[0]

    # Convert delays from seconds to samples by multiplying with the sampling rate
    # delays_in_samples = delays_in_seconds * fs
    
    # return delays_in_samples
    return delays_in_seconds

def generate_steering_vectors(mic_positions, thetas, phis, freq, speed_of_sound=343):
    k = 2 * np.pi * freq / speed_of_sound
    steering_vectors = np.exp(
        1j * k * (mic_positions @ np.array([np.sin(phis) * np.cos(thetas), np.sin(phis) * np.sin(thetas), np.cos(phis)]))
    )
    return steering_vectors

def music_algorithm(R, steering_vectors, num_sources, num_angles):
    _, V = eigh(R)
    noise_subspace = V[:, :-num_sources]
    pseudo_spectrum = []

    for a in range(num_angles):
        S_theta_phi = steering_vectors[:, a][:, np.newaxis]
        music_pseudo_value = 1 / np.linalg.norm(S_theta_phi.conj().T @ noise_subspace @ noise_subspace.conj().T @ S_theta_phi)
        pseudo_spectrum.append(music_pseudo_value)

    return np.array(pseudo_spectrum)

def estimate_doa_with_music(audio_data, mic_positions, sampling_rate):
    freq = 1000  # Choose a frequency for DOA estimation, can be adapted
    speed_of_sound = 343  # Speed of sound in air in m/s

    # Create the spatial covariance matrix
    R = audio_data @ audio_data.conj().T / audio_data.shape[1]

    # Generate possible DOA angles
    num_angles = 180
    possible_thetas = np.linspace(0, np.pi, num_angles)
    possible_phis = np.linspace(0, np.pi / 2, num_angles)
    steering_vectors = generate_steering_vectors(mic_positions, possible_thetas, possible_phis, freq)

    # Run the MUSIC algorithm
    pseudo_spectrum = music_algorithm(R, steering_vectors, 1, num_angles)

    # Find the angles corresponding to the peak
    estimated_theta = possible_thetas[np.argmax(pseudo_spectrum)]
    estimated_phi = possible_phis[np.argmax(pseudo_spectrum)]

    return estimated_theta, estimated_phi
