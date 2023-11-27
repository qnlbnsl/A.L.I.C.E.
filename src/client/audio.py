import pyaudio as pa


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
