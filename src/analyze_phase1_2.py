import pandas as pd

FILE = (
    "data/asr_test_set/phase1.2/"
    "asr_comparison_v2.csv"
)


def main():

    print("=" * 70)
    print("PHASE 1.2 FINAL ASR ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(FILE)

    overall = (
        df
        .groupby("model")
        .agg(
            average_wer=(
                "wer",
                "mean"
            ),
            average_latency_sec=(
                "inference_time_sec",
                "mean"
            ),
            average_rtf=(
                "rtf",
                "mean"
            )
        )
        .reset_index()
    )

    print()
    print("=" * 70)
    print("OVERALL PERFORMANCE")
    print("=" * 70)

    print(
        overall.to_string(
            index=False
        )
    )

    category = (
        df
        .groupby(
            [
                "model",
                "category"
            ]
        )
        .agg(
            average_wer=(
                "wer",
                "mean"
            ),
            average_latency_sec=(
                "inference_time_sec",
                "mean"
            )
        )
        .reset_index()
    )

    print()
    print("=" * 70)
    print("CATEGORY PERFORMANCE")
    print("=" * 70)

    print(
        category.to_string(
            index=False
        )
    )

    best_wer_index = (
        overall["average_wer"]
        .idxmin()
    )

    best_wer_model = (
        overall.loc[
            best_wer_index,
            "model"
        ]
    )

    best_wer_value = (
        overall.loc[
            best_wer_index,
            "average_wer"
        ]
    )

    fastest_index = (
        overall["average_latency_sec"]
        .idxmin()
    )

    fastest_model = (
        overall.loc[
            fastest_index,
            "model"
        ]
    )

    fastest_value = (
        overall.loc[
            fastest_index,
            "average_latency_sec"
        ]
    )

    print()
    print("=" * 70)
    print("MODEL RESULTS")
    print("=" * 70)

    print()
    print(
        f"Lowest average WER : "
        f"{best_wer_model}"
    )

    print(
        f"WER                 : "
        f"{best_wer_value:.4f}"
    )

    print()
    print(
        f"Fastest average latency : "
        f"{fastest_model}"
    )

    print(
        f"Latency                  : "
        f"{fastest_value:.4f} sec"
    )

    whisper = overall[
        overall["model"]
        == "whisper-medium"
    ]

    indic = overall[
        overall["model"]
        == "indic-conformer-600m-multilingual"
    ]

    if (
        len(whisper) == 1
        and len(indic) == 1
    ):

        whisper_wer = (
            whisper[
                "average_wer"
            ].iloc[0]
        )

        indic_wer = (
            indic[
                "average_wer"
            ].iloc[0]
        )

        whisper_latency = (
            whisper[
                "average_latency_sec"
            ].iloc[0]
        )

        indic_latency = (
            indic[
                "average_latency_sec"
            ].iloc[0]
        )

        print()
        print("=" * 70)
        print("WHISPER VS INDICCONFORMER")
        print("=" * 70)

        print()
        print(
            f"Whisper WER       : "
            f"{whisper_wer:.4f}"
        )

        print(
            f"IndicConformer WER: "
            f"{indic_wer:.4f}"
        )

        print()
        print(
            f"Whisper latency       : "
            f"{whisper_latency:.4f} sec"
        )

        print(
            f"IndicConformer latency: "
            f"{indic_latency:.4f} sec"
        )

        wer_difference = (
            indic_wer
            - whisper_wer
        )

        print()
        print(
            f"WER difference "
            f"(Indic - Whisper): "
            f"{wer_difference:.4f}"
        )

        latency_difference = (
            indic_latency
            - whisper_latency
        )

        print(
            f"Latency difference "
            f"(Indic - Whisper): "
            f"{latency_difference:.4f} sec"
        )


if __name__ == "__main__":
    main()