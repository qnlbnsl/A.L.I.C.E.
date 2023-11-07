import asyncio
import websockets
import base64
import wave


async def audio_receiver(websocket, path, output_filename):
    print("Client connected.")
    # Set up the WAV file parameters
    sample_rate = 48000  # or the rate you are using on the client side
    channels = 8  # or the number of channels you are using
    sample_width = 2  # float32 has a sample width of 4 bytes

    # Initialize the wave file outside the try block to ensure it is in scope for the finally block
    wav_file = wave.open(output_filename, "wb")
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(sample_width)
    wav_file.setframerate(sample_rate)

    try:
        while True:
            message = await websocket.recv()
            # Decode the base64 message
            audio_data = base64.b64decode(message)
            # Write the decoded bytes to the WAV file
            wav_file.writeframes(audio_data)
            print(f"Received and wrote audio data of size: {len(audio_data)} bytes")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected with exception: {e}")
    finally:
        # Ensure that the wave file is properly closed even if there is an error
        wav_file.close()
        print(f"Audio data written to {output_filename}")


async def main():
    output_filename = "received_audio.wav"
    server = await websockets.serve(
        lambda ws, path: audio_receiver(ws, path, output_filename), "0.0.0.0", 8080
    )
    print("Server started.")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
