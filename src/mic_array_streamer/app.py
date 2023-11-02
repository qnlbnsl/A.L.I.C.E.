# Multiprocessing
from multiprocessing import Process

from audio.audio_processing import process_audio
from audio.capture import initialize_audio
from audio_stream.server_communication import initialize_server_communication
import webrtcvad

from enums import local_audio_queue, stream_queue

def main():

    try:
        # Create and configure Voice Activity Detection
        vad = webrtcvad.Vad(3)
    except Exception as e:
        print(f"Could not initialize VAD: {e}")
        exit()


    # Process that listens to the mic
    # audio_process = Process(target=initialize_audio, args=())
    initialize_audio()
    # Process that processes the audio
    # processing_thread = Process(target=process_audio, args=(vad,))
    
    # # Process that streams the audio (you need to define this)
    # streaming_thread = Process(target=initialize_server_communication, args=())

    # Start the processes
    # audio_process.start()
    # processing_thread.start()
    # streaming_thread.start()

    # Wait for processes to complete
    # audio_process.join()
    # processing_thread.join()
    # streaming_thread.join()

if __name__ == "__main__":
    main()
