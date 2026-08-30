import librosa

from transformers import pipeline


class ASR:

    def __init__(
        self,
        model_name="openai/whisper-medium"
    ):

        self.model_name = model_name

        print(
            f"Loading Whisper model: {model_name}"
        )

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_name
        )

        print("Whisper model loaded.")

    def audio_to_text(
        self,
        audio_path: str
    ) -> str:

        # Load audio at 16 kHz
        audio, sample_rate = librosa.load(
            audio_path,
            sr=16000,
            mono=True
        )

        # Whisper inference
        result = self.pipe(audio)

        return result["text"].strip()