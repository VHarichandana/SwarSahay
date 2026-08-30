# ASR Phase 1 and Phase 1.2 Report

## 1. Objective

The goal of this phase was to test and compare speech-to-text models for the SwarSahay project.

The main focus was:

- Hindi speech recognition
- Code-switching between Hindi and English
- Dates and numeric information
- Word Error Rate (WER)
- Inference latency
- Real-Time Factor (RTF)

The two models tested were:

- OpenAI Whisper Medium
- AI4Bharat IndicConformer 600M Multilingual

---

## 2. Dataset

A small ASR test set was created with 9 audio samples.

The audio files are in:

```text
data/asr_test_set/audio/
```

The dataset contains three categories.

### Clean

- clean_01
- clean_02
- clean_03

### Code Switch

- codeswitch_01
- codeswitch_02
- codeswitch_03

### Numeric / Date

- numeric_01
- numeric_02
- numeric_03

The audio files are in `.ogg` format.

---

## 3. Manifest

The dataset is controlled using:

```text
data/asr_test_set/manifest.json
```

Each sample contains:

```json
{
  "audio": "clean_01.ogg",
  "expected": "meri beti ka naam anisha hai",
  "category": "clean"
}
```

The manifest provides:

- Audio file name
- Expected transcription
- Category

This allows both ASR models to be tested on the same samples.

---

## 4. Initial Whisper Evaluation

Whisper Medium was first evaluated on the 9 samples.

The initial evaluation showed an important issue with Hindi text.

For example:

```text
Expected : meri beti ka naam anisha hai
Predicted: मेरी बेटी का नाम अनीशा है
```

A direct WER comparison treated Roman Hindi and Devanagari Hindi as different text.

This resulted in an incorrect interpretation of the model performance.

Because of this, text normalization was added before calculating WER.

---

## 5. Text Normalization

A normalization step was added to make the expected and predicted text more comparable.

The evaluation workflow became:

```text
Expected text
      |
      v
Text normalization
      |
      v
Normalized expected text

Predicted text
      |
      v
Text normalization
      |
      v
Normalized predicted text

Normalized expected + normalized predicted
      |
      v
WER
```

Normalization helped with differences such as:

- Uppercase and lowercase English
- Punctuation
- Some Devanagari formatting differences
- Number formatting in some cases

However, normalization does not solve all pronunciation or language-script differences.

For example, an English number spoken by the model as Hindi words can still produce a high WER.

---

## 6. Whisper Evaluation Code

The Whisper evaluation was performed using:

```text
src/evaluate_asr.py
```

The model used was:

```text
openai/whisper-medium
```

The evaluation produced:

- Transcription
- Normalized expected text
- Normalized predicted text
- WER
- Audio duration
- Inference latency
- RTF

The normalized Whisper results were saved to:

```text
data/asr_test_set/asr_results_whisper_normalized.csv
```

---

## 7. IndicConformer Evaluation

The second model tested was:

```text
ai4bharat/indic-conformer-600m-multilingual
```

The original evaluation faced several technical problems.

### Problem 1: Model access

The Hugging Face repository required approval.

The model access was obtained and the model could eventually be loaded.

### Problem 2: TorchCodec

The first audio-loading approach caused:

```text
TorchCodec is required for load_with_torchcodec
```

There was also a Windows DLL error:

```text
libtorchcodec_core4.dll
```

To avoid this problem, audio loading was changed to use `librosa`.

The audio pipeline became:

```text
OGG audio
   |
   v
librosa
   |
   v
16 kHz mono audio
   |
   v
PyTorch tensor
   |
   v
IndicConformer
```

### Problem 3: Model parameter access

The model object did not expose parameters in the expected way.

The following approach caused:

```text
StopIteration
```

because of:

```python
next(model.parameters())
```

The code was changed to use an explicit device:

```python
torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
```

### Phase 1.2 evaluator

The updated evaluator was:

```text
src/evaluate_indic_v2.py
```

It records:

- Transcription
- Normalized transcription
- WER
- Audio duration
- Inference latency
- RTF

The results were saved to:

```text
data/asr_test_set/phase1.2/asr_results_indic_v2.csv
```

---

## 8. Final Phase 1.2 Workflow

The complete workflow used so far is:

```text
                    ASR TEST SET
                         |
                         v
                    manifest.json
                         |
                         v
                    Load audio
                         |
                         v
                  16 kHz mono audio
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Whisper Medium         IndicConformer
             |                       |
             v                       v
        Prediction              Prediction
             |                       |
             +-----------+-----------+
                         |
                         v
                  Text normalization
                         |
                         v
                Expected vs Predicted
                         |
                         v
                       WER
                         |
             +-----------+-----------+
             |                       |
             v                       v
          Latency                   RTF
             |                       |
             +-----------+-----------+
                         |
                         v
                  Results CSV
                         |
                         v
                Model comparison
                         |
                         v
                  Final analysis
```

---

## 9. Comparison File

The two model results were combined using:

```text
src/create_phase1_2_comparison.py
```

The final comparison file is:

```text
data/asr_test_set/phase1.2/asr_comparison_v2.csv
```

It contains 18 rows:

- 9 Whisper results
- 9 IndicConformer results

---

## 10. Overall Results

### Average WER

| Model | Average WER |
|---|---:|
| Whisper Medium | 0.4610 |
| IndicConformer 600M | 0.7364 |

Lower WER is better.

Whisper had the lower average WER on this test set.

Difference:

```text
IndicConformer WER - Whisper WER
= 0.2754
```

---

## 11. WER by Category

| Model | Clean | Code Switch | Numeric / Date |
|---|---:|---:|---:|
| Whisper Medium | 0.2235 | 0.5595 | 0.6000 |
| IndicConformer 600M | 0.4192 | 0.7679 | 1.0222 |

Lower is better.

Whisper had lower WER in all three categories in this experiment.

---

## 12. Average Inference Latency

| Model | Average Latency |
|---|---:|
| Whisper Medium | 29.7471 sec |
| IndicConformer 600M | 0.9001 sec |

IndicConformer was much faster in this experiment.

Latency difference:

```text
IndicConformer - Whisper
= -28.8471 seconds
```

---

## 13. Average RTF

| Model | Average RTF |
|---|---:|
| Whisper Medium | 5.7575 |
| IndicConformer 600M | 0.1655 |

Lower RTF is better.

IndicConformer had a much lower RTF.

An RTF below 1 means the measured inference time was lower than the duration of the processed audio.

---

## 14. Latency by Category

| Model | Clean | Code Switch | Numeric / Date |
|---|---:|---:|---:|
| Whisper Medium | 38.6761 sec | 25.8760 sec | 24.6893 sec |
| IndicConformer 600M | 1.1303 sec | 0.8206 sec | 0.7494 sec |

IndicConformer was faster in every category in this experiment.

---

## 15. Sample-Level Results

### Whisper Medium

| Sample | Category | WER |
|---|---|---:|
| clean_01 | clean | 0.0000 |
| clean_02 | clean | 0.0000 |
| clean_03 | clean | 0.5455 |
| codeswitch_01 | code_switch | 0.1250 |
| codeswitch_02 | code_switch | 0.7143 |
| codeswitch_03 | code_switch | 0.7143 |
| numeric_01 | numeric_date | 0.0000 |
| numeric_02 | numeric_date | 0.8000 |
| numeric_03 | numeric_date | 1.0000 |

### IndicConformer 600M

| Sample | Category | WER |
|---|---|---:|
| clean_01 | clean | 0.1667 |
| clean_02 | clean | 1.0000 |
| clean_03 | clean | 0.0909 |
| codeswitch_01 | code_switch | 0.8750 |
| codeswitch_02 | code_switch | 0.7143 |
| codeswitch_03 | code_switch | 0.7143 |
| numeric_01 | numeric_date | 1.6667 |
| numeric_02 | numeric_date | 0.4000 |
| numeric_03 | numeric_date | 1.0000 |

---

## 16. Final Phase 1.2 Findings

Based on the current 9-sample evaluation:

### Whisper Medium

Advantages:

- Lower overall WER
- Better clean-speech performance
- Better code-switch performance
- Better numeric/date performance
- Better accuracy on this test set

Disadvantage:

- Much higher inference latency
- RTF is above 1 in this experiment

### IndicConformer

Advantages:

- Very low inference latency
- Much lower RTF
- Fast enough for real-time style processing in this experiment
- Designed for Indian-language speech

Disadvantages:

- Higher overall WER
- Higher code-switch WER
- Higher numeric/date WER
- Accuracy needs improvement for the current test set

---

## 17. Current Model Decision

The current results do not justify saying that one model is universally better.

Instead:

```text
Whisper Medium
    =
Higher accuracy
+
Lower WER
-
Much slower

IndicConformer
    =
Much faster
+
Low RTF
-
Higher WER
```

For the current test set, Whisper is the accuracy winner.

IndicConformer is the speed winner.

The final production model should therefore be selected using both accuracy and latency requirements.

---

## 18. Important Limitation

The evaluation contains only 9 samples.

Therefore, the results should be treated as an initial experiment and not as a final benchmark.

The current results show performance on:

- 3 clean samples
- 3 code-switch samples
- 3 numeric/date samples

A larger and more representative dataset should be used before making a final production decision.

---

## 19. Files Created or Used

```text
data/
└── asr_test_set/
    ├── manifest.json
    ├── audio/
    │   ├── clean_01.ogg
    │   ├── clean_02.ogg
    │   ├── clean_03.ogg
    │   ├── codeswitch_01.ogg
    │   ├── codeswitch_02.ogg
    │   ├── codeswitch_03.ogg
    │   ├── numeric_01.ogg
    │   ├── numeric_02.ogg
    │   └── numeric_03.ogg
    │
    ├── asr_results_whisper_normalized.csv
    │
    └── phase1.2/
        ├── asr_results_indic_v2.csv
        └── asr_comparison_v2.csv

src/
├── evaluate_asr.py
├── evaluate_indic.py
├── evaluate_indic_v2.py
├── create_phase1_2_comparison.py
├── analyze_phase1_2.py
└── text_normalizer.py
```

---

## 20. Commands Used

Activate the virtual environment:

```powershell
.venv\Scriptsctivate
```

Run Whisper evaluation:

```powershell
python src/evaluate_asr.py
```

Run IndicConformer Phase 1.2 evaluation:

```powershell
python src/evaluate_indic_v2.py
```

Create model comparison:

```powershell
python src/create_phase1_2_comparison.py
```

Analyze Phase 1.2:

```powershell
python src/analyze_phase1_2.py
```

---

## 21. Phase 1.2 Conclusion

Phase 1 established the ASR evaluation pipeline and tested two candidate models using the same manifest and audio samples.

Phase 1.2 added:

- Text normalization
- Model comparison
- Category-level WER
- Inference latency
- RTF
- Detailed CSV results

The experiment shows a clear trade-off:

```text
Whisper Medium
Better accuracy
        vs
IndicConformer
Much better speed
```

The next phase should focus on improving and validating the ASR system with a larger dataset and then measuring its effect on the downstream SwarSahay pipeline.

# Current Model Decision

Whisper → better accuracy
IndicConformer → better speed

### Phase 1 V1 Decision

For V1, we will proceed with Whisper Medium as the primary ASR pipeline.
Whisper achieved the lower WER on the current evaluation set, and the V1
scope is a local demo where real-time latency is not a strict requirement.
IndicConformer will be revisited after its language and decoding
configuration is independently verified and its accuracy is re-evaluated.
