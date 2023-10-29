import webrtcvad
import wave
vad = webrtcvad.Vad(3)

def is_speech(frame, sample_rate):
    # return True
    return vad.is_speech(buf=frame, sample_rate=sample_rate)

def send_to_server(data):
    return True

