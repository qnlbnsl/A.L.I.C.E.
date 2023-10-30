from multiprocessing import Process, Queue
import socket
import json
import numpy as np
from enums import port
from stt.record import record


def receive_data(client_socket, length):
    data = b""
    while len(data) < length:
        packet = client_socket.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def on_receive(client_socket, audio_queue: Queue):
    while True:
        # Receive the length of the metadata bytes
        metadata_length_bytes = receive_data(client_socket, 4)
        if metadata_length_bytes is None:
            print("Connection closed by the client.")
            break

        metadata_length = int.from_bytes(metadata_length_bytes, byteorder="big")

        # Receive the metadata bytes
        metadata_bytes = receive_data(client_socket, metadata_length)
        if metadata_bytes is None:
            print("Connection closed by the client.")
            break

        # Deserialize metadata
        metadata_str = metadata_bytes.decode("utf-8")
        metadata = json.loads(metadata_str)

        # Receive the length of the audio bytes
        audio_length_bytes = receive_data(client_socket, 4)
        if audio_length_bytes is None:
            print("Connection closed by the client.")
            break

        audio_length = int.from_bytes(audio_length_bytes, byteorder="big")

        # Receive the audio bytes
        audio_bytes = receive_data(client_socket, audio_length)
        if audio_bytes is None:
            print("Connection closed by the client.")
            break

        # Convert audio bytes to NumPy array
        audio_data_np = np.frombuffer(audio_bytes, dtype=np.int16)

        print(f"Received metadata: {metadata}")
        print(f"Received audio data: {audio_data_np}")
        record(
            audio_bytes,
            metadata.get("channels"),
            metadata.get("sample_width"),
            metadata.get("rate"),
        )
        audio_queue.put(
            {
                "AudioData": audio_data_np,
                "duration": metadata["duration"],
                "theta": metadata["theta"],
                "phi": metadata["phi"],
                "channels": metadata["channels"],
                "sample_width": metadata["sample_width"],
                "rate": metadata["rate"],
            }
        )


def on_send(client_socket, response_queue: Queue):
    while True:
        if not response_queue.empty():
            message = response_queue.get()
            message_str = json.dumps(message)
            message_bytes = message_str.encode("utf-8")
            message_length = len(message_bytes)
            message_length_bytes = message_length.to_bytes(4, byteorder="big")
            client_socket.sendall(message_length_bytes + message_bytes)


def handle_client_connection(client_socket, audio_queue: Queue, response_queue: Queue):
    receive_thread = Process(target=on_receive, args=(client_socket, audio_queue))
    send_thread = Process(target=on_send, args=(client_socket, response_queue))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()


def server(audio_queue: Queue, payload_queue: Queue, response_queue: Queue):
    SERVER_HOST = "0.0.0.0"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, port))
    server_socket.listen(1)

    print(f"Listening on {SERVER_HOST}:{port}...")

    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    handle_client_connection(client_socket, audio_queue, response_queue)
