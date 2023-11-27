import numpy as np
from numpy.typing import NDArray

retry_max = 12
retry_delay = 5


# recording configs
CHANNELS: int = 8  # overriden from client
SAMPLE_WIDTH: int = 2  # We are using int16 which is 2 bytes
RATE: int = 16000  # overriden from client
BLOCK_DURATION = 40  # milliseconds
RECORD_SECONDS: int = 5
RECORD: bool = True

CHUNK: int = int((RATE * BLOCK_DURATION) // 1000)

STRENGHT_THRESHOLD: int = -40

# Microphone positions in millimeters, converted to meters
mic_positions_3d: NDArray[np.float64] = np.array(
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
 
# Microphone positions in millimeters, converted to meters
mic_positions: NDArray[np.float64] = np.array(
    [
        [20.0908795e-3, -48.5036755e-3],
        [-20.0908795e-3, -48.5036755e-3],
        [-48.5036755e-3, -20.0908795e-3],
        [-48.5036755e-3, 20.0908795e-3],
        [-20.0908795e-3, 48.5036755e-3],
        [20.0908795e-3, 48.5036755e-3],
        [48.5036755e-3, 20.0908795e-3],
        [48.5036755e-3, -20.0908795e-3],
    ]
)
