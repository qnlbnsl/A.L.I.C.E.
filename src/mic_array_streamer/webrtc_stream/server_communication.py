from multiprocessing import Queue

from webrtc import init_connection, send_to_server

async def initialize_webrtc(audio_queue: Queue):
    await init_connection()
    while True:
        # Check if there is something in the queue
        if not audio_queue.empty():
            data = audio_queue.get()

            audio_data = data["AudioData"]
            duration = data["Duration"]
            theta = data["theta"]
            phi = data["phi"]

            # Now do something with the data, such as send it to the server
            await send_to_server(audio_data, duration, theta, phi)

