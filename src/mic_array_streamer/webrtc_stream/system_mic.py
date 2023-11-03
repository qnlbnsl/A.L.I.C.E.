from av import AudioFrame
import pyaudio
import av
import numpy as np

from threading import Thread, Event, Lock
from aiortc.mediastreams import MediaStreamTrack


class SystemMic(MediaStreamTrack):
    kind = "audio"
    
    def __init__(self):
        super().__init__()
        
        self.kind         = "audio"
        self.RATE         = 44100
        self.AUDIO_PTIME  = 0.020  # 20ms audio packetization
        self.SAMPLES      = int(self.AUDIO_PTIME * self.RATE)
        self.FORMAT       = pyaudio.paInt32
        self.CHANNELS     = 8  # Set to 8 channels for the mic array
        self.CHUNK        = int(self.RATE * self.AUDIO_PTIME)
        self.INDEX        = 0
        self.FORMATAF     = 's32'  # Assuming 's32' corresponds to pyaudio.paInt32
        self.LAYOUT       = '7.1'  # Use '7.1' as a placeholder for 8 channels
        self.sampleCount  = 0

        self.audio        = pyaudio.PyAudio()
        self.stream       = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                            input=True, input_device_index=self.INDEX,
                                            frames_per_buffer=self.CHUNK)
        #thread
        self.micData          = None
        self.micDataLock      = Lock()
        self.newMicDataEvent  = Event()
        self.newMicDataEvent.clear()
        self.running = Event()  # Initialize the running flag
        self.captureThread    = Thread(target=self.capture)
        self.running.set() 
        self.captureThread.start()
        

    def capture(self):
        while True:
            data  = np.fromstring(self.stream.read(self.CHUNK),dtype=np.int32) # type: ignore
            
            with self.micDataLock:
                self.micData = data
                self.newMicDataEvent.set()
    
        
    async def recv(self):
        newMicData = None
            
        self.newMicDataEvent.wait()

        with self.micDataLock:
            data  = self.micData
            if data is None:
                print("no data")
                return
            data  = (data/2).astype('int32')
            data  = np.array([(data>>16).astype('int16')])
            self.newMicDataEvent.clear()
        
        frame   = av.AudioFrame.from_ndarray(data, self.FORMATAF, layout=self.LAYOUT)
        frame.pts         = self.sampleCount
        frame.rate        = self.RATE
        self.sampleCount += frame.samples

        return frame

    # def stop(self):
    #     super.stop()
    #     self.captureThread.kill()

    def stop(self):
        self.running.clear()  # Clear the running flag to stop the thread
        self.captureThread.join()  # Wait for the thread to finish
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        super().stop()  # Call the superclass stop method if it exists