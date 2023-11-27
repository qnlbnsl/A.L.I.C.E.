import pyaudio as pa
import sounddevice as sd


def get_audio_handler() -> pa.PyAudio:
    return pa.PyAudio()


def open(
    format,
    channels,
    rate,
    input,
    frames_per_buffer,
    stream_callback,
    input_device_index=None,
):
    return get_audio_handler().open(
        format=format,
        channels=channels,
        rate=rate,
        input=input,
        frames_per_buffer=frames_per_buffer,
        stream_callback=stream_callback,
        input_device_index=input_device_index,
    )


def sd_open(format, device, samplerate, callback):
    return sd.InputStream(
        device=device,
        channels=1,
        samplerate=samplerate,
        callback=callback,
        dtype=format,
    )
