import os
import sys
import unittest
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schema_loader import (
    load_schema,
    get_all_fields,
    get_required_fields,
    get_conversational_required_fields,
    get_field_by_id
)
from normalizer import (
    normalize_date,
    normalize_guardian_relationship,
    normalize_boolean,
    normalize_aadhaar,
    normalize_pan,
    normalize_mobile_number,
    normalize_deposit_mode,
    normalize_amount,
    normalize_enum,
    normalize_field,
    normalize_fields,
    is_ambiguous_date_missing_year
)
from field_validator import (
    validate_field,
    validate_fields,
    validate_date,
    validate_boolean,
    validate_number,
    validate_enum,
    validate_deposit_mode,
    validate_email,
    identify_invalid_fields,
    validate_fields_with_reask
)
from form_state import (
    update_form_state,
    condition_is_met,
    get_conditional_fields,
    get_missing_required_fields,
    get_next_missing_field
)
from question_generator import (
    generate_question,
    generate_reask_question,
    generate_confirmation_prompt,
    is_sensitive_field,
    NON_CONVERSATIONAL_FIELDS,
    SENSITIVE_CONFIRMATION_FIELDS
)


class TestValidExtractionAndNormalization(unittest.TestCase):
    """Test normalization and validation on valid inputs."""

    def test_date_normalization(self):
        self.assertEqual(normalize_date("15 March 2018"), "2018-03-15")
        self.assertEqual(normalize_date("March 15 2018"), "2018-03-15")
        self.assertEqual(normalize_date("15/03/2018"), "2018-03-15")
        self.assertEqual(normalize_date("15-03-2018"), "2018-03-15")
        self.assertEqual(normalize_date("15.03.2018"), "2018-03-15")
        self.assertEqual(normalize_date("15 मार्च 2018"), "2018-03-15")
        self.assertEqual(normalize_date("१५ मार्च २०१८"), "2018-03-15")

    def test_guardian_relationship_normalization(self):
        self.assertEqual(normalize_guardian_relationship("maa"), "mother")
        self.assertEqual(normalize_guardian_relationship("mata"), "mother")
        self.assertEqual(normalize_guardian_relationship("mom"), "mother")
        self.assertEqual(normalize_guardian_relationship("pita"), "father")
        self.assertEqual(normalize_guardian_relationship("pitaji"), "father")
        self.assertEqual(normalize_guardian_relationship("dad"), "father")
        self.assertEqual(normalize_guardian_relationship("pati"), "husband")
        self.assertEqual(normalize_guardian_relationship("kanuni guardian"), "legal_guardian")
        self.assertEqual(normalize_guardian_relationship("sanrakshak"), "legal_guardian")

    def test_boolean_normalization(self):
        self.assertTrue(normalize_boolean("haan"))
        self.assertTrue(normalize_boolean("ji haan"))
        self.assertTrue(normalize_boolean("yes"))
        self.assertTrue(normalize_boolean("sahi hai"))
        self.assertTrue(normalize_boolean("theek hai"))
        self.assertFalse(normalize_boolean("nahi"))
        self.assertFalse(normalize_boolean("nahin"))
        self.assertFalse(normalize_boolean("no"))
        self.assertFalse(normalize_boolean("alag hai"))

    def test_aadhaar_normalization(self):
        self.assertEqual(normalize_aadhaar("1234 5678 9012"), "123456789012")
        self.assertEqual(normalize_aadhaar("1234-5678-9012"), "123456789012")

    def test_pan_normalization(self):
        self.assertEqual(normalize_pan("abcde 1234 f"), "ABCDE1234F")

    def test_mobile_normalization(self):
        self.assertEqual(normalize_mobile_number("+91 98765 43210"), "9876543210")
        self.assertEqual(normalize_mobile_number("919876543210"), "9876543210")
        self.assertEqual(normalize_mobile_number("9876543210"), "9876543210")

    def test_amount_normalization(self):
        self.assertEqual(normalize_amount("₹ 5,000"), "5000")
        self.assertEqual(normalize_amount("1,50,000"), "150000")
        self.assertEqual(normalize_amount("500"), "500")

    def test_enum_normalization(self):
        self.assertEqual(normalize_enum("deposit_mode", "demand draft"), "dd")
        self.assertEqual(normalize_enum("deposit_mode", "nakad"), "cash")
        self.assertEqual(normalize_enum("deposit_mode", "cheque"), "cheque")
        self.assertEqual(normalize_enum("identification_proof_type", "voter card"), "voter_id")
        self.assertEqual(normalize_enum("identification_proof_type", "driving licence"), "driving_license")
        self.assertEqual(normalize_enum("address_proof_type", "nrega job card"), "nrega_job_card")
        self.assertEqual(normalize_enum("account_operation", "guardian chalayenge"), "guardian_until_majority")
        self.assertEqual(normalize_enum("account_operation", "depositor chalayegi"), "depositor_after_majority")


class TestInvalidValues(unittest.TestCase):
    """Test that invalid values fail validation and are rejected."""

    def test_invalid_mobile(self):
        self.assertIsNone(validate_field("mobile_number", "12345"))
        self.assertIsNone(validate_field("mobile_number", "5876543210"))  # Indian mobile starts 6-9
        self.assertIsNotNone(validate_field("mobile_number", "9876543210"))

    def test_invalid_date_and_missing_year(self):
        # Missing year must fail validation and be identified as ambiguous
        self.assertTrue(is_ambiguous_date_missing_year("15 March"))
        self.assertTrue(is_ambiguous_date_missing_year("15 तारीख"))
        self.assertFalse(is_ambiguous_date_missing_year("15 March 2018"))
        # Missing year remains un-normalized and fails date validation
        norm = normalize_date("15 March")
        self.assertEqual(norm, "15 March")
        self.assertIsNone(validate_field("date_of_birth", norm))

    def test_invalid_amount(self):
        self.assertIsNone(validate_field("initial_deposit_amount", "100"))  # < 250 min
        self.assertIsNone(validate_field("initial_deposit_amount", "200000"))  # > 150000 max
        self.assertIsNotNone(validate_field("initial_deposit_amount", "5000"))

    def test_invalid_aadhaar(self):
        self.assertIsNone(validate_field("guardian_aadhaar", "12345"))
        self.assertIsNone(validate_field("guardian_aadhaar", "12345678901A"))
        self.assertIsNotNone(validate_field("guardian_aadhaar", "123456789012"))

    def test_invalid_pan(self):
        self.assertIsNone(validate_field("guardian_pan", "12345"))
        self.assertIsNone(validate_field("guardian_pan", "ABCDE1234"))
        self.assertIsNotNone(validate_field("guardian_pan", "ABCDE1234F"))

    def test_invalid_enums(self):
        self.assertIsNone(validate_field("deposit_mode", "bitcoin"))
        self.assertIsNone(validate_field("guardian_relationship", "friend"))
        self.assertIsNone(validate_field("identification_proof_type", "college_id"))
        self.assertIsNotNone(validate_field("deposit_mode", "cash"))
        self.assertIsNotNone(validate_field("guardian_relationship", "mother"))


class TestFormStatePreservation(unittest.TestCase):
    """Test that existing form state is preserved when updates/invalids occur."""

    def test_preserve_state_on_partial_update(self):
        current_state = {
            "account_holder_name": "Ananya Sharma",
            "date_of_birth": "2018-03-15"
        }
        new_extracted = {
            "mobile_number": "9876543210"
        }
        updated = update_form_state(dict(current_state), new_extracted)
        self.assertEqual(updated["account_holder_name"], "Ananya Sharma")
        self.assertEqual(updated["date_of_birth"], "2018-03-15")
        self.assertEqual(updated["mobile_number"], "9876543210")

    def test_invalid_value_not_saved_to_state(self):
        current_state = {
            "account_holder_name": "Ananya Sharma",
            "mobile_number": "9876543210"
        }
        # Extracted value has invalid mobile
        raw = {"mobile_number": "12345"}
        validated = validate_fields(raw)
        self.assertIsNone(validated["mobile_number"])

        updated = update_form_state(dict(current_state), validated)
        # Mobile number must retain original valid value
        self.assertEqual(updated["mobile_number"], "9876543210")


class TestCorrections(unittest.TestCase):
    """Test explicit user corrections."""

    def test_correction_overwrites_field(self):
        current_state = {
            "account_holder_name": "Ananya Sharma",
            "date_of_birth": "2018-03-15"
        }
        correction = {
            "account_holder_name": "Kavya Sharma"
        }
        updated = update_form_state(dict(current_state), correction)
        self.assertEqual(updated["account_holder_name"], "Kavya Sharma")
        self.assertEqual(updated["date_of_birth"], "2018-03-15")


class TestConditionalActivation(unittest.TestCase):
    """Test conditional fields activation and deactivation."""

    def test_deposit_mode_conditional_instrument_date(self):
        cheque_state = {"deposit_mode": "cheque"}
        self.assertIn("instrument_date", get_conditional_fields(cheque_state))

        dd_state = {"deposit_mode": "dd"}
        self.assertIn("instrument_date", get_conditional_fields(dd_state))

        cash_state = {"deposit_mode": "cash"}
        self.assertNotIn("instrument_date", get_conditional_fields(cash_state))

    def test_permanent_address_conditional(self):
        diff_address_state = {"permanent_same_as_present": False}
        self.assertIn("permanent_address", get_conditional_fields(diff_address_state))

        same_address_state = {"permanent_same_as_present": True}
        self.assertNotIn("permanent_address", get_conditional_fields(same_address_state))


class TestReaskBehavior(unittest.TestCase):
    """Test identifying invalid fields and generating re-ask questions."""

    def test_reask_identification_and_messages(self):
        raw = {
            "mobile_number": "12345",
            "date_of_birth": "15 March",
            "initial_deposit_amount": "50"
        }
        validated, invalid = validate_fields_with_reask(raw)
        self.assertIn("mobile_number", invalid)
        self.assertIn("date_of_birth", invalid)
        self.assertIn("initial_deposit_amount", invalid)

        mobile_reask = generate_reask_question("mobile_number", invalid["mobile_number"])
        self.assertIn("10 digit", mobile_reask)

        dob_reask = generate_reask_question("date_of_birth", invalid["date_of_birth"])
        self.assertIn("saal", dob_reask.lower())

        amount_reask = generate_reask_question("initial_deposit_amount", invalid["initial_deposit_amount"])
        self.assertIn("250", amount_reask)


class TestAmbiguityAndConfirmation(unittest.TestCase):
    """Test sensitive fields and confirmation generation."""

    def test_sensitive_fields_detection(self):
        self.assertTrue(is_sensitive_field("account_holder_name"))
        self.assertTrue(is_sensitive_field("guardian_full_name"))
        self.assertTrue(is_sensitive_field("date_of_birth"))
        self.assertTrue(is_sensitive_field("guardian_aadhaar"))
        self.assertTrue(is_sensitive_field("guardian_pan"))
        self.assertTrue(is_sensitive_field("mobile_number"))
        self.assertFalse(is_sensitive_field("bank_name"))

    def test_confirmation_prompt_generation(self):
        prompt = generate_confirmation_prompt("account_holder_name", "Ananya Sharma")
        self.assertIn("Ananya Sharma", prompt)
        self.assertIn("sahi hai", prompt)

        aadhaar_prompt = generate_confirmation_prompt("guardian_aadhaar", "123456789012")
        self.assertIn("1234 5678 9012", aadhaar_prompt)


class TestConversationalFieldFiltering(unittest.TestCase):
    """Test that manual/bank-only/derived fields are excluded from conversational flow."""

    def test_non_conversational_fields_not_asked(self):
        conversational_required = get_conversational_required_fields()
        self.assertNotIn("applicant_photograph", conversational_required)
        self.assertNotIn("guardian_signature", conversational_required)
        self.assertNotIn("account_type", conversational_required)

        # Question generator returns None for manual/bank-only fields
        self.assertIsNone(generate_question("applicant_photograph"))
        self.assertIsNone(generate_question("guardian_signature"))
        self.assertIsNone(generate_question("bank_account_number"))


class TestMultiTurnConversations(unittest.TestCase):
    """Test simulated multi-turn form filling."""

    def test_multiturn_dialogue_flow(self):
        state = {}

        # Turn 1: user provides name and dob
        turn1_extracted = {
            "account_holder_name": "Ananya Sharma",
            "date_of_birth": "15 March 2018"
        }
        norm1 = normalize_fields(turn1_extracted)
        val1 = validate_fields(norm1)
        state = update_form_state(state, val1)

        self.assertEqual(state["account_holder_name"], "Ananya Sharma")
        self.assertEqual(state["date_of_birth"], "2018-03-15")

        # Turn 2: user provides invalid mobile
        turn2_extracted = {"mobile_number": "12345"}
        norm2 = normalize_fields(turn2_extracted)
        val2, invalid2 = validate_fields_with_reask(norm2)
        self.assertIn("mobile_number", invalid2)
        state = update_form_state(state, val2)

        # State not corrupted
        self.assertNotIn("mobile_number", state)
        reask = generate_reask_question("mobile_number", invalid2["mobile_number"])
        self.assertIn("10 digit", reask)

        # Turn 3: user re-provides valid mobile
        turn3_extracted = {"mobile_number": "9876543210"}
        norm3 = normalize_fields(turn3_extracted)
        val3 = validate_fields(norm3)
        state = update_form_state(state, val3)
        self.assertEqual(state["mobile_number"], "9876543210")

        # Turn 4: user provides deposit mode = cheque
        turn4_extracted = {"deposit_mode": "cheque"}
        norm4 = normalize_fields(turn4_extracted)
        val4 = validate_fields(norm4)
        state = update_form_state(state, val4)

        # Now instrument_date should be active conditional field
        active_conditionals = get_conditional_fields(state)
        self.assertIn("instrument_date", active_conditionals)


if __name__ == "__main__":
    unittest.main()
