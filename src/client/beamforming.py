import numpy as np
import asyncio

from multiprocessing import Queue
from tdoa import calculate_doa

from typing import Tuple
from numpy.typing import NDArray

from strength import SignalStrengthTracker as str
from fir_filter import apply_fir_filter
from led_control import set_leds, clear_leds

from logger import logger

from enums import mic_positions, RATE, STRENGHT_THRESHOLD, CHUNK, CHANNELS


def beamform_audio(raw_audio_queue: Queue, beamformed_audio_queue: Queue):
    logger.debug("Starting beamformer")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        # get audio from queue
        audio_data: NDArray[np.int16] = raw_audio_queue.get(block=True, timeout=None)
        audio_data = apply_fir_filter(audio_data, RATE)
        reshaped_audio_data = None
        try:
            reshaped_audio_data = np.reshape(audio_data, (CHUNK, CHANNELS)).T
            assert reshaped_audio_data.shape[0] == CHANNELS
            assert reshaped_audio_data.shape[1] == CHUNK
        except Exception as e:
            logger.error(f"Error in reshaping audio: {e}")
            reshaped_audio_data = audio_data
        # beamform
        beamformed_audio, doa_angle, strength = process_audio(reshaped_audio_data)
        logger.debug(f"DOA: {doa_angle}, Strength: {strength}")
        if strength > STRENGHT_THRESHOLD:
            # set leds
            set_leds(doa_angle, strength)
        else:
            # clear leds
            clear_leds()
        # add to queue
        beamformed_audio_queue.put(beamformed_audio)


def process_audio(audio) -> Tuple[NDArray[np.float64], np.float64, np.float64]:
    # Get theta from TDOA
    theta = calculate_doa(audio, mic_positions)
    # logger.debug(f"Theta: {theta}")
    delays = calculate_delays(mic_positions, theta)
    # Apply delays and sum signals
    audio = delay_and_sum(audio, delays)
    # Calculate signal strength
    strength = str().process_chunk(audio)
    return audio, theta, strength


def delay_and_sum(audio_data_2d, delays) -> NDArray[np.float64]:
    num_channels, num_samples = audio_data_2d.shape
    max_delay = int(np.max(delays))
    padded_length = num_samples + max_delay

    # Initialize a padded array to store delayed signals
    delayed_signals = np.zeros((num_channels, padded_length))

    # Apply delays to each channel
    for i in range(num_channels):
        delay = int(delays[i])
        # Copy the signal to the delayed position in the padded array
        delayed_signals[i, delay : delay + num_samples] = audio_data_2d[i, :]

    # Sum across channels and then trim the padded portion
    summed_signal = np.sum(delayed_signals, axis=0)[max_delay:]

    # Averaging the sum (Beamforming)
    averaged_signal = summed_signal / num_channels

    return averaged_signal


def calculate_delays(mic_positions, theta, speed_of_sound=343, fs=RATE):
    # Convert angles to radians
    theta = np.radians(theta)
    # Sound source position in circular coordinates
    x = np.cos(theta)
    y = np.sin(theta)

    # Calculate distances and delays
    distances = np.sqrt((mic_positions[:, 0] - x) ** 2 + (mic_positions[:, 1] - y) ** 2)

    # Convert distances to delays
    delays_in_seconds = distances / speed_of_sound
    delays_in_seconds -= np.min(delays_in_seconds)  # Normalize to the minimum delay

    return delays_in_seconds * fs  # Convert to samples
