from faster_whisper import WhisperModel
import torch
import whisper

model_path = "large-v2"


def force_cudnn_initialization():
    s = 32
    dev = torch.device("cuda")
    torch.nn.functional.conv2d(
        torch.zeros(s, s, s, s, device=dev), torch.zeros(s, s, s, s, device=dev)
    )


force_cudnn_initialization()
# model = WhisperModel(
#     model_size_or_path=model_path, device="cuda", compute_type="float16"
# )

whisper_model = "medium.en"
model_ = whisper.load_model(whisper_model, device="cuda")

print("transcribing")
# segments, info = model.transcribe("test1.wav", beam_size=5, vad_filter=True)
data = model_.transcribe("test1.wav", temperature=0.2, fp16=torch.cuda.is_available())

# print(
#     "Detected language '%s' with probability %f"
#     % (info.language, info.language_probability)
# )

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

print(f"whisper segments: {data}")
