import numpy as np
from scipy.signal import correlate
from scipy.fftpack import fft, ifft
from scipy.linalg import eigh

def delay_and_sum(audio_data, delays):
    result = np.zeros_like(audio_data[0])
    for channel, delay in zip(audio_data, delays):
        result += np.roll(channel, delay)
    return result / len(audio_data)

def calculate_delays(mic_positions, theta, phi, speed_of_sound=343):
    # Convert angles to radians
    theta = np.radians(theta)
    phi = np.radians(phi)

    # Calculate the unit vector for the given angles
    unit_vector = np.array([
        np.sin(theta) * np.cos(phi),
        np.sin(theta) * np.sin(phi),
        np.cos(theta)
    ])

    # Calculate the delays
    delays = np.dot(mic_positions, unit_vector) / speed_of_sound

    # Normalize the delays to be relative to the first microphone
    delays -= delays[0]

    return delays

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
