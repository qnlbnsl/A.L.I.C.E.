import asyncio
import websockets
import json
import numpy as np
from scipy.signal import resample
from asyncio import Queue

from stt_processor.client import TranscriptionClient

prepped_audio_queue = Queue()

rs_data = []


async def whisper_live_client(uri: str):
    client = TranscriptionClient(
        "localhost", "9090", is_multilingual=True, lang="hi", translate=True
    )
    await client(prepped_audio_queue)
    # async with websockets.connect(uri) as ws:
    #     print("Connected to WhisperLive server.")
    #     await ws.send(
    #         json.dumps(
    #             {
    #                 "uid": "",
    #                 "multilingual": "true",
    #                 "language": "en",
    #                 "task": "transcribe",
    #             }
    #         )
    #     )
    #     while True:
    #         # Check if there's audio data in the prepped queue
    #         if not prepped_audio_queue.empty():
    #             audio_data = prepped_audio_queue.get()
    #             rs_data.extend(resample_audio(audio_data, 48000, 16000))
    #             # Prepare the message (assuming the server expects JSON)
    #             message = json.dumps(
    #                 {
    #                     "audio_data": rs_data,  # Convert numpy array to list
    #                     # Include other required fields by the server
    #                 }
    #             )

    #             # Send the audio data to the WhisperLive server
    #             await ws.send(message)

    #             # Wait for the server's response
    #             response = await ws.recv()
    #             response_data = json.loads(response)

    #             # Handle the response (for now, just print it)
    #             print("Received transcription:", response_data["transcription"])

    #         else:
    #             # Sleep a bit before checking the queue again
    #             await asyncio.sleep(0.1)


# # Replace 'ws://whisperlive.example.com' with the actual URI of the WhisperLive server
# whisper_live_server_uri = "ws://whisperlive.example.com"


# # Start the WebSocket client
# asyncio.run(whisper_live_client(whisper_live_server_uri))
def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    Resample audio data from original sample rate to target sample rate.

    Parameters:
    audio_data (np.ndarray): The original audio data as a numpy array.
    orig_sr (int): The original sample rate.
    target_sr (int): The target sample rate.

    Returns:
    np.ndarray: Resampled audio data as a numpy array.
    """

    # Calculate the number of samples after resampling
    num_samples = round(len(audio_data) * float(target_sr) / orig_sr)

    # Use scipy.signal.resample to resample the data
    resampled_audio = resample(audio_data, num_samples)

    # The resampled data is in float64 format, but we need to convert it back to int16
    resampled_audio_int16 = np.round(resampled_audio).astype(np.int16)

    return resampled_audio_int16
