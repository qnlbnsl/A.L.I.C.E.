from aiortc import MediaStreamTrack, RTCSessionDescription, RTCPeerConnection
from aiortc.mediastreams import AudioStreamTrack as aiortc_AudioStreamTrack
import json
import websockets



peer_connection = RTCPeerConnection()
peer_connection_id = "PeerConnectionID"  # Some identifier for the peer connection
websocket_url = 'ws://your_signaling_server_url'
ws = None  # Global WebSocket client

async def init_connection():
    global ws  # Declare ws as global to modify it
    ws = await websockets.connect(websocket_url)
    offer = await peer_connection.createOffer()
    await peer_connection.setLocalDescription(offer)
    await ws.send(json.dumps({"offer": offer.sdp, "id": peer_connection_id}))
    response = await ws.recv()
    response_data = json.loads(response)
    answer = RTCSessionDescription(sdp=response_data["answer"], type="answer")
    await peer_connection.setRemoteDescription(answer)

class CustomAudioStreamTrack(aiortc_AudioStreamTrack):
    def __init__(self, audio_frame, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_frame = audio_frame  # NumPy array containing audio data

    async def recv(self):
        # Populate this method based on your requirements
        pass

async def send_to_server(audio_frame, doa_theta, doa_phi):
    global ws  # Using the WebSocket client that was initialized at startup
    audio_track = CustomAudioStreamTrack(audio_frame)
    peer_connection.addTrack(audio_track)

    # Send metadata over data channel
    data_channel = peer_connection.createDataChannel("metadata")
    metadata = json.dumps({"theta": doa_theta, "phi": doa_phi})
    data_channel.send(metadata)

    # If you have signaling messages specific to each data send, you can use ws here.