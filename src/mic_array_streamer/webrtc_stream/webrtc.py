import asyncio
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from webrtc_stream.system_mic import SystemMic  # Assuming your SystemMic class is in system_mic.py

async def rtc(pc, SIGNALING_SERVER_IP):
    # Assume we have a signaling channel that allows us to send and receive messages
    async with websockets.connect(SIGNALING_SERVER_IP) as ws:
        # Add the SystemMic track to the peer connection
        audio_track = SystemMic()
        pc.addTrack(audio_track)

        # Create an offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await ws.send(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))

        # Wait for the answer
        answer = json.loads(await ws.recv())
        await pc.setRemoteDescription(RTCSessionDescription(sdp=answer["sdp"], type=answer["type"]))

        # Wait for the connection to be established
        await asyncio.sleep(30)

        # Stop the audio track
        audio_track.stop()
