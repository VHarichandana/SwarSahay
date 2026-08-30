from asr import ASR
from jiwer import wer

expected = "मेरी बेटी का नाम अनीशा है"

asr = ASR()

predicted = asr.audio_to_text(
    "data/asr_test_set/audio/clean_01.ogg"
)

score = wer(expected, predicted)

print("Expected :", expected)
print("Predicted:", predicted)
print("WER      :", score)