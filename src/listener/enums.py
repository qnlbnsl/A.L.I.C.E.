## Types
from numpy import array, float64, float32, zeros
from numpy.typing import NDArray

# recording configs
CHANNELS: int = 8  # 8 microphones
SAMPLE_WIDTH: int = 2  # int16 = 2 bytes, int32 = 4 bytes, float32 = 4 bytes
RATE: int = 16000  # Hz
BLOCK_DURATION = 40  # milliseconds
RECORD_SECONDS: int = 5  # seconds
RECORD: bool = True  # Record audio from microphone

CHUNK: int = int((RATE * BLOCK_DURATION) // 1000)

# Detection Config
NO_SPEECH_COUNT = 0
NO_SPEECH_LIMIT = 2 * (RATE // CHUNK)
MIN_SPEECH_COUNT = 20
MIN_SPEECH_TIME = 2  # seconds
DECAY = 0.5  # decay factor for the running average

LABEL_MAP = {0: "other", 1: "command", 2: "question"}
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

# Define a queue to store decoded audio
silent_waveform = zeros(640, dtype=float32)
