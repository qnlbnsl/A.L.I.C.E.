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


async def index(request):
    logger.info("Request Received: ", request.method, request.url)
    return web.Response(content_type="text/html", text="Healthy")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    pc = RTCPeerConnection(
        RTCConfiguration([RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )
    # Initialize the MediaRecorder with appropriate audio settings
    recorder = MediaRecorder(rate=44100, channels=8, width=2, layout="7.1")
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
            # Renegotiate the connection
            await renegotiate()

    async def renegotiate():
        # Create a new offer and send it to the remote peer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await ws.send_str(
            json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            )
        )

    # Handle offer/answer exchange and ICE candidates
    async for message in ws:
        data = json.loads(message.data)
        if "sdp" in data:
            # ... existing SDP handling code ...
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await pc.setRemoteDescription(offer)

            # Send answer
            answer = await pc.createAnswer()
            if answer is None:
                logger.debug("Answer is None")
                return
            await pc.setLocalDescription(answer)
            await ws.send_str(
                json.dumps(
                    {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
                )
            )
        elif "candidate" in data:
            # ... existing ICE candidate handling code ...
            pass

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
