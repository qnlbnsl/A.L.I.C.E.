import socket
import pyaudio
import numpy as np

class Client:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=1024)

    def start(self):
        self.client_socket.connect((self.host, self.port))
        while True:
            data = self.stream.read(1024)
            self.client_socket.sendall(data)

if __name__ == "__main__":
    client = Client()
    client.start()
