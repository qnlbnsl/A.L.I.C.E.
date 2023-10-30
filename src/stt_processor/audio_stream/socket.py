import socket
import json
import numpy as np
from enums import port


def receive_data(client_socket, length):
    data = b""
    while len(data) < length:
        packet = client_socket.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def handle_client_connection(client_socket):
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


def server():
    SERVER_HOST = "0.0.0.0"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, port))
    server_socket.listen(1)

    print(f"Listening on {SERVER_HOST}:{port}...")

    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    handle_client_connection(client_socket)
