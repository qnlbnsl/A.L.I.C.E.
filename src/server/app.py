import asyncio
import websockets
import base64
import json
from pyogg import OpusEncoder, OpusDecoder
from typing import Text
from logger import logger

from audio_processing.process import process_audio, raw_audio_queue
from stt.stt import transcribe
from assistant.process import initialize_assistant
from assistant.concept_store.parse_concept import parse_concept
from assistant.intents.parse_intent import parse_intent
from assistant.questions.parse_question import parse_question

from enums import RATE

# TODO: Update as per the TTS sample rate and channels
# Create an Opus encoder/decoder
opus_encoder = OpusEncoder()
opus_decoder = OpusDecoder()

# The following are exported in a very weird fashion.
# Pylance is unable to detect these functions
opus_encoder.set_application("restricted_lowdelay")  # type: ignore

opus_encoder.set_sampling_frequency(RATE)  # type: ignore
opus_decoder.set_sampling_frequency(RATE)  # type: ignore

opus_encoder.set_channels(1)  # type: ignore
opus_decoder.set_channels(1)  # type: ignore

# Create an asyncio Event object
playback_event = asyncio.Event()


def decode_audio(encoded_data: str) -> bytes | None:
    """
    Decode the base64 and Opus encoded audio data.
    :param encoded_data: Base64 encoded string of Opus audio data.
    :return: Decoded raw audio bytes.
    """
    base64_data = encoded_data.encode("utf-8")
    # Decode the base64 data to get Opus encoded bytes
    opus_data = base64.b64decode(base64_data)
    try:
        # Then, decode the Opus bytes to get raw audio data
        # logger.debug(f"Decoding audio of length: {len(opus_data)}")
        return opus_decoder.decode(bytearray(opus_data))  # type: ignore

    except Exception as e:
        logger.error(f"Error in audio decoding: {e}")
        return None


async def receiver(websocket: websockets.WebSocketServerProtocol, path: str):
    print("Client connected.")
    try:
        while True:
            message = await websocket.recv()
            # logger.debug(f"Received: {message}")
            data = json.loads(message)
            if data["type"] == "audio":
                # Decode the base64 message
                decoded_audio = decode_audio(data["data"])
                if decoded_audio is None:
                    logger.error("Error in audio decoding. decoded_audio is None")
                    continue
                # logger.debug(f"Received and added audio to queue")
                await raw_audio_queue.put(decoded_audio)
                # Write the decoded bytes to the WAV file
            elif data["type"] == "config":
                logger.debug(f"Received config: {data}")
            else:
                logger.debug(f"Received unknown message: {data}")
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")


async def main():
    # Start the WebSocket server
    server = await websockets.serve(
        lambda ws, path: receiver(ws, path), "0.0.0.0", 8080
    )
    logger.debug("Server started.")

    # Run the audio processing in a separate asyncio task if it's an async function
    # If process_audio is not an async function, consider converting it to be compatible with asyncio
    # or use run_in_executor to run it in a threadpool executor for blocking IO-bound tasks
    audio_process_task = asyncio.create_task(process_audio())
    stt_process_task = asyncio.create_task(transcribe())
    assistant_task = asyncio.create_task(initialize_assistant())
    concept_task = asyncio.create_task(parse_concept())
    intent_task = asyncio.create_task(parse_intent())
    question_task = asyncio.create_task(parse_question())
    # Wait for the server to close and the STT process to complete
    await asyncio.gather(
        server.wait_closed(),
        stt_process_task,
        assistant_task,
        concept_task,
        intent_task,
        question_task,
    )

    # If server.wait_closed() completes, cancel the audio processing task
    audio_process_task.cancel()
    try:
        await audio_process_task  # Wait for the task cancellation to complete
    except asyncio.CancelledError:
        logger.debug("Audio processing task cancelled.")


if __name__ == "__main__":
    asyncio.run(main())
