import torch
import torchaudio
from transformers import pipeline

# Check if GPU is available
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Initialize the ASR pipeline with Whisper model
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",
    chunk_length_s=30,
    device=device
)

def speech_to_text(audio_file_path):
    # Load the audio file
    waveform, sampling_rate = torchaudio.load(audio_file_path)
    print(f"Audio loaded! Shape: {waveform.shape}, Sample rate: {sampling_rate}")

    # Resample the audio to 16 kHz (Whisper expects this sampling rate)
    resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
    waveform = resampler(waveform)

    # Prepare the audio input for the pipeline
    audio_input = {"raw": waveform.numpy()[0], "sampling_rate": 16000} 

    # Generate transcription
    prediction = pipe(audio_input, batch_size=16, language='en')["text"]

    # Output the transcription
    return prediction