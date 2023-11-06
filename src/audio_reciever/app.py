import socket
import subprocess
import wave

# Server details
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345

# Socket initialization
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# FFmpeg command for decoding Opus to raw audio
ffmpeg_command = [
    "ffmpeg",
    "-f",
    "ogg",  # Specify the input is in Opus format
    "-i",
    "pipe:0",  # Read input from stdin
    "-acodec",
    "pcm_s16le",  # Decode to WAV PCM s16le (16-bit signed little endian)
    "-ar",
    "48000",  # Sample rate
    "-ac",
    "8",  # Number of audio channels
    "pipe:1",  # Write output to stdout
]

# Open the FFmpeg process
process = subprocess.Popen(
    ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
)

print("Server is listening...")

# Initialize a buffer to hold the raw audio data
raw_audio_data = bytearray()

if process.stdin is None:
    exit(1)
if process.stdout is None:
    exit(1)
# Initialize a counter to monitor the number of received packets
packet_count = 0

try:
    while True:
        # Receive Opus-encoded audio from socket
        opus_data, addr = server_socket.recvfrom(4096)

        # Increment the packet counter and print a log message
        packet_count += 1
        print(f"Received packet #{packet_count} from {addr}")

        # Write Opus data to FFmpeg's stdin for decoding
        process.stdin.write(opus_data)

        # Check if we're actually getting audio data back
        try:
            raw_data = process.stdout.read(4096)
            if raw_data:
                print(f"Decoded audio data length: {len(raw_data)}")
            else:
                print("No audio data decoded.")
        except IOError:
            # This may happen if the buffer is empty; non-blocking I/O
            pass
except KeyboardInterrupt:
    print("Server stopped by user. Finalizing WAV file...")
finally:
    # Close the FFmpeg process
    process.stdin.close()
    process.terminate()
    process.wait()
    server_socket.close()
    # Save the raw audio data to a WAV file
    with wave.open("output.wav", "wb") as wav_file:
        wav_file.setnchannels(8)  # Set to 8 channels
        wav_file.setsampwidth(2)  # 16-bit samples
        wav_file.setframerate(48000)  # 48kHz sample rate
        wav_file.writeframes(raw_audio_data)
    print("Audio saved to 'output.wav'.")
