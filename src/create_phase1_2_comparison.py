import pandas as pd

WHISPER_FILE = (
    "data/asr_test_set/phase1.2/"
    "asr_results_whisper_v2.csv"
)

INDIC_FILE = (
    "data/asr_test_set/phase1.2/"
    "asr_results_indic_v2.csv"
)

OUTPUT_FILE = (
    "data/asr_test_set/phase1.2/"
    "asr_comparison_v2.csv"
)


def main():

    print("=" * 60)
    print("PHASE 1.2 ASR MODEL COMPARISON")
    print("=" * 60)

    print()
    print("Loading Whisper results...")

    whisper = pd.read_csv(
        WHISPER_FILE
    )

    print(
        "Whisper samples:",
        len(whisper)
    )

    print()
    print(
        "Loading IndicConformer results..."
    )

    indic = pd.read_csv(
        INDIC_FILE
    )

    print(
        "IndicConformer samples:",
        len(indic)
    )

    comparison = pd.concat(
        [
            whisper,
            indic
        ],
        ignore_index=True
    )

    comparison.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 60)
    print("COMPARISON CREATED")
    print("=" * 60)

    print(
        "Total rows:",
        len(comparison)
    )

    print(
        "Saved to:",
        OUTPUT_FILE
    )

    print()
    print("Average WER:")

    print(
        comparison
        .groupby("model")["wer"]
        .mean()
        .round(4)
    )

    print()
    print("Average WER by category:")

    category_wer = (
        comparison
        .groupby(
            [
                "model",
                "category"
            ]
        )["wer"]
        .mean()
        .round(4)
    )

    print(category_wer)

    print()
    print("Average inference latency:")

    latency = (
        comparison
        .groupby(
            "model"
        )["inference_time_sec"]
        .mean()
        .round(4)
    )

    print(latency)

    print()
    print("Average RTF:")

    rtf = (
        comparison
        .groupby(
            "model"
        )["rtf"]
        .mean()
        .round(4)
    )

    print(rtf)

    print()
    print(
        "Average latency by category:"
    )

    category_latency = (
        comparison
        .groupby(
            [
                "model",
                "category"
            ]
        )["inference_time_sec"]
        .mean()
        .round(4)
    )

    print(category_latency)


if __name__ == "__main__":
    main()