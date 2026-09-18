# Phase 2: NLU & Field Extraction Evaluation Report

## 1. Objective

The objective of Phase 2 is to convert Hindi and Hinglish conversational user transcripts into validated, structured fields for the **Sukanya Samriddhi Account Form 1**, maintaining fidelity to official scheme rules, conversational naturalness, and robust error recovery.

Key goals achieved:
- Extracting structured data from diverse Hindi and Hinglish utterances.
- Strict schema adherence based on `schema/sukanya_schema.json` without altering field identifiers or enum constraints.
- Zero-hallucination policy: missing information (such as missing date years) is never guessed.
- Conversational state management: valid existing form fields are preserved, while user corrections explicitly override prior values.
- Automated validation and targeted re-ask handling with format explanations.
- Deterministic confirmation prompts for sensitive fields.
- Exclusion of back-office, derived, and manual fields (`MANUAL`, `BANK_ONLY`, `DERIVED`) from user-facing dialogue.

---

## 2. Architecture & Pipeline Overview

The Phase 2 pipeline operates in a sequential, deterministic flow:

```
[User Transcript + Current Form State]
                 │
                 ▼
     [1. Groq LLM Extractor]
     (openai/gpt-oss-20b with compact schema constraints)
                 │
                 ▼
        [2. Normalizer]
     (Hindi numerals, dates, enums, booleans, amounts)
                 │
                 ▼
      [3. Field Validator]
     (Regex, boundaries, enum validity, missing year detection)
                 │
        ┌────────┴────────────────────────┐
        ▼                                 ▼
 [Valid Fields]                   [Invalid Fields]
        │                                 │
        ▼                                 ▼
[4. Update Form State]          [Generate Re-ask Prompts]
        │
        ▼
[5. Check Active Conditionals]
        │
        ▼
[6. Sensitive Field Confirmation Prompts]
        │
        ▼
[7. Next Missing Field & Conversational Question Generation]
```

---

## 3. Component Details

### 3.1 Schema Loader (`src/schema_loader.py`)
- Loads `schema/sukanya_schema.json` as the single source of truth (with fallback to `data/sukanya_schema.json`).
- Categorizes fields into conversational vs. non-conversational.
- Excludes `MANUAL`, `BANK_ONLY`, and `DERIVED` fields (`applicant_signature_or_thumb`, `operating_instructions`, `specimen_signature_1`, etc.) from conversational requirements.

### 3.2 Extractor (`src/extractor.py`)
- Powered by Groq LLM (`openai/gpt-oss-20b`) via standard Chat Completions API.
- Prompt incorporates field identifiers, field types, descriptions, and allowed options directly from the schema.
- Context-aware extraction: passes current form state so the LLM understands user corrections (e.g., *"Nahi, naam Ananya nahi, Kavya hai"*).
- Zero-shot rules prevent false positive extractions from conversational fillers and hard negatives (e.g., general scheme inquiries or greeting phrases).
- Cost & latency optimization: capped at `max_tokens=350` and uses deterministic caching (`data/.nlu_cache.json`) for reproducible benchmark testing.

### 3.3 Normalizer (`src/normalizer.py`)
- **Numerals**: Converts Hindi Devanagari numerals (०, १, २, ३...) and words (paanch sau -> 500) into standard digits.
- **Dates**: Normalizes varied Hindi/Hinglish date formats ("15 March 2018", "15/03/2018", "25 December 2016") to ISO-8601 `YYYY-MM-DD`. Flags ambiguous dates lacking a year.
- **Enums**: Normalizes relationship names (`maa`/`mata ji` -> `mother`, `pita ji` -> `father`), deposit modes (`rokad`/`nakad` -> `cash`, `cheque`, `dd`), and proof types (`voter id` -> `voter_id`, `driving licence` -> `driving_license`).
- **Booleans**: Normalizes affirmations (`haan`, `sahi hai`, `sweekar`) and negations (`nahi`, `alag hai`) into boolean values.

### 3.4 Field Validator (`src/field_validator.py`)
- Performs schema-driven validation against regex patterns, value ranges, and enum sets.
- Detects invalid inputs via `identify_invalid_fields`:
  - Aadhaar: exactly 12 digits (fails incomplete numbers).
  - Mobile: exactly 10 digits starting with 6-9.
  - PAN: standard 10-character alphanumeric pattern (`[A-Z]{5}[0-9]{4}[A-Z]`).
  - Deposit amount: numeric value within scheme boundaries (₹250 to ₹1,50,000).
  - Date of birth: valid calendar date; flags dates lacking a year as invalid.
  - Enums: validated strictly against schema `options`.

### 3.5 Question Generator & Re-Ask Handling (`src/question_generator.py`)
- **Conversational Questions**: 100% question coverage across personal details, guardian info, identification documents, deposit modes, address, and declarations.
- **Targeted Re-ask Handling (`generate_reask_question`)**:
  - Provides constructive format guidance upon validation failure:
    - Mobile: *"Kripya 10 digit ka sahi mobile number batayein (jaise 9876543210)."*
    - Date missing year: *"Kripya janam ka saal bhi batayein. Saal ke bina taareekh darj nahi ki ja sakti."*
    - Amount: *"Kripya sahi rashi batayein (kam se kam 250 aur zyada se zyada 1,50,000 rupaye)."*
    - Aadhaar: *"Kripya 12 digit ka sahi Aadhaar number batayein."*
- **Confirmation Prompts (`generate_confirmation_prompt`)**:
  - Automatically triggers confirmation for high-stakes fields (`account_holder_name`, `initial_deposit_amount`, `date_of_birth`, `guardian_aadhaar`, `mobile_number`, `guardian_pan`).

### 3.6 Form State & Turn Orchestration (`src/form_state.py`)
- `update_form_state`: Deterministically merges valid updates while preserving existing fields.
- `get_conditional_fields`: Evaluates conditional dependencies dynamically (e.g. `deposit_mode == 'cheque'` -> `instrument_date`; `permanent_same_as_present == False` -> `permanent_address`).
- `get_missing_required_fields`: Computes missing mandatory conversational fields, prioritizing primary fields before conditional branches.
- `process_turn`: Orchestrates the complete end-to-end turn flow.

---

## 4. Evaluation Dataset

The synthetic evaluation dataset (`data/sample_conversations.json`) contains **46 examples** covering all operational scenarios:

| Category | Count | Description |
| :--- | :---: | :--- |
| **Clean Single-Field Extractions** | 16 | Single field utterances for name, DOB, deposit, bank, branch, address, PAN, Aadhaar |
| **Multi-Field Utterances** | 4 | Utterances containing 2 to 4 fields simultaneously |
| **Explicit State Corrections** | 4 | Overriding existing state (name, mobile, relationship, deposit amount) |
| **Hard Negatives / Out-of-Domain** | 6 | General queries, scheme questions, greetings (yielding empty extractions) |
| **Invalid Inputs (Triggering Re-Ask)** | 4 | Incomplete mobile, date without year, short Aadhaar, deposit amount below ₹250 |
| **Conditional Field Utterances** | 4 | Cheque/DD instrument date, separate permanent address |
| **Boolean Declarations & Statutory** | 5 | Existing account declaration, citizenship/residency, terms acceptance |
| **Enum & Document Types** | 3 | Voter ID, Driving License, operation mode |

---

## 5. Quantitative Evaluation Results

Evaluation script: `src/evaluate_nlu.py`

```text
--------------------
NLU Evaluation Summary
--------------------
Total test examples:     46
Expected field values:   48
Correct field values:    48
False Positives (FP):    0
False Negatives (FN):    0

Field Accuracy:          100.0% (1.0000)
Precision:               100.0% (1.0000)
Recall:                  100.0% (1.0000)
F1 Score:                1.0000
```

### Unit Test Results
Test suite: `tests/test_phase2_nlu.py`

```text
Ran 24 tests in 0.065s

OK
```

#### Test Suite Breakdown:
1. `TestValidExtractionAndNormalization` (8 tests):
   - Aadhaar normalization (stripping spaces, formatting)
   - Amount normalization (Hindi word forms and numeric strings)
   - Boolean normalization (affirmations, statutory declarations)
   - Date normalization (ISO conversion, Hindi month translation)
   - Enum normalization (schema-compliant values)
   - Guardian relationship normalization (mother, father, guardian)
   - Mobile normalization
   - PAN normalization (capitalization, whitespace)
2. `TestInvalidValues` (6 tests):
   - Incomplete and non-digit Aadhaar rejection
   - Out-of-bounds deposit amount rejection (< ₹250 or > ₹1,50,000)
   - Incomplete date rejection (missing calendar year)
   - Invalid enum rejection
   - Invalid mobile rejection (< 10 digits or non-numeric)
   - Invalid PAN format rejection
3. `TestFormStatePreservation` (2 tests):
   - Preservation of valid fields during partial updates
   - Prevention of invalid extracted values from corrupting form state
4. `TestCorrections` (1 test):
   - Explicit user correction correctly overwriting previous field value
5. `TestConditionalActivation` (2 tests):
   - Activation of `instrument_date` when deposit mode is cheque/DD
   - Activation of `permanent_address` when `permanent_same_as_present` is false
6. `TestConversationalFieldFiltering` (1 test):
   - Ensuring `MANUAL`, `BANK_ONLY`, and `DERIVED` fields are excluded from conversational prompts
7. `TestReaskBehavior` (1 test):
   - Invalid field detection and format guidance generation
8. `TestAmbiguityAndConfirmation` (2 tests):
   - Identification of sensitive fields requiring verification
   - Generation of confirmation prompts with extracted values
9. `TestMultiTurnConversations` (1 test):
   - End-to-end multi-turn dialogue simulation verifying state persistence across turns

---

## 6. Limitations & Edge Cases

1. **Synthetic Transcripts**:
   - The current evaluation uses normalized text transcripts. While it includes colloquial Hinglish, real-world speech from offline ASR (tested in Phase 1) will contain acoustic misrecognitions, disfluencies, stuttering, and non-standard dialect variants.
2. **Strict Date Policy**:
   - Transcripts with dates missing the year (e.g. *"15 March"*) are intentionally not filled with current/assumed year to protect legal form integrity. A re-ask question is deterministically raised.
3. **External LLM Latency & Quotas**:
   - Groq API has rate limits (tokens per day on free tier). The extractor includes rate-limit retry with dynamic backoff and strict token ceilings (`max_tokens=350`).
4. **KYC Document Scope**:
   - As per project constraints, `identification_proof_type` and `address_proof_type` strictly adhere to the Form 1 schema enums (`passport`, `driving_license`, `voter_id`, `nrega_job_card`, `npr_letter`). Aadhaar and PAN are handled in their dedicated fields and not injected into proof type enums.

---

## 7. Recommendation & Phase 2 Freeze

All Phase 2 requirements specified in the project roadmap and approval criteria have been met:
- [x] Schema-driven enum normalization & validation
- [x] Full conversational question coverage across all form sections
- [x] Validation-failure re-ask with contextual guidance
- [x] Deterministic confirmation handling for sensitive fields
- [x] Non-conversational field filtering (`MANUAL`, `BANK_ONLY`, `DERIVED`)
- [x] Turn orchestration via `process_turn`
- [x] Comprehensive test suite (24 unit tests, all passing)
- [x] Multi-scenario evaluation (46 synthetic cases, 100% precision/recall/F1)

**Phase 2 is fully functional, thoroughly tested, and ready to freeze.**
