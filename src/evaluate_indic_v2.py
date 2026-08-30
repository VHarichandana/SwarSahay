import os
import json
import csv
import time
import traceback

import torch
import librosa

from jiwer import wer
from transformers import AutoModel

from text_normalizer import normalize_text

MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"

MANIFEST_PATH = "data/asr_test_set/manifest.json"

OUTPUT_PATH = (
    "data/asr_test_set/phase1.2/"
    "asr_results_indic_v2.csv"
)

AUDIO_DIR = "data/asr_test_set/audio"

TARGET_SAMPLE_RATE = 16000

LANGUAGE = "hi"

DECODING_MODE = "ctc"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


def load_manifest():

    with open(
        MANIFEST_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_model():

    print()
    print("Loading IndicConformer...")

    print(
        "Model    :",
        MODEL_NAME
    )

    print(
        "Language :",
        LANGUAGE
    )

    print(
        "Decoding :",
        DECODING_MODE
    )

    print(
        "Device   :",
        DEVICE
    )

    try:

        model = AutoModel.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True
        )

        model.eval()

        print()
        print(
            "IndicConformer loaded successfully."
        )

        print(
            "Model type:",
            type(model)
        )

        try:

            model.to(DEVICE)

            print(
                "Model moved to:",
                DEVICE
            )

        except Exception as move_error:

            print(
                "Model .to(device) skipped:"
            )

            print(
                repr(move_error)
            )

        return model

    except Exception as e:

        print()
        print("=" * 60)
        print("MODEL LOADING FAILED")
        print("=" * 60)

        print(
            "Exception type:",
            type(e).__name__
        )

        print(
            "Exception:",
            repr(e)
        )

        traceback.print_exc()

        raise


def load_audio(audio_path):

    print()
    print(
        "Loading audio:",
        audio_path
    )

    audio, sample_rate = librosa.load(
        audio_path,
        sr=TARGET_SAMPLE_RATE,
        mono=True
    )

    if audio is None:

        raise RuntimeError(
            "librosa returned None"
        )

    if len(audio) == 0:

        raise RuntimeError(
            "Audio contains zero samples"
        )

    duration = (
        len(audio)
        / sample_rate
    )

    print(
        "Sample rate :",
        sample_rate
    )

    print(
        "Samples     :",
        len(audio)
    )

    print(
        "Duration    :",
        f"{duration:.4f}",
        "sec"
    )

    print(
        "Audio shape :",
        audio.shape
    )

    return (
        audio,
        sample_rate,
        duration
    )


def inspect_model(model):

    print()
    print("=" * 60)
    print("MODEL INSPECTION")
    print("=" * 60)

    print(
        "Python class:",
        type(model)
    )

    print(
        "Module:",
        type(model).__module__
    )

    interesting = []

    for name in dir(model):

        if name.startswith("_"):
            continue

        keywords = [
            "trans",
            "infer",
            "recogn",
            "decode",
            "predict",
            "ctc",
            "rnnt",
            "audio",
            "speech"
        ]

        if any(
            keyword in name.lower()
            for keyword in keywords
        ):

            interesting.append(name)

    print()
    print(
        "Relevant model methods:"
    )

    if interesting:

        for name in interesting:

            print(
                "  -",
                name
            )

    else:

        print(
            "  No obvious transcription method found."
        )

    print("=" * 60)


def run_model(
    model,
    wav
):

    print()
    print(
        "Attempting IndicConformer inference..."
    )

    try:

        print(
            "Trying:"
        )

        print(
            "model(wav, LANGUAGE, DECODING_MODE)"
        )

        with torch.no_grad():

            result = model(
                wav,
                LANGUAGE,
                DECODING_MODE
            )

        print()
        print(
            "Model call succeeded."
        )

        print(
            "Output type:",
            type(result)
        )

        print(
            "Raw output:",
            repr(result)
        )

        return result

    except Exception as e:

        print()
        print(
            "MODEL CALL FAILED"
        )

        print(
            "Exception type:",
            type(e).__name__
        )

        print(
            "Exception:",
            repr(e)
        )

        traceback.print_exc()

        raise


def output_to_text(result):

    if isinstance(
        result,
        str
    ):

        return result.strip()

    if isinstance(
        result,
        (list, tuple)
    ):

        if len(result) == 0:

            return ""

        first = result[0]

        if isinstance(
            first,
            str
        ):

            return first.strip()

        result = first

    if isinstance(
        result,
        dict
    ):

        possible_keys = [
            "text",
            "transcription",
            "transcript",
            "prediction",
            "predictions"
        ]

        for key in possible_keys:

            if key in result:

                value = result[key]

                if isinstance(
                    value,
                    str
                ):

                    return value.strip()

                return str(value).strip()

    for attr in [
        "text",
        "transcription",
        "transcript",
        "prediction"
    ]:

        if hasattr(
            result,
            attr
        ):

            value = getattr(
                result,
                attr
            )

            if isinstance(
                value,
                str
            ):

                return value.strip()

    return str(
        result
    ).strip()


def transcribe(
    audio_path,
    model
):

    (
        audio,
        sample_rate,
        duration
    ) = load_audio(
        audio_path
    )

    wav = torch.tensor(
        audio,
        dtype=torch.float32
    )

    print(
        "Tensor shape:",
        wav.shape
    )

    wav = wav.unsqueeze(0)

    print(
        "Batched shape:",
        wav.shape
    )

    wav = wav.to(
        DEVICE
    )

    print(
        "Tensor device:",
        wav.device
    )

    if (
        DEVICE.type == "cuda"
    ):

        torch.cuda.synchronize()

    start = time.perf_counter()

    result = run_model(
        model,
        wav
    )

    if (
        DEVICE.type == "cuda"
    ):

        torch.cuda.synchronize()

    end = time.perf_counter()

    inference_time = (
        end - start
    )

    predicted = output_to_text(
        result
    )

    if duration > 0:

        rtf = (
            inference_time
            / duration
        )

    else:

        rtf = 0.0

    return (
        predicted,
        duration,
        inference_time,
        rtf
    )


def evaluate():

    print("=" * 60)
    print(
        "INDICCONFORMER ASR EVALUATION - PHASE 1.2"
    )
    print("=" * 60)

    print()
    print(
        "Model    :",
        MODEL_NAME
    )

    print(
        "Language :",
        LANGUAGE
    )

    print(
        "Decoding :",
        DECODING_MODE
    )

    print(
        "Device   :",
        DEVICE
    )

    print(
        "Manifest :",
        MANIFEST_PATH
    )

    manifest = load_manifest()

    print()
    print(
        "Loaded",
        len(manifest),
        "samples."
    )

    model = load_model()

    inspect_model(
        model
    )

    results = []

    for item in manifest:

        print()
        print("-" * 60)

        try:

            audio_file = (
                item["audio"]
                .strip()
            )

            expected = item[
                "expected"
            ]

            category = item[
                "category"
            ]

        except Exception as e:

            print(
                "Manifest error:",
                repr(e)
            )

            continue

        sample = os.path.splitext(
            audio_file
        )[0]

        audio_path = os.path.join(
            AUDIO_DIR,
            audio_file
        )

        print(
            "Sample   :",
            sample
        )

        print(
            "Category :",
            category
        )

        print(
            "Audio    :",
            audio_path
        )

        if not os.path.exists(
            audio_path
        ):

            print(
                "ERROR: File does not exist."
            )

            continue

        try:

            (
                predicted,
                duration,
                inference_time,
                rtf
            ) = transcribe(
                audio_path,
                model
            )

            normalized_expected = normalize_text(
                expected
            )

            normalized_predicted = normalize_text(
                predicted
            )

            score = wer(
                normalized_expected,
                normalized_predicted
            )

            print()
            print(
                "Expected :",
                expected
            )

            print(
                "Predicted:",
                predicted
            )

            print(
                "Norm Exp :",
                normalized_expected
            )

            print(
                "Norm Pred:",
                normalized_predicted
            )

            print(
                f"WER      : {score:.4f}"
            )

            print(
                f"Duration : {duration:.4f} sec"
            )

            print(
                f"Latency  : {inference_time:.4f} sec"
            )

            print(
                f"RTF      : {rtf:.4f}"
            )

            results.append({

                "model":
                    "indic-conformer-600m-multilingual",

                "sample":
                    sample,

                "category":
                    category,

                "wer":
                    round(
                        score,
                        4
                    ),

                "audio_duration_sec":
                    round(
                        duration,
                        4
                    ),

                "inference_time_sec":
                    round(
                        inference_time,
                        4
                    ),

                "rtf":
                    round(
                        rtf,
                        4
                    ),

                "expected":
                    normalized_expected,

                "predicted":
                    normalized_predicted
            })

        except Exception as e:

            print()
            print("=" * 60)
            print(
                "ERROR PROCESSING:",
                sample
            )
            print("=" * 60)

            print(
                "Exception type:",
                type(e).__name__
            )

            print(
                "Exception repr:",
                repr(e)
            )

            print(
                "Exception str:",
                str(e)
            )

            print()
            print(
                "FULL TRACEBACK:"
            )

            traceback.print_exc()

            print("=" * 60)

    os.makedirs(
        os.path.dirname(
            OUTPUT_PATH
        ),
        exist_ok=True
    )

    fieldnames = [
        "model",
        "sample",
        "category",
        "wer",
        "audio_duration_sec",
        "inference_time_sec",
        "rtf",
        "expected",
        "predicted"
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            results
        )

    print()
    print("=" * 60)
    print(
        "EVALUATION COMPLETE"
    )
    print("=" * 60)

    print(
        "Samples evaluated :",
        len(results)
    )

    print(
        "Results saved to  :",
        OUTPUT_PATH
    )

    if results:

        avg_wer = (
            sum(
                r["wer"]
                for r in results
            )
            / len(results)
        )

        avg_latency = (
            sum(
                r["inference_time_sec"]
                for r in results
            )
            / len(results)
        )

        avg_rtf = (
            sum(
                r["rtf"]
                for r in results
            )
            / len(results)
        )

        print()
        print(
            f"Average WER       : {avg_wer:.4f}"
        )

        print(
            f"Average latency   : "
            f"{avg_latency:.4f} sec"
        )

        print(
            f"Average RTF       : "
            f"{avg_rtf:.4f}"
        )

    else:

        print()
        print(
            "No samples were successfully evaluated."
        )


if __name__ == "__main__":

    try:

        evaluate()

    except KeyboardInterrupt:

        print()
        print(
            "Evaluation interrupted."
        )

    except Exception as e:

        print()
        print("=" * 60)
        print("FATAL ERROR")
        print("=" * 60)

        print(
            "Exception type:",
            type(e).__name__
        )

        print(
            "Exception repr:",
            repr(e)
        )

        print()
        print(
            "FULL TRACEBACK:"
        )

        traceback.print_exc()