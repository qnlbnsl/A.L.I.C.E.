# Multiprocessing
from multiprocessing import Process, Queue

from audio.audio_processing import initialize_audio
from audio_stream.server_communication import initialize_server_communication


def main():
    # Create a multiprocessing Queue
    audio_queue = Queue()

    # Create two Processes
    audio_process = Process(target=initialize_audio, args=(audio_queue,))
    server_process = Process(
        target=initialize_server_communication, args=(audio_queue,)
    )

    # Start Processes
    audio_process.start()
    server_process.start()

    # Wait for audio_process to finish processing
    audio_process.join()

    # Signal to server_process that audio_process is done
    audio_queue.put(None)

    # Wait for server_process to finish sending all data
    server_process.join()


if __name__ == "__main__":
    main()
