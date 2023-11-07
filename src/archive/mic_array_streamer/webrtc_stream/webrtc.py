import asyncio
import json
from time import sleep
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from webrtc_stream.system_mic import (
    SystemMic,
)  # Assuming your SystemMic class is in system_mic.py

from enums import RATE, CHANNELS
from logger import logger


async def rtc(pc: RTCPeerConnection, SIGNALING_SERVER_IP):
    logger.info("trying to connect over websockets...")
    # Assume we have a signaling channel that allows us to send and receive messages
    async with websockets.connect(f"ws://" + SIGNALING_SERVER_IP + ":8080/ws") as ws:
        logger.info("connected over websockets!!!")
        # Add the SystemMic track to the peer connection
        audio_track = SystemMic(rate=RATE, channels=CHANNELS, width=2, layout="7.1")
        pc.addTrack(audio_track)
        pc.createDataChannel("meta")
        # Create an offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await ws.send(
            json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            )
        )

        # Wait for the answer
        answer = json.loads(await ws.recv())
        await pc.setRemoteDescription(
            RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
        )

        logger.info("sleeping")
        # Wait for the connection to be established
        sleep(3)

        logger.info("stopping track")
        # Stop the audio track
        audio_track.stop()
        logger.info("stopped")
