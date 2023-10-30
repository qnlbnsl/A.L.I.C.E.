from multiprocessing import Process, Queue

from audio_stream.socket import server


def main():
    audio_queue = Queue()
    payload_queue = Queue()
    response_queue = Queue()

    server_process = Process(
        target=server, args=(audio_queue, payload_queue, response_queue)
    )
    try:
        server_process.start()
        server_process.join()
        audio_queue.put(None)

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting.")
        server_process.terminate()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        server_process.terminate()
        exit(1)


if __name__ == "__main__":
    main()
