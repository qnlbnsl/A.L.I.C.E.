## Types
from numpy import array
from numpy.typing import NDArray
from numpy import float64

# recording configs
CHANNELS: int = 8  # overriden from client
SAMPLE_WIDTH: int = 2  # We are using int16 which is 2 bytes
RATE: int = 16000  # overriden from client
BLOCK_DURATION = 30  # milliseconds
RECORD_SECONDS: int = 5
RECORD: bool = True

CHUNK: int = int((RATE * BLOCK_DURATION) // 1000)

# Detection Config
NO_SPEECH_COUNT = 0
NO_SPEECH_LIMIT = 2 * (RATE // CHUNK)
MIN_SPEECH_COUNT = 20
MIN_SPEECH_TIME = 2  # seconds
DECAY = 0.5  # decay factor for the running average

# Microphone positions in millimeters, converted to meters
mic_positions: NDArray[float64] = array(
    [
        [20.0908795e-3, -48.5036755e-3, 0],
        [-20.0908795e-3, -48.5036755e-3, 0],
        [-48.5036755e-3, -20.0908795e-3, 0],
        [-48.5036755e-3, 20.0908795e-3, 0],
        [-20.0908795e-3, 48.5036755e-3, 0],
        [20.0908795e-3, 48.5036755e-3, 0],
        [48.5036755e-3, 20.0908795e-3, 0],
        [48.5036755e-3, -20.0908795e-3, 0],
    ]
)
