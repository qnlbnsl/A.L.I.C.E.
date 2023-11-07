import asyncio
import json
from aiohttp import web

from logger import logger
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)

from audio_stream.server_audio_track import ServerAudioTrack
from audio_stream.media_recorder import MediaRecorder

from enums import RATE, CHANNELS


async def index(request: web.Request):
    logger.info("Request Received: ", request.method, request.url)
    return web.Response(content_type="text/html", text="Healthy")


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    pc = RTCPeerConnection(
        RTCConfiguration([RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )
    # Initialize the MediaRecorder with appropriate audio settings
    recorder = MediaRecorder(rate=RATE, channels=CHANNELS, width=2, layout="7.1")
    # Start the recorder
    recorder.start()

    # Create a ServerAudioTrack and pass the recorder to it
    audio_track = ServerAudioTrack(recorder=recorder)
    # Add the ServerAudioTrack to the peer connection
    pc.addTrack(audio_track)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Received track {track.kind}")

        @track.on("ended")
        async def on_ended():
            logger.info(f"Track {track.kind} ended")
            # Stop the recorder when the track ends
            audio_track.stop()

        @track.on("frame")
        def on_frame(frame):
            logger.debug(f"Received frame: {frame}")

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.debug("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            # pcs.discard(pc)

    # Handle offer/answer exchange and ICE candidates
    async for message in ws:
        data = json.loads(message.data)
        # logger.debug(f"Received message: {data}")
        if "sdp" in data:
            # ... existing SDP handling code ...
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await pc.setRemoteDescription(offer)

            # Send answer
            answer = await pc.createAnswer()
            if answer is None:
                logger.debug("Answer is None")
                continue
            await pc.setLocalDescription(answer)
            await ws.send_str(
                json.dumps(
                    {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
                )
            )
        elif "candidate" in data:
            # ... existing ICE candidate handling code ...
            pass
        elif "action" in data and data["action"] == "close":
            logger.info("Client requested to close the connection")
            await pc.close()

    return ws


def run_server():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    try:
        web.run_app(app, port=8080)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
        exit(0)


if __name__ == "__main__":
    run_server()
