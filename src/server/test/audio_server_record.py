import asyncio
from multiprocessing import Process, Value
import ctypes
from websockets.sync.server import serve, ServerConnection
import websockets
import base64
import wave
import json
from logger import logger
from pyogg import OpusEncoder, OpusDecoder  # type: ignore
import numpy as np

from numpy.typing import NDArray

from logger import logger

# from stt.stt import decoded_audio_queue

from enums import CHUNK, RATE

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


def decode_audio(encoded_data: str) -> NDArray[np.int16] | None:
    """
    Decode the base64 and Opus encoded audio data.
    :param encoded_data: Base64 encoded string of Opus audio data.
    :return: Decoded raw audio bytes.
    """
    # base64_data = encoded_data.encode("utf-8")
    # Decode the base64 data to get Opus encoded bytes
    opus_data = base64.b64decode(encoded_data.encode("utf-8"))
    try:
        # Then, decode the Opus bytes to get raw audio data
        # logger.debug(f"Decoding audio of length: {len(opus_data)}")

        decoded_data = opus_decoder.decode(bytearray(opus_data))  # type: ignore
        if decoded_data is not None:
            decoded_data = np.frombuffer(decoded_data, dtype=np.int16)
            assert len(decoded_data) == CHUNK
            # logger.debug(f"Decoded audio of length: {len(decoded_data)}")
        else:
            logger.error("Error in audio decoding. decoded_data is None")
        return decoded_data
    except Exception as e:
        logger.error(f"Error in audio decoding: {e}")
        return None


def receiver(websocket: ServerConnection, stop_flag):
    print("Client connected.")
    sample_rate = 16000
    channels = 1
    sample_width = 2
    output_filename = "received_audio.wav"
    wav_file = wave.open(output_filename, "wb")
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(sample_width)
    wav_file.setframerate(sample_rate)

    try:
        
        while not stop_flag.value:
            message = websocket.recv()
            data = json.loads(message)
            if data["type"] == "audio":
                audio_data = decode_audio(data["data"])
                if audio_data is None:
                    logger.error("Error in audio decoding. audio_data is None")
                    continue
                wav_file.writeframes(audio_data.tobytes())
                logger.debug(
                    f"Received and wrote audio data of size: {len(audio_data)} bytes"
                )
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f"Client disconnected with exception: {e}")
    except asyncio.CancelledError as e:
        logger.debug("Receive Socket operation cancelled")
    finally:
        wav_file.close()
        logger.debug(f"Audio data written to {output_filename}")


def main():
    stop_flag = Value(ctypes.c_bool, False)
    server_process = Process(
        target=lambda: serve(
            lambda ws: receiver(ws, stop_flag), "0.0.0.0", 8765
        ).serve_forever()
    )

    try:
        server_process.start()
        while True:
            pass
    except KeyboardInterrupt:
        stop_flag.value = True
        server_process.terminate()
        server_process.join()


if __name__ == "__main__":
    main()
