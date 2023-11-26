import time
import sys
import queue


class ProgressBar:
    def __init__(self, q):
        self.q = q
        self.audio_status = "Silent"
        self.server_status = "Disconnected"
        self.strength = 0

    def update(self):
        while True:
            try:
                message = self.q.get_nowait()
                if "strength" in message:
                    self.strength = message["strength"]
                elif "audio_status" in message:
                    self.audio_status = message["audio_status"]
                elif "server_status" in message:
                    self.server_status = message["server_status"]

                self.draw()
            except queue.Empty:
                pass

            time.sleep(0.1)  # Adjust as needed

    def draw(self):
        bar_length = 20
        filled_length = int(bar_length * self.strength / 100)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        sys.stdout.write(
            f"\rStrength: [{bar}] {self.strength}% | Audio: {self.audio_status} | Server: {self.server_status}"
        )
        sys.stdout.flush()
