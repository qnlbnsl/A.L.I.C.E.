import numpy as np
from scipy.interpolate import interp1d

from multiprocessing import Queue
from client.audio.tdoa import calculate_doa

from typing import Tuple
from numpy.typing import NDArray

import client.audio.strength as str
from client.utils.fir_filter import apply_fir_filter
from client.utils.led_control import set_leds, clear_leds

from logger import logger

from enums import (
    mic_positions,
    RATE,
    STRENGHT_THRESHOLD,
    CHUNK,
    CHANNELS,
    mic_positions_3d,
)

# Strength tracker parameters
silent_waveform = np.zeros(CHUNK, dtype=np.int16)


str_tracker = str.SignalStrengthTracker(
    smoothing_window=30, silence_threshold=STRENGHT_THRESHOLD
)  # processes each "chunk"


def beamform_audio(
    raw_audio_queue: Queue, beamformed_audio_queue: Queue, far_field_queue: Queue
):
    logger.debug("Starting beamformer")
    while True:
        # get audio from queue
        audio_data: NDArray[np.int16] = raw_audio_queue.get()
        far_field_audio: NDArray[np.int16] = far_field_queue.get()
        reshaped_audio_data = None
        # TODO: AEC using far field queue
        try:
            reshaped_audio_data = np.reshape(audio_data, (CHUNK, CHANNELS)).T
            assert reshaped_audio_data.shape[0] == CHANNELS
            assert reshaped_audio_data.shape[1] == CHUNK
        except Exception as e:
            logger.error(f"Error in reshaping audio: {e}")
            reshaped_audio_data = audio_data
        # Apply FIR filter # TODO: Fix this
        # reshaped_audio_data = apply_fir_filter(reshaped_audio_data, RATE)
        # beamform
        try:
            beamformed_audio, doa_angle, strength = process_audio(reshaped_audio_data)
        except Exception as e:
            logger.error(f"Error in beamforming: {e}")
            raise e
        # logger.debug(f"DOA: {doa_angle}, Strength: {strength}")
        if strength > STRENGHT_THRESHOLD:
            # set leds
            set_leds(doa_angle, strength)
            beamformed_audio_queue.put(beamformed_audio)
        else:
            # clear leds
            clear_leds()
            # i think this should be enough to make the server not play the audio
            # beamformed_audio_queue.put(silent_waveform)


def process_audio(
    audio: NDArray[np.int16],
) -> Tuple[NDArray[np.int16], np.float64, np.float64]:
    # Get theta from TDOA
    theta = calculate_doa(audio, mic_positions)
    # logger.debug(f"Theta: {theta}")
    delays = calculate_delays(mic_positions_3d, theta)
    # Apply delays and sum signals
    audio = delay_and_sum(audio, delays)
    # Calculate signal strength
    strength = str_tracker.process_chunk(audio)
    # logger.debug(f"Strength: {type(strength)}")
    return audio, theta, strength  # type: ignore # TODO: Fix type


def delay_and_sum(audio_data_2d, delays):
    # Make sure audio_data_2d and delays have the same number of rows (channels)
    assert audio_data_2d.shape[0] == len(
        delays
    ), "Mismatch between number of channels and delays"

    # Initialize an array for the result; same length as one channel
    result = np.zeros(audio_data_2d.shape[1])
    t = (
        np.arange(audio_data_2d.shape[1]) / RATE
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

    return result.astype(np.int16)


def calculate_delays(mic_positions, theta, speed_of_sound=343, fs=16000):
    # Convert angles to radians
    theta = np.radians(theta)
    phi = np.radians(0)

    # Calculate the unit vector for the given angles
    unit_vector = np.array(
        [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    )

    # Calculate the delays in seconds
    delays_in_seconds = np.dot(mic_positions, unit_vector) / speed_of_sound

    # Normalize the delays to be relative to the first microphone
    delays_in_seconds -= delays_in_seconds[0]

    # Convert delays from seconds to samples by multiplying with the sampling rate
    # delays_in_samples = delays_in_seconds * fs

    # return delays_in_samples
    return delays_in_seconds
