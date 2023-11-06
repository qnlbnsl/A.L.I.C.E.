from google.cloud import speech_v1p1beta1 as speech

class Transcriber:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe(self, audio):
        audio = speech.RecognitionAudio(content=audio.raw_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code="en-US",
        )
        response = self.client.recognize(config=config, audio=audio)
        for result in response.results:
            return result.alternatives[0].transcript
