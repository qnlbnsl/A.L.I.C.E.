# Multiprocessing
from multiprocessing import Process
from aiortc import RTCPeerConnection
from audio.audio_processing import process_audio
from audio.capture import initialize_audio, initialize_audio_file
from audio_stream.server_communication import initialize_server_communication
from webrtc_stream.webrtc import rtc
import webrtcvad
import asyncio

from enums import local_audio_queue, stream_queue

async def main():

    # try:
    #     # Create and configure Voice Activity Detection
    #     vad = webrtcvad.Vad(3)
    # except Exception as e:
    #     print(f"Could not initialize VAD: {e}")
    #     exit()

    pc = RTCPeerConnection()
    await rtc(pc, "192.168.3.46")
    # webrtc_process = Process(target=rtc, args=(pc,"192.168.3.46"))

    # Process that listens to the mic
    # audio_process = Process(target=initialize_audio, args=())
    # initialize_audio_file("/home/qnlbnsl/ai_voice_assistant/sample-15s.wav")
    # initialize_audio()
    # Process that processes the audio
    # processing_thread = Process(target=process_audio, args=(vad,))
    
    # # Process that streams the audio (you need to define this)
    # streaming_thread = Process(target=initialize_server_communication, args=())

    # Start the processes
    # webrtc_process.start()
    # audio_process.start()
    # processing_thread.start()
    # streaming_thread.start()

    # Wait for processes to complete
    # webrtc_process.join()
    # audio_process.join()
    # processing_thread.join()
    # streaming_thread.join()

if __name__ == "__main__":
   asyncio.run(main())
    # main()
