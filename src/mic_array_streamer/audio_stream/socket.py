import json
import socket
import numpy as np
from enums import websocket_url, peer_connection_id, port

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init_connection():
    global client_socket  # Declare ws as global to modify it
    try:
        client_socket.connect((websocket_url, port))
    except Exception as e:
        print(f"An error occurred while connecting to socket : {e}")


def close_connection():
    global client_socket
    client_socket.close()


def send_to_server(audio_bytes, duration, doa_theta, doa_phi):
    global client_socket  # Using the Socket client that was initialized at startup
    metadata = {"duration": duration, "doa_theta": doa_theta, "doa_phi": doa_phi}
    metadata_str = json.dumps(metadata)
    metadata_bytes = metadata_str.encode("utf-8")
    client_socket.sendall(len(metadata_bytes).to_bytes(4, byteorder="big"))
    client_socket.sendall(metadata_bytes)

    # audio_bytes = audio_frame_np.tobytes()
    client_socket.sendall(len(audio_bytes).to_bytes(4, byteorder="big"))
    client_socket.sendall(audio_bytes)
