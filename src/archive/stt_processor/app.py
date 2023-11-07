from multiprocessing import Process, Queue

# from audio_stream.socket import server
from audio_stream.webrtc import run_server

from logger import logger


def main():
    audio_queue = Queue()

    try:
        audio_queue.put(None)
        run_server()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
        exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
