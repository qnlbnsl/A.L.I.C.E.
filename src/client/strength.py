import numpy as np
from collections import deque
from typing import List, Deque
from numpy.typing import NDArray
from enums import STRENGHT_THRESHOLD


class SignalStrengthTracker:
    def __init__(self, smoothing_window=5, silence_threshold=-40):
        self.smoothing_window = smoothing_window
        self.silence_threshold = silence_threshold
        self.strength_buffer: Deque[np.float64] = deque([], maxlen=smoothing_window)
        self.silence_weight = 1
        self.non_silence_weight = 50
        self.log_constant = 20 * np.log10(1 / 32768)

    def calculate_signal_strength(self, signal: np.ndarray) -> np.float64:
        # Check if the signal is empty
        if signal.size == 0:
            return np.float64(STRENGHT_THRESHOLD - 5)  # 5 less than the threshold

        if not np.any(signal):  # Check if the signal is all zeros
            return self.log_constant

        rms = np.sqrt(np.mean(np.square(signal.astype(np.float64))))
        strength_db = 20 * np.log10(rms) + self.log_constant
        return strength_db  # Return the strength in dB

    def update_strength_buffer(self, strength: np.float64):
        self.strength_buffer.append(strength)

    def get_smoothed_strength(self) -> np.float64:
        if not self.strength_buffer:
            return np.float64(
                STRENGHT_THRESHOLD - 5
            )  # Default value if buffer is empty

        buffer_array = np.array(self.strength_buffer)
        weights = np.where(
            buffer_array >= self.silence_threshold,
            self.non_silence_weight,
            self.silence_weight,
        )
        weighted_strengths: NDArray[np.float64] = buffer_array * weights
        smoothed_strength: np.float64 = np.sum(weighted_strengths) / np.sum(weights)

        return smoothed_strength

    def process_chunk(self, chunk: NDArray[np.int16]):
        strength = self.calculate_signal_strength(chunk)
        self.update_strength_buffer(strength)
        return self.get_smoothed_strength()
