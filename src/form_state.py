from schema_loader import (
    get_required_fields,
    get_all_fields,
    get_conversational_required_fields,
    get_field_by_id
)
from question_generator import (
    generate_question,
    generate_reask_question,
    generate_confirmation_prompt,
    is_sensitive_field,
    NON_CONVERSATIONAL_FIELDS
)


def update_form_state(current_state: dict, extracted_fields: dict) -> dict:
    for key, value in extracted_fields.items():
        if value is not None:
            current_state[key] = value

    return current_state


def condition_is_met(condition: dict, current_state: dict) -> bool:
    if condition is None:
        return True

    field_id = condition.get("field")
    operator = condition.get("operator")
    expected_value = condition.get("value")

    actual_value = current_state.get(field_id)

    if operator == "equals":
        return actual_value == expected_value

    if operator == "in":
        return actual_value in expected_value

    return False


def get_conditional_fields(current_state: dict) -> list:
    fields = get_all_fields()

    active_fields = []

    for field in fields:
        if field.get("status") != "CONDITIONAL":
            continue

        if field.get("id") in NON_CONVERSATIONAL_FIELDS:
            continue

        condition = field.get("conditional_on")

        if condition is None:
            continue

        if condition_is_met(condition, current_state):
            active_fields.append(field["id"])

    return active_fields


def get_missing_required_fields(current_state: dict) -> list:
    required_fields = get_conversational_required_fields()

    missing_fields = []

    for field in required_fields:
        if current_state.get(field) is None:
            missing_fields.append(field)

    return missing_fields


def get_next_missing_field(current_state: dict):
    missing_required = get_missing_required_fields(current_state)

    if missing_required:
        return missing_required[0]

    conditional_fields = get_conditional_fields(current_state)

    for field in conditional_fields:
        if current_state.get(field) is None:
            return field

    return None


def process_turn(current_state: dict, transcript: str) -> dict:
    from extractor import extract_fields
    from normalizer import normalize_fields
    from field_validator import validate_fields_with_reask

    extracted = extract_fields(transcript, current_state)
    normalized = normalize_fields(extracted)
    validated, invalid_fields = validate_fields_with_reask(normalized)

    # Generate re-ask questions for invalid fields
    reask_questions = {}
    for f in invalid_fields:
        reask_questions[f] = generate_reask_question(f, extracted.get(f))

    # Update form state with valid fields only
    new_state = update_form_state(dict(current_state), validated)

    # Confirmation prompts for sensitive/error-prone fields
    confirmation_prompts = {}
    for f, val in validated.items():
        if val is not None and is_sensitive_field(f):
            confirmation_prompts[f] = generate_confirmation_prompt(f, val)

    next_field = get_next_missing_field(new_state)
    next_question = generate_question(next_field) if next_field else None

    return {
        "extracted": extracted,
        "normalized": normalized,
        "validated": validated,
        "invalid_fields": invalid_fields,
        "reask_questions": reask_questions,
        "updated_state": new_state,
        "confirmation_prompts": confirmation_prompts,
        "next_field": next_field,
        "next_question": next_question
    }


if __name__ == "__main__":

    form_state = {
        "deposit_mode": "cheque",
        "permanent_same_as_present": True,
        "nominee_is_minor": False
    }

    conditional_fields = get_conditional_fields(form_state)

    print("Active conditional fields:")
    print(conditional_fields)

    missing = get_missing_required_fields(form_state)
    print("Missing conversational required fields count:", len(missing))
    print("Next missing field:", get_next_missing_field(form_state))