from faster_whisper import WhisperModel


model_path = "turicas/faster-whisper-large-v3"


model = WhisperModel(
    model_size_or_path=model_path, device="cuda", compute_type="float16"
)

print("transcribing")
segments, info = model.transcribe("test.wav", beam_size=5, vad_filter=True)

print(
    "Detected language '%s' with probability %f"
    % (info.language, info.language_probability)
)

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
