import json
import os

from extractor import extract_fields
from normalizer import normalize_fields
from field_validator import validate_fields
from form_state import (
    update_form_state,
    get_next_missing_field,
    get_conditional_fields
)
from question_generator import generate_question, generate_reask_question

CACHE_FILE = "data/.nlu_cache.json"


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_examples():
    with open(
        "data/sample_conversations.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)["examples"]


def evaluate():
    examples = load_examples()
    cache = load_cache()

    total_expected_fields = 0
    correct_fields = 0
    false_positives = 0
    false_negatives = 0

    for index, example in enumerate(examples, start=1):
        transcript = example["transcript"]
        expected = example["expected"]
        form_state = dict(example.get("form_state", {}))

        cache_key = f"{transcript.strip()} || {json.dumps(form_state, sort_keys=True)}"
        if cache_key in cache:
            extracted = cache[cache_key]
        else:
            extracted = extract_fields(
                transcript,
                form_state
            )
            cache[cache_key] = extracted
            save_cache(cache)

        normalized = normalize_fields(extracted)
        validated = validate_fields(normalized)

        predicted = {
            field_id: value
            for field_id, value in validated.items()
            if value is not None
        }

        print(f"\nExample {index}")
        print("Transcript:")
        print(transcript)

        if form_state:
            print("Initial Form State:")
            print(form_state)

        print("Expected:")
        print(expected)

        print("Predicted:")
        print(predicted)

        # Check for invalid fields & re-ask
        invalid = {
            f: val for f, val in extracted.items()
            if val is not None and validated.get(f) is None
        }
        if invalid:
            for inv_field, inv_val in invalid.items():
                print(f"Invalid Field Detected: {inv_field} (Value: '{inv_val}')")
                print(f"Re-ask Question: {generate_reask_question(inv_field, inv_val)}")

        for field_id, expected_value in expected.items():
            total_expected_fields += 1

            predicted_value = predicted.get(field_id)

            if predicted_value == expected_value:
                correct_fields += 1
            else:
                false_negatives += 1

        for field_id in predicted:
            if field_id not in expected:
                false_positives += 1

    print("\n--------------------")
    print("Correction State Test")
    print("--------------------")

    form_state = {
        "account_holder_name": "Ananya Sharma"
    }

    correction_transcript = (
        "Nahi, naam Ananya Sharma nahi, Kavya Sharma hai"
    )

    corr_key = f"{correction_transcript.strip()} || {json.dumps(form_state, sort_keys=True)}"
    if corr_key in cache:
        extracted = cache[corr_key]
    else:
        extracted = extract_fields(
            correction_transcript,
            form_state
        )
        cache[corr_key] = extracted
        save_cache(cache)

    normalized = normalize_fields(extracted)
    validated = validate_fields(normalized)

    form_state = update_form_state(
        form_state,
        validated
    )

    print("Final corrected state:")
    print(form_state)

    print("\n--------------------")
    print("Missing Field Test")
    print("--------------------")

    form_state = {
        "account_holder_name": "Ananya Sharma",
        "date_of_birth": "2018-03-15",
        "guardian_full_name": "Sita Sharma",
        "guardian_relationship": "mother"
    }

    next_field = get_next_missing_field(form_state)

    print("Next missing field:")
    print(next_field)

    if next_field is not None:
        question = generate_question(next_field)

        print("Question:")
        print(question)

    print("\n--------------------")
    print("Conditional Field Test")
    print("--------------------")

    form_state = {
        "nominee_is_minor": False
    }

    conditional_fields = get_conditional_fields(
        form_state
    )

    print("Active conditional fields:")
    print(conditional_fields)

    accuracy = (
        correct_fields / total_expected_fields
        if total_expected_fields > 0
        else 0
    )

    precision_denominator = (
        correct_fields + false_positives
    )

    precision = (
        correct_fields / precision_denominator
        if precision_denominator > 0
        else 0
    )

    recall_denominator = (
        correct_fields + false_negatives
    )

    recall = (
        correct_fields / recall_denominator
        if recall_denominator > 0
        else 0
    )

    if precision + recall > 0:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1 = 0

    print("\n--------------------")
    print("NLU Evaluation")
    print("--------------------")
    print(f"Total examples: {len(examples)}")
    print(f"Correct fields: {correct_fields}")
    print(f"Expected fields: {total_expected_fields}")
    print(f"False positives: {false_positives}")
    print(f"False negatives: {false_negatives}")
    print(f"Field accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 score: {f1:.4f}")


if __name__ == "__main__":
    evaluate()