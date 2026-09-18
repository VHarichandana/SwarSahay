import json
import os
import time
import re
from dotenv import load_dotenv
from groq import Groq, RateLimitError

from form_state import update_form_state
from schema_loader import (
    get_required_fields,
    get_conversational_required_fields,
    get_all_fields,
    get_field_by_id
)
from normalizer import normalize_fields
from field_validator import validate_fields

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_llm(prompt: str) -> str:
    max_retries = 8
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=350
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            err_msg = str(e)
            wait_sec = 60
            min_sec_match = re.search(r"try again in (\d+)m([\d\.]+)s", err_msg)
            sec_match = re.search(r"try again in ([\d\.]+)s", err_msg)
            if min_sec_match:
                wait_sec = int(min_sec_match.group(1)) * 60 + float(min_sec_match.group(2)) + 3
            elif sec_match:
                wait_sec = float(sec_match.group(1)) + 3

            if attempt < max_retries - 1:
                print(f"[RateLimit] Free tier daily token limit reached. Sleeping {wait_sec:.1f}s before retry ({attempt + 1}/{max_retries})...")
                time.sleep(wait_sec)
            else:
                raise e


def extract_fields(transcript: str, current_form_state: dict) -> dict:
    required_fields = get_conversational_required_fields()
    all_fields = get_all_fields()

    conditional_fields = []
    optional_fields = []

    for field in all_fields:
        f_id = field.get("id")
        status = field.get("status")

        if status in ["MANUAL", "BANK_ONLY", "DERIVED"]:
            continue

        if status == "CONDITIONAL":
            condition = field.get("conditional_on")

            if condition is None:
                # E.g. guardian_pan which is conditional without condition block
                conditional_fields.append(f_id)
                continue

            condition_field = condition.get("field")
            operator = condition.get("operator")
            expected_value = condition.get("value")

            actual_value = current_form_state.get(condition_field)

            if operator == "equals":
                if actual_value == expected_value:
                    conditional_fields.append(f_id)

            elif operator == "in":
                if actual_value in expected_value:
                    conditional_fields.append(f_id)

        elif status == "OPTIONAL" and field.get("type") != "array":
            optional_fields.append(f_id)

    fields_to_extract = []
    for f in required_fields + conditional_fields + optional_fields:
        if f not in fields_to_extract:
            fields_to_extract.append(f)

    field_lines = []
    for i, f_id in enumerate(fields_to_extract, 1):
        f_obj = get_field_by_id(f_id) or {}
        label = f_obj.get("label", "")
        f_type = f_obj.get("type", "string")
        options = f_obj.get("options")
        if f_type == "boolean":
            field_lines.append(f"{i}. {f_id} (label: {label}, type: boolean: true/false)")
        elif options:
            field_lines.append(f"{i}. {f_id} (label: {label}, type: enum, options: {options})")
        else:
            field_lines.append(f"{i}. {f_id} (label: {label}, type: {f_type})")

    field_list = "\n".join(field_lines)

    json_template = {
        field: None for field in fields_to_extract
    }

    prompt = f"""
You are an information extraction system for the SwarSahay project.

Extract information only from the user's transcript.

Available fields:

{field_list}

Current form state:
{json.dumps(current_form_state)}

Rules:

1. Extract only information explicitly present in the transcript.
2. Do not invent or guess values.
3. Extract the actual value, not surrounding conversational words.
4. Only return NEW information or an explicit correction.
5. If a field already has a value in the current form state and the user does not correct it, return null for that field.
6. If a field is not mentioned, return null.
7. Return ONLY valid JSON.
8. Do not infer a form field from general intent words.
9. "Mujhe Sukanya account kholna hai" expresses user intent only and does not confirm account_type or account_operation.
10. A field should be extracted only when the user explicitly provides that field's value as form information.
11. When a user introduces themselves as mother, father, or guardian (e.g. "Main Anita Gupta uski mother hoon", "Mera PAN number..."), extract their name as guardian_full_name (NOT account_holder_name) and their documents to guardian_pan/guardian_aadhaar. account_holder_name is strictly the girl child in whose name the account is opened.
12. For fields with type: boolean, return true or false as a JSON boolean value (not a text string).
13. For enum fields, map the user's expression to one of the allowed options.
14. When the user accepts or agrees to scheme rules or terms (e.g. "yojana ke niyam sweekar", "terms accept"), extract terms_acceptance as true.

Transcript:
"{transcript}"

JSON format:
{json.dumps(json_template)}
"""

    response = ask_llm(prompt).strip()

    if response.startswith("```"):
        response = response.strip("`")
        if response.startswith("json"):
            response = response[4:]
        response = response.strip()

    return json.loads(response)


if __name__ == "__main__":

    form_state = {
        "deposit_mode": "cheque"
    }

    transcript = (
        "Meri beti ka naam Ananya Sharma hai. "
        "Uska janam 15 March 2018 ko hua tha. "
        "Main uski maa Sita Sharma hoon. "
        "Mera mobile number 9876543210 hai. "
        "Cheque ki date 20 March 2026 hai."
    )

    fields = extract_fields(
        transcript,
        form_state
    )

    print("Raw extraction:")
    print(fields)

    fields = normalize_fields(fields)

    print("\nAfter normalization:")
    print(fields)

    fields = validate_fields(fields)

    print("\nAfter validation:")
    print(fields)

    form_state = update_form_state(
        form_state,
        fields
    )

    print("\nFinal form state:")
    print(form_state)