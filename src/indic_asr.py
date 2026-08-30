import torch
import librosa

from transformers import AutoModel


class IndicASR:

    def __init__(
        self,
        model_name="ai4bharat/indic-conformer-600m-multilingual"
    ):

        self.model_name = model_name

        print("Loading IndicConformer...")

        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        self.model.eval()

        print("IndicConformer loaded.")

    def audio_to_text(
        self,
        audio_path: str,
        language="hi"
    ) -> str:

        # Load audio at 16 kHz
        audio, sample_rate = librosa.load(
            audio_path,
            sr=16000,
            mono=True
        )

        # Convert to tensor
        audio = torch.tensor(
            audio,
            dtype=torch.float32
        )

        # Add batch/channel dimension
        audio = audio.unsqueeze(0)

        # IndicConformer inference
        with torch.no_grad():

            transcription = self.model(
                audio,
                language,
                "ctc"
            )

        return transcription.strip()