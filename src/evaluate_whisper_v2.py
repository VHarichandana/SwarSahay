import os
import json
import csv
import time

import librosa
from jiwer import wer
from transformers import pipeline

from text_normalizer import normalize_text

MODEL_NAME = "openai/whisper-medium"

MANIFEST_PATH = "data/asr_test_set/manifest.json"

OUTPUT_PATH = (
    "data/asr_test_set/phase1.2/"
    "asr_results_whisper_v2.csv"
)

SAMPLE_RATE = 16000


def load_manifest():

    with open(
        MANIFEST_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def evaluate():

    print("=" * 60)
    print("WHISPER ASR EVALUATION - PHASE 1.2")
    print("=" * 60)

    print("Model    :", MODEL_NAME)
    print("Manifest :", MANIFEST_PATH)

    manifest = load_manifest()

    print()
    print("Loaded", len(manifest), "samples.")
    print()

    print("Loading Whisper model...")

    pipe = pipeline(
        "automatic-speech-recognition",
        model=MODEL_NAME
    )

    print("Whisper model loaded.")

    results = []

    for item in manifest:

        audio_file = item["audio"].strip()

        expected = item["expected"]

        category = item["category"]

        sample = os.path.splitext(
            audio_file
        )[0]

        audio_path = os.path.join(
            "data/asr_test_set/audio",
            audio_file
        )

        print("-" * 60)

        print("Sample   :", sample)
        print("Category :", category)
        print("Audio    :", audio_path)

        try:

            audio, sr = librosa.load(
                audio_path,
                sr=SAMPLE_RATE,
                mono=True
            )

            duration = len(audio) / sr

            start_time = time.perf_counter()

            result = pipe(
                {
                    "raw": audio,
                    "sampling_rate": SAMPLE_RATE
                }
            )

            end_time = time.perf_counter()

            inference_time = (
                end_time - start_time
            )

            predicted = result["text"].strip()

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

            rtf = inference_time / duration

            print("Expected :", expected)
            print("Predicted:", predicted)

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
                    "whisper-medium",

                "sample":
                    sample,

                "category":
                    category,

                "wer":
                    round(score, 4),

                "audio_duration_sec":
                    round(duration, 4),

                "inference_time_sec":
                    round(inference_time, 4),

                "rtf":
                    round(rtf, 4),

                "expected":
                    normalized_expected,

                "predicted":
                    normalized_predicted

            })

        except Exception as e:

            print(
                f"ERROR processing {sample}: {e}"
            )

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
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

        writer.writerows(results)

    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
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
            sum(r["wer"] for r in results)
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
            sum(r["rtf"] for r in results)
            / len(results)
        )

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


if __name__ == "__main__":
    evaluate()