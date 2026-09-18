import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_schema():
    candidate_paths = [
        PROJECT_ROOT / "schema" / "sukanya_schema.json",
        Path("schema/sukanya_schema.json"),
        PROJECT_ROOT / "data" / "sukanya_schema.json",
        Path("data/sukanya_schema.json")
    ]

    for p in candidate_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as file:
                return json.load(file)

    raise FileNotFoundError("schema/sukanya_schema.json not found.")


def get_all_fields():
    schema = load_schema()

    fields = []

    for section in schema["sections"]:
        for field in section["fields"]:
            fields.append(field)

    return fields


def get_required_fields():
    fields = get_all_fields()

    required_fields = []

    for field in fields:
        if field.get("required") is True:
            required_fields.append(field["id"])

    return required_fields


def get_conversational_required_fields():
    fields = get_all_fields()

    non_conversational_statuses = {"MANUAL", "BANK_ONLY", "DERIVED"}
    conversational_required = []

    for field in fields:
        if field.get("required") is True and field.get("status") not in non_conversational_statuses:
            conversational_required.append(field["id"])

    return conversational_required


def get_field_by_id(field_id: str):
    fields = get_all_fields()

    for field in fields:
        if field.get("id") == field_id:
            return field

    return None


if __name__ == "__main__":

    fields = get_all_fields()

    for field in fields:
        print("\nFIELD:", field.get("id"))
        print("TYPE:", field.get("type"))
        print("NORMALIZATION:", field.get("normalization"))
        print("VALIDATION:", field.get("validation"))