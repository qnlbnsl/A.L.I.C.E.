import numpy as np
from numpy.typing import NDArray
from typing import List


class SignalStrengthTracker:
    def __init__(self, smoothing_window=5, silence_threshold=-45):
        self.smoothing_window = smoothing_window
        self.silence_threshold = silence_threshold
        self.strength_buffer: List[np.float64] = []

    def calculate_signal_strength(self, signal: NDArray[np.int16]):
        rms = np.sqrt(np.mean(np.square(signal.astype(np.float64))))
        rms = np.finfo(float).eps if rms == 0 else rms
        strength_db = 20 * np.log10(rms / 32768)
        return strength_db

    def update_strength_buffer(self, strength: np.float64):
        self.strength_buffer.append(strength)
        if len(self.strength_buffer) > self.smoothing_window:
            self.strength_buffer.pop(0)

    def get_smoothed_strength(self):
        if len(self.strength_buffer) == 0:
            return 0  # Default value if buffer is empty

        # Apply weighted average: recent values have more weight
        weights = []
        for strength in self.strength_buffer:
            if strength >= self.silence_threshold:
                weights.append(50)
            else:
                weights.append(1)
        weighted_strengths = np.array(self.strength_buffer) * np.array(weights)
        total_weight = np.sum(weights)
        smoothed_strength = np.sum(weighted_strengths) / total_weight

        return smoothed_strength

    def process_chunk(self, chunk):
        strength = self.calculate_signal_strength(chunk)
        self.update_strength_buffer(strength)
        return self.get_smoothed_strength()
