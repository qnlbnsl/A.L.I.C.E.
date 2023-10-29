## Types
from numpy import array
from numpy.typing import NDArray
from numpy import float64
from pyaudio import paInt16
# recording configs
CHUNK: int = 1440
FORMAT: int = paInt16
CHANNELS: int = 8
RATE: int = 48000
RECORD_SECONDS: int = 5
# Microphone positions in millimeters, converted to meters


mic_positions: NDArray[float64] = array([
    [20.0908795e-3, -48.5036755e-3, 0],
    [-20.0908795e-3, -48.5036755e-3, 0],
    [-48.5036755e-3, -20.0908795e-3, 0],
    [-48.5036755e-3, 20.0908795e-3, 0],
    [-20.0908795e-3, 48.5036755e-3, 0],
    [20.0908795e-3, 48.5036755e-3, 0],
    [48.5036755e-3, 20.0908795e-3, 0],
    [48.5036755e-3, -20.0908795e-3, 0]
])