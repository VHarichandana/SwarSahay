import json
import csv
import os

from jiwer import wer

from indic_asr import IndicASR
from text_normalizer import normalize_text

MANIFEST_PATH = (
    "data/asr_test_set/manifest.json"
)

AUDIO_DIR = (
    "data/asr_test_set/audio"
)

OUTPUT_CSV = (
    "data/asr_test_set/"
    "asr_results_indic_normalized.csv"
)

MODEL_NAME = (
    "ai4bharat/"
    "indic-conformer-600m-multilingual"
)


def load_manifest(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def evaluate():

    print("=" * 60)
    print("INDICCONFORMER ASR EVALUATION")
    print("=" * 60)

    print(
        f"Model    : {MODEL_NAME}"
    )

    print(
        f"Manifest : {MANIFEST_PATH}"
    )

    print()

    manifest = load_manifest(
        MANIFEST_PATH
    )

    print(
        f"Loaded {len(manifest)} samples."
    )

    print()

    asr = IndicASR(
        MODEL_NAME
    )

    results = []

    for item in manifest:

        audio_file = item["audio"].strip()

        expected = item["expected"].strip()

        category = item["category"].strip()

        sample = os.path.splitext(
            audio_file
        )[0]

        audio_path = os.path.join(
            AUDIO_DIR,
            audio_file
        )

        print("-" * 60)

        print(
            f"Sample   : {sample}"
        )

        print(
            f"Category : {category}"
        )

        print(
            f"Audio    : {audio_path}"
        )

        if not os.path.exists(audio_path):

            print(
                "ERROR: Audio file not found!"
            )

            continue

        try:

            predicted = asr.audio_to_text(
                audio_path,
                language="hi"
            )

            normalized_expected = (
                normalize_text(expected)
            )

            normalized_predicted = (
                normalize_text(predicted)
            )

            score = wer(
                normalized_expected,
                normalized_predicted
            )

            print(
                f"Expected : {expected}"
            )

            print(
                f"Predicted: {predicted}"
            )

            print(
                f"Norm Exp : {normalized_expected}"
            )

            print(
                f"Norm Pred: {normalized_predicted}"
            )

            print(
                f"WER      : {score:.2f}"
            )

            results.append({

                "model":
                    "indic-conformer-600m-multilingual",

                "sample":
                    sample,

                "category":
                    category,

                "wer":
                    f"{score:.4f}",

                "expected":
                    expected,

                "predicted":
                    predicted,

                "normalized_expected":
                    normalized_expected,

                "normalized_predicted":
                    normalized_predicted

            })

        except Exception as e:

            print(
                f"ERROR processing {sample}: {e}"
            )

    os.makedirs(
        os.path.dirname(OUTPUT_CSV),
        exist_ok=True
    )

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        fieldnames = [

            "model",

            "sample",

            "category",

            "wer",

            "expected",

            "predicted",

            "normalized_expected",

            "normalized_predicted"

        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)

    print()

    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    print(
        f"Samples evaluated : {len(results)}"
    )

    print(
        f"Results saved to  : {OUTPUT_CSV}"
    )

    if results:

        average_wer = sum(
            float(row["wer"])
            for row in results
        ) / len(results)

        print(
            f"Average WER       : {average_wer:.4f}"
        )


if __name__ == "__main__":
    evaluate()