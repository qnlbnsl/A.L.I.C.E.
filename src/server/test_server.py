import asyncio
import websockets
import base64
import wave
import json
from logger import logger


async def receiver(websocket, path, output_filename):
    print("Client connected.")
    # Set up the WAV file parameters
    sample_rate = 16000  # or the rate you are using on the client side
    channels = 1  # or the number of channels you are using
    sample_width = 2  # int16 has a sample width of 2 bytes, whereas float32 has sample width of 4 byte

    # Initialize the wave file outside the try block to ensure it is in scope for the finally block
    wav_file = wave.open(output_filename, "wb")
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(sample_width)
    wav_file.setframerate(sample_rate)

    try:
        while True:
            message = await websocket.recv()
            # logger.debug(f"Received: {message}")
            data = json.loads(message)
            if data["type"] == "audio":
                audio_data = base64.b64decode(data["data"])
                wav_file.writeframes(audio_data)
                # Decode the base64 message
                # Write the decoded bytes to the WAV file
                logger.debug(
                    f"Received and wrote audio data of size: {len(audio_data)} bytes"
                )
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    finally:
        # Ensure that the wave file is properly closed even if there is an error
        wav_file.close()
        logger.debug(f"Audio data written to {output_filename}")


async def main():
    output_filename = "received_audio.wav"
    server = await websockets.serve(
        lambda ws, path: receiver(ws, path, output_filename), "0.0.0.0", 8080
    )
    logger.debug("Server started.")
    try:
        await server.wait_closed()
    except asyncio.CancelledError as e:
        logger.debug("Server cancelled")
    except Exception as e:
        logger.debug(f"Unknown Server exception: {e}")
    except KeyboardInterrupt:
        logger.debug("SIGTERM received. Shutting down.")


if __name__ == "__main__":
    asyncio.run(main())
