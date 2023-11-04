import asyncio
import json
from aiohttp import web

from logger import logger

# import websockets
from aiortc import (
    RTCPeerConnection,
    MediaStreamTrack,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)

from audio_stream.server_audio_track import ServerAudioTrack
from audio_stream.media_recorder import MediaRecorder


async def index(request):
    logger.info("Request Received: ", request.method, request.url)
    return web.Response(content_type="text/html", text="Healthy")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Assume we only have one peer connection for simplicity
    pc = RTCPeerConnection(
        RTCConfiguration([RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )
    audio_track = ServerAudioTrack()
    recorder = MediaRecorder(rate=44100, channels=8, width=2)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            logger.info("Received message:", message)
            if isinstance(message, str) and message.startswith("ping"):
                await channel.send("pong" + message[4:])

    @pc.on("track")
    def on_track(track):
        logger.info(f"Received track {track.kind}")
        pc.addTrack(audio_track)

        @track.on("ended")
        async def on_ended():
            logger.info(f"Track {track.kind} ended")
            # await recorder.stop()

    # Handle offer from the client
    async for message in ws:
        data = json.loads(message.data)
        if "sdp" in data:
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await pc.setRemoteDescription(offer)

            # Prepare local media
            # await recorder.start()

            # Send answer
            answer = await pc.createAnswer()
            if answer is None:
                continue
            await pc.setLocalDescription(answer)
            await ws.send_str(
                json.dumps(
                    {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
                )
            )

        elif "candidate" in data:
            pass  # Handle ICE candidates (not shown here)

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
