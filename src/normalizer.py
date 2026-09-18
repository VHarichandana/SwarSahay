from datetime import datetime
import re

from schema_loader import get_field_by_id


HINDI_MONTH_MAP = {
    "जनवरी": "January",
    "फ़रवरी": "February",
    "फरवरी": "February",
    "मार्च": "March",
    "अप्रैल": "April",
    "मई": "May",
    "जून": "June",
    "जुलाई": "July",
    "अगस्त": "August",
    "सितंबर": "September",
    "सितम्बर": "September",
    "अक्टूबर": "October",
    "अक्तूबर": "October",
    "नवंबर": "November",
    "नवम्बर": "November",
    "दिसंबर": "December",
    "दिसम्बर": "December"
}

HINDI_NUMERAL_TRANSLATION = str.maketrans("०१२३४५६७८९", "0123456789")


def is_ambiguous_date_missing_year(value: str) -> bool:
    if value is None:
        return False

    value = str(value).strip()
    if not value:
        return False

    has_four_digit_year = bool(re.search(r"\b(19\d{2}|20\d{2})\b", value))
    if has_four_digit_year:
        return False

    # Check if there is some day or month indication without a year
    has_date_indicator = bool(
        re.search(
            r"(january|february|march|april|may|june|july|august|september|october|november|december|"
            r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|"
            r"जनवरी|फ़रवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|सितम्बर|अक्टूबर|अक्तूबर|नवंबर|नवम्बर|दिसंबर|दिसम्बर|"
            r"\b\d{1,2}[/-]\d{1,2}\b|\b\d{1,2}\s+(tarikh|tareekh|taareekh|तारीख))",
            value,
            re.IGNORECASE
        )
    )
    return has_date_indicator


def normalize_date(value: str):
    if value is None:
        return None

    value = str(value).strip()
    value = value.translate(HINDI_NUMERAL_TRANSLATION)

    for hi_month, en_month in HINDI_MONTH_MAP.items():
        if hi_month in value:
            value = value.replace(hi_month, en_month)

    # Never guess missing year
    if is_ambiguous_date_missing_year(value):
        return value

    formats = [
        "%d %B %Y",
        "%d%B %Y",
        "%d %b %Y",
        "%d%b %Y",
        "%B %d %Y",
        "%B %d, %Y",
        "%b %d %Y",
        "%b %d, %Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%Y-%m-%d"
    ]

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(value, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try matching flexible day month year patterns
    match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", value)
    if match:
        day, month_str, year = match.groups()
        for month_fmt in ["%B", "%b"]:
            try:
                parsed_month = datetime.strptime(month_str, month_fmt).month
                return f"{int(year):04d}-{parsed_month:02d}-{int(day):02d}"
            except ValueError:
                pass

    return value


def normalize_guardian_relationship(value: str):
    if value is None:
        return None

    value = value.strip().lower()

    relationship_map = {
        "maa": "mother",
        "mata": "mother",
        "mother": "mother",
        "mom": "mother",
        "pita": "father",
        "pitaji": "father",
        "father": "father",
        "dad": "father",
        "baap": "father",
        "pati": "husband",
        "husband": "husband",
        "legal guardian": "legal_guardian",
        "legal_guardian": "legal_guardian",
        "kanuni guardian": "legal_guardian",
        "sanrakshak": "legal_guardian",
        "guardian": "legal_guardian"
    }

    return relationship_map.get(value, value)


def normalize_boolean(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    true_values = {
        "haan",
        "ha",
        "yes",
        "ji",
        "ji haan",
        "true",
        "sahi hai",
        "theek hai",
        "bilkul"
    }

    false_values = {
        "nahi",
        "nahin",
        "no",
        "false",
        "alag hai",
        "galat hai"
    }

    if value in true_values:
        return True

    if value in false_values:
        return False

    return value


def normalize_enum(field_id: str, value: str):
    if value is None:
        return None

    val_clean = str(value).strip().lower()

    if field_id == "deposit_mode":
        return normalize_deposit_mode(val_clean)

    if field_id == "guardian_relationship":
        return normalize_guardian_relationship(val_clean)

    if field_id in ["identification_proof_type", "address_proof_type"]:
        if "voter" in val_clean or "pehchan" in val_clean:
            return "voter_id"
        if "driving" in val_clean or val_clean == "dl" or "license" in val_clean or "licence" in val_clean:
            return "driving_license"
        if "passport" in val_clean:
            return "passport"
        if "nrega" in val_clean or "job card" in val_clean:
            return "nrega_job_card"
        if "npr" in val_clean:
            return "npr_letter"
        return val_clean

    if field_id == "account_operation":
        op_map = {
            "guardian until majority": "guardian_until_majority",
            "guardian_until_majority": "guardian_until_majority",
            "guardian": "guardian_until_majority",
            "guardian chalayenge": "guardian_until_majority",
            "depositor after majority": "depositor_after_majority",
            "depositor_after_majority": "depositor_after_majority",
            "depositor": "depositor_after_majority",
            "depositor chalayegi": "depositor_after_majority",
            "major hone par": "depositor_after_majority"
        }
        return op_map.get(val_clean, val_clean)

    if field_id == "account_type":
        return "minor"

    return val_clean


def normalize_aadhaar(value):
    if value is None:
        return None

    value = str(value)

    digits = re.sub(r"\D", "", value)

    return digits


def normalize_pan(value):
    if value is None:
        return None

    value = str(value).strip().upper()

    value = re.sub(r"\s+", "", value)

    return value


def normalize_mobile_number(value):
    if value is None:
        return None

    value = str(value)

    digits = re.sub(r"\D", "", value)

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    return digits


def normalize_deposit_mode(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    deposit_mode_map = {
        "cash": "cash",
        "nakad": "cash",
        "cheque": "cheque",
        "check": "cheque",
        "demand draft": "dd",
        "demanddraft": "dd",
        "dd": "dd"
    }

    return deposit_mode_map.get(value, value)


def normalize_amount(value):
    if value is None:
        return None

    value = str(value).strip()

    value = value.replace("₹", "")
    value = value.replace(",", "")
    value = value.strip()

    return value


def normalize_email(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    value = value.replace(" ", "")

    return value


def normalize_person_name(value):
    if value is None:
        return None

    value = str(value).strip()

    value = re.sub(r"\s+", " ", value)

    return value


def normalize_field(field_id: str, value):
    if value is None:
        return None

    field_schema = get_field_by_id(field_id)

    if field_schema is None:
        return value

    field_type = field_schema.get("type")
    normalization = field_schema.get("normalization")

    if field_type == "date":
        return normalize_date(value)

    if normalization == "spoken_date":
        return normalize_date(value)

    if field_type == "boolean":
        return normalize_boolean(value)

    if field_type == "enum":
        return normalize_enum(field_id, value)

    if normalization == "person_name":
        return normalize_person_name(value)

    if field_id == "guardian_relationship":
        return normalize_guardian_relationship(value)

    if normalization == "spoken_digits":
        if field_id == "mobile_number":
            return normalize_mobile_number(value)

        return normalize_aadhaar(value)

    if normalization == "spoken_alphanumeric":
        return normalize_pan(value)

    if normalization == "email":
        return normalize_email(value)

    if field_id == "deposit_mode":
        return normalize_deposit_mode(value)

    if field_id == "initial_deposit_amount":
        return normalize_amount(value)

    return value


def normalize_fields(fields: dict) -> dict:
    normalized = {}

    for field_id, value in fields.items():
        normalized[field_id] = normalize_field(
            field_id,
            value
        )

    return normalized


if __name__ == "__main__":

    fields = {
        "date_of_birth": "15 March 2018",
        "instrument_date": "20 March 2026",
        "guardian_relationship": "maa",
        "permanent_same_as_present": "haan",
        "guardian_aadhaar": "1234 5678 9012",
        "guardian_pan": "abcde 1234 f",
        "mobile_number": "+91 98765 43210",
        "deposit_mode": "demand draft",
        "initial_deposit_amount": "₹ 5,000",
        "email": " User.Name@Example.COM ",
        "account_holder_name": "  Ananya   Sharma  "
    }

    print(normalize_fields(fields))