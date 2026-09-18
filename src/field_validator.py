from datetime import datetime
import re

from schema_loader import get_field_by_id


def validate_date(value: str) -> bool:
    if value is None:
        return False

    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_boolean(value) -> bool:
    return isinstance(value, bool)


def validate_regex(value, pattern: str) -> bool:
    if value is None:
        return False

    return re.fullmatch(
        pattern,
        str(value)
    ) is not None


def validate_number(value, validation: dict) -> bool:
    if value is None:
        return False

    try:
        number = float(value)
    except (ValueError, TypeError):
        return False

    minimum = validation.get("min")
    maximum = validation.get("max")

    if minimum is not None and number < minimum:
        return False

    if maximum is not None and number > maximum:
        return False

    return True


def validate_enum(value: str, allowed_options: list) -> bool:
    if value is None or not allowed_options:
        return False

    return value in allowed_options


def validate_deposit_mode(value: str) -> bool:
    if value is None:
        return False

    valid_modes = [
        "cash",
        "cheque",
        "dd"
    ]

    return validate_enum(value, valid_modes)


def validate_email(value: str) -> bool:
    if value is None:
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.fullmatch(
        pattern,
        str(value)
    ) is not None


def validate_field(field_id: str, value):
    if value is None:
        return None

    field_schema = get_field_by_id(field_id)

    if field_schema is None:
        return value

    field_type = field_schema.get("type")
    validation = field_schema.get("validation") or {}

    if field_type == "date":
        if not validate_date(value):
            return None

    if field_type == "boolean":
        if not validate_boolean(value):
            return None

    if field_type == "enum":
        options = field_schema.get("options")
        if options is not None:
            if not validate_enum(value, options):
                return None

    if field_type == "number":
        if not validate_number(
            value,
            validation
        ):
            return None

    regex_pattern = validation.get("regex")

    if regex_pattern is not None:
        if not validate_regex(
            value,
            regex_pattern
        ):
            return None

    if validation.get("valid_date") is True:
        if not validate_date(value):
            return None

    if field_id == "deposit_mode":
        if not validate_deposit_mode(value):
            return None

    if field_id == "email":
        if not validate_email(value):
            return None

    return value


def validate_fields(fields: dict) -> dict:
    validated = {}

    for field_id, value in fields.items():
        validated[field_id] = validate_field(
            field_id,
            value
        )

    return validated


def identify_invalid_fields(raw_or_normalized_fields: dict, validated_fields: dict) -> dict:
    invalid = {}

    for field_id, value in raw_or_normalized_fields.items():
        if value is not None and validated_fields.get(field_id) is None:
            invalid[field_id] = value

    return invalid


def validate_fields_with_reask(fields: dict) -> tuple:
    validated = validate_fields(fields)
    invalid = identify_invalid_fields(fields, validated)
    return validated, invalid


if __name__ == "__main__":

    fields = {
        "email": "usernameexample.com"
    }

    print(validate_fields(fields))