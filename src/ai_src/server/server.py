import socket
import multiprocessing
from pydub import AudioSegment
from transcriber import Transcriber

class Server:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.transcriber = Transcriber()

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address} has been established.")
            p = multiprocessing.Process(target=self.handle_client, args=(client_socket,))
            p.start()

    def handle_client(self, client_socket):
        while True:
            audio_data = client_socket.recv(1024)
            if not audio_data:
                break
            audio = AudioSegment.from_file(audio_data, format="opus")
            text = self.transcriber.transcribe(audio)
            print(text)

if __name__ == "__main__":
    server = Server()
    server.start()
