import csv
import os

WHISPER_RESULTS = (
    "data/asr_test_set/"
    "asr_results_whisper_normalized.csv"
)

INDIC_RESULTS = (
    "data/asr_test_set/"
    "asr_results_indic_normalized.csv"
)

OUTPUT_FILE = (
    "data/asr_test_set/"
    "asr_comparison_normalized.csv"
)


def load_results(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        return list(
            csv.DictReader(file)
        )


def create_comparison():

    print("=" * 60)
    print("CREATING NORMALIZED ASR MODEL COMPARISON")
    print("=" * 60)

    print("\nLoading Whisper results...")

    whisper_results = load_results(
        WHISPER_RESULTS
    )

    print(
        f"Whisper samples: "
        f"{len(whisper_results)}"
    )

    print("\nLoading IndicConformer results...")

    indic_results = load_results(
        INDIC_RESULTS
    )

    print(
        f"IndicConformer samples: "
        f"{len(indic_results)}"
    )

    comparison = []

    for row in whisper_results:

        comparison.append({
            "model": row["model"],
            "sample": row["sample"],
            "category": row["category"],
            "wer": row["wer"]
        })

    for row in indic_results:

        comparison.append({
            "model": row["model"],
            "sample": row["sample"],
            "category": row["category"],
            "wer": row["wer"]
        })

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        fieldnames = [
            "model",
            "sample",
            "category",
            "wer"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(comparison)

    print()

    print("=" * 60)
    print("COMPARISON CREATED")
    print("=" * 60)

    print(
        f"Total rows: {len(comparison)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    models = {}

    for row in comparison:

        model = row["model"]

        score = float(
            row["wer"]
        )

        if model not in models:
            models[model] = []

        models[model].append(score)

    print("\nAverage WER:")

    for model, scores in models.items():

        average = (
            sum(scores) / len(scores)
        )

        print(
            f"{model}: {average:.4f}"
        )

    categories = {}

    for row in comparison:

        key = (
            row["model"],
            row["category"]
        )

        score = float(
            row["wer"]
        )

        if key not in categories:
            categories[key] = []

        categories[key].append(score)

    print("\nCategory WER:")

    for (
        model,
        category
    ), scores in categories.items():

        average = (
            sum(scores) / len(scores)
        )

        print(
            f"{model:40} "
            f"{category:15} "
            f"{average:.4f}"
        )


if __name__ == "__main__":
    create_comparison()