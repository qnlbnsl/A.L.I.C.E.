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
RECORD: bool = False
NO_SPEECH_COUNT = 0
NO_SPEECH_LIMIT = 2 * (RATE // CHUNK)

# Detection Config
MIN_SPEECH_COUNT = 20
MIN_SPEECH_TIME = 2  # seconds
DECAY = 0.8  # decay factor for the running average
# Microphone positions in millimeters, converted to meters

peer_connection_id = "PeerConnectionID"  # Some identifier for the peer connection
websocket_url = "192.168.3.46"
port = 8765
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
