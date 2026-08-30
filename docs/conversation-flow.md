# Sukanya Samriddhi Form-1 — Form Analysis

## 1. Purpose

This document converts the actual Sukanya Samriddhi Form-1 into a structured specification for SwarSahay.

The purpose is to determine:

* What information the user needs to provide
* Which fields are required
* Which fields are optional
* Which fields are conditional
* Which fields can be derived
* Which fields require manual completion
* Which fields belong only to the bank
* What format each field should have
* What speech normalization is required

---

# 2. Field Classification

Each field is assigned one of the following categories.

| Classification | Meaning                                                  |
| -------------- | -------------------------------------------------------- |
| `REQUIRED`     | Must be collected for the supported application workflow |
| `OPTIONAL`     | Can be provided but is not mandatory                     |
| `CONDITIONAL`  | Required only when a specific condition applies          |
| `DERIVED`      | Generated from information already collected             |
| `CONFIRMATION` | Requires explicit confirmation from the user             |
| `MANUAL`       | Requires physical/manual completion                      |
| `BANK_ONLY`    | Completed by the bank                                    |

---

# 3. General Speech Normalization

Users will not necessarily speak information in the same format in which it appears on the form.

SwarSahay therefore needs a normalization layer.

```text
Natural Hindi Speech
        ↓
Speech-to-Text
        ↓
Normalization
        ↓
Structured Field
```

Examples:

```text
"pandrah March do hazaar atharah"
                ↓
        15 March 2018
                ↓
        2018-03-15
```

---

# 4. Section A — Application Details

| Form Field           | Internal Name                | Type   | Status      | Expected Format          |
| -------------------- | ---------------------------- | ------ | ----------- | ------------------------ |
| Bank                 | `bank_name`                  | string | REQUIRED    | Text                     |
| Branch               | `branch_name`                | string | REQUIRED    | Text                     |
| Applicant/Guardian   | `applicant_role`             | enum   | REQUIRED    | Controlled value         |
| Initial subscription | `initial_subscription`       | number | REQUIRED    | Positive currency amount |
| Amount in words      | `initial_subscription_words` | string | DERIVED     | Generated text           |
| Payment mode         | `payment_mode`               | enum   | REQUIRED    | cash / cheque / DD       |
| Payment date         | `payment_date`               | date   | REQUIRED    | YYYY-MM-DD internally    |
| Cheque/DD date       | `instrument_date`            | date   | CONDITIONAL | YYYY-MM-DD               |
| Cheque/DD reference  | `payment_reference`          | string | CONDITIONAL | Alphanumeric             |
| Applicant photograph | `applicant_photo`            | image  | MANUAL      | Physical/image           |

### Payment Mode

Allowed values:

```text
cash
cheque
demand_draft
```

If payment mode is cheque or demand draft, relevant instrument information becomes applicable.

---

# 5. Section B — Depositor Details

The depositor is the girl in whose name the account is opened.

| Form Field        | Internal Name         | Type   | Status   | Expected Format       |
| ----------------- | --------------------- | ------ | -------- | --------------------- |
| Name of Depositor | `depositor_name`      | string | REQUIRED | Personal name         |
| Date of Birth     | `depositor_dob`       | date   | REQUIRED | YYYY-MM-DD internally |
| DOB in words      | `depositor_dob_words` | string | DERIVED  | Generated from DOB    |

### Name Normalization

Names may be spoken in Hindi but need to be represented consistently.

Examples:

```text
"अनन्या शर्मा"
"Ananya Sharma"
"Ananya Sharma ji ki beti"
```

The extraction layer should identify the actual name rather than retaining surrounding conversational words.

Important:

> Transliteration should not silently alter a person's official name.

If speech recognition produces:

```text
"Anaya Sharma"
```

while the user says:

```text
"Ananya Sharma"
```

the system should ask for confirmation rather than assuming the spelling.

---

# 6. Date Normalization

Dates are one of the most important speech ambiguities.

Possible user expressions include:

```text
15 March 2018
March 15 2018
15/03/2018
15-03-2018
15 March, 2018
पंद्रह मार्च 2018
पंद्रह मार्च दो हजार अठारह
15 3 2018
```

All unambiguous representations should normalize to:

```text
2018-03-15
```

### Ambiguous Date

If the user says:

```text
"15 March"
```

the year is missing.

SwarSahay must ask:

> "Kripya janam ka saal bhi batayein."

It must not guess.

If a numeric date is ambiguous in interpretation, the system should ask for clarification.

---

# 7. Section C — Guardian Details

| Form Field                   | Internal Name                 | Type   | Status   | Expected Format |
| ---------------------------- | ----------------------------- | ------ | -------- | --------------- |
| Name of Guardian             | `guardian_name`               | string | REQUIRED | Personal name   |
| Husband/Father/Mother's Name | `guardian_parent_spouse_name` | string | REQUIRED | Personal name   |
| Guardian DOB                 | `guardian_dob`                | date   | REQUIRED | YYYY-MM-DD      |
| Guardian DOB in words        | `guardian_dob_words`          | string | DERIVED  | Generated       |

### Guardian Relationship

Internal field:

```text
guardian_relationship
```

Possible values:

```text
father
mother
husband
other_guardian
```

Speech examples:

```text
"Main uska pita hoon."
"Main uski maa hoon."
"Main uska guardian hoon."
```

The system should map conversational expressions to controlled values.

---

# 8. Section D — Guardian KYC

| Form Field     | Internal Name      | Type   | Status   | Expected Format |
| -------------- | ------------------ | ------ | -------- | --------------- |
| Aadhaar Number | `guardian_aadhaar` | string | REQUIRED | 12 digits       |
| PAN            | `guardian_pan`     | string | REQUIRED | PAN format      |

## Aadhaar Speech

Aadhaar is particularly difficult in speech because users may say:

```text
"1234 5678 9012"
```

or:

```text
"one two three four..."
```

or Hindi number words.

The system should normalize spoken digits into:

```text
123456789012
```

Validation:

```text
Exactly 12 numeric digits
```

The system should not perform actual Aadhaar authentication.

---

# 9. PAN Normalization

PAN is an alphanumeric identifier.

Example:

```text
ABCDE1234F
```

The user may pronounce it character-by-character.

The system should preserve the sequence and normalize case.

Example:

```text
"ABC D E one two three four F"
        ↓
ABCDE1234F
```

The system performs only format validation.

It does not verify ownership.

---

# 10. Section E — Address

## Present Address

Internal field:

```text
present_address
```

Status:

```text
REQUIRED
```

## Permanent Address

Internal field:

```text
permanent_address
```

Status:

```text
REQUIRED
```

For V1, the full address may initially be represented as a text value.

Example:

```json
{
  "present_address": "House 12, Hyderabad, Telangana, 500001"
}
```

### Future Structured Address

The architecture should allow later expansion to:

```text
house
street
locality
village
city
district
state
pincode
```

### Same Address

If the user says:

> "Permanent address bhi yahi hai."

The system can reuse the present address after explicit confirmation.

---

# 11. Section F — Contact Details

| Form Field       | Internal Name      | Type   | Status   | Expected Format             |
| ---------------- | ------------------ | ------ | -------- | --------------------------- |
| Telephone Number | `telephone_number` | string | OPTIONAL | Telephone format            |
| Mobile Number    | `mobile_number`    | string | REQUIRED | Indian mobile number format |
| Email ID         | `email`            | string | OPTIONAL | Email format                |

The exact required/optional interpretation should be confirmed against the version of the physical form being implemented.

The schema should allow optional contact fields without blocking the conversation unnecessarily.

---

# 12. Section G — Account Type

Form value:

```text
Minor
```

Internal field:

```text
account_type
```

Type:

```text
enum
```

Value:

```text
minor
```

Classification:

```text
DERIVED
```

The user does not need to manually provide this because the selected form itself establishes the account type.

---

# 13. Section H — Birth Certificate

| Form Field         | Internal Name                         | Type   | Status   | Expected Format |
| ------------------ | ------------------------------------- | ------ | -------- | --------------- |
| Certificate Number | `birth_certificate_number`            | string | REQUIRED | Alphanumeric    |
| Date of Issue      | `birth_certificate_issue_date`        | date   | REQUIRED | YYYY-MM-DD      |
| Issuing Authority  | `birth_certificate_issuing_authority` | string | REQUIRED | Text            |

SwarSahay collects the information.

Document verification itself is outside V1.

---

# 14. Section I — KYC Documents

The form asks for:

1. Proof of identification
2. Address proof

## Identification Proof

Internal field:

```text
identification_proof
```

Possible values:

```text
passport
driving_license
voter_id
nrega_job_card
npr_letter
```

## Address Proof

Internal field:

```text
address_proof
```

Possible values:

```text
passport
driving_license
voter_id
nrega_job_card
npr_letter
```

The system collects the document type.

It does not verify the physical document.

---

# 15. Section J — Account Operation

| Form Field        | Internal Name       | Type | Status   |
| ----------------- | ------------------- | ---- | -------- |
| Account operation | `account_operation` | enum | REQUIRED |

Allowed values:

```text
guardian_until_majority
depositor_after_majority
```

---

# 16. Section K — Specimen Signatures

The form contains specimen signatures.

Fields:

```text
specimen_signature_1
specimen_signature_2
specimen_signature_3
```

Classification:

```text
MANUAL
```

SwarSahay should display these as:

```text
Manual completion required
```

It should never generate or imitate a signature.

---

# 17. Section L — Declarations

The form contains declarations that must not simply be inferred by the AI.

## Declaration 1

No existing Sukanya Samriddhi Account in the depositor's name.

Internal field:

```text
declaration_no_existing_account
```

Type:

```text
boolean
```

Classification:

```text
CONFIRMATION
```

The user must explicitly confirm.

---

## Declaration 2

Residency/citizenship declaration.

Internal field:

```text
declaration_residency_citizenship
```

Type:

```text
boolean
```

Classification:

```text
CONFIRMATION
```

---

## Declaration 3

Agreement to applicable scheme provisions and rules.

Internal field:

```text
declaration_scheme_rules
```

Type:

```text
boolean
```

Classification:

```text
CONFIRMATION
```

---

# 18. Section M — Guardian Signature

| Field                     | Internal Name               | Status  |
| ------------------------- | --------------------------- | ------- |
| Application date          | `application_date`          | DERIVED |
| Guardian signature        | `guardian_signature`        | MANUAL  |
| Guardian thumb impression | `guardian_thumb_impression` | MANUAL  |

---

# 19. Section N — Nomination

The nomination section can contain multiple nominees.

Maximum supported entries in the form:

```text
4
```

Internal representation:

```json
{
  "nominees": []
}
```

Each nominee contains:

| Form Field            | Internal Name           | Type   | Status      |
| --------------------- | ----------------------- | ------ | ----------- |
| Name                  | `name`                  | string | REQUIRED    |
| Relationship          | `relationship`          | string | REQUIRED    |
| Full Address          | `address`               | string | REQUIRED    |
| Aadhaar               | `aadhaar`               | string | OPTIONAL    |
| DOB if minor          | `date_of_birth`         | date   | CONDITIONAL |
| Share of entitlement  | `share_of_entitlement`  | number | REQUIRED    |
| Nature of entitlement | `nature_of_entitlement` | string | REQUIRED    |
| Trustee/Owner         | `trustee_or_owner`      | string | REQUIRED    |

---

# 20. Nominee Aadhaar

The form explicitly identifies nominee Aadhaar as optional.

Therefore:

```text
status = OPTIONAL
```

The system should not repeatedly ask for it if the user does not provide it.

---

# 21. Minor Nominee Logic

If the nominee is a minor, additional information is required.

Conceptually:

```text
Nominee
   ↓
Is nominee a minor?
   │
   ├── No → Continue
   │
   └── Yes
        ↓
Collect appointee details
```

---

# 22. Section O — Minor Nominee Appointee

| Form Field   | Internal Name            | Type   | Status      |
| ------------ | ------------------------ | ------ | ----------- |
| Name         | `appointee_name`         | string | CONDITIONAL |
| Relationship | `appointee_relationship` | string | CONDITIONAL |
| Address      | `appointee_address`      | string | CONDITIONAL |

These fields are activated only when the relevant nominee is a minor.

---

# 23. Section P — Witnesses

The form contains two witnesses.

Each witness contains:

```text
name
address
signature
```

Internal structure:

```json
{
  "witnesses": [
    {
      "name": null,
      "address": null,
      "signature": null
    },
    {
      "name": null,
      "address": null,
      "signature": null
    }
  ]
}
```

Classification:

```text
name       → USER_INPUT
address    → USER_INPUT
signature  → MANUAL
```

---

# 24. Section Q — Bank Use Only

The following fields are not part of the user conversation.

| Form Field                     | Internal Name                    | Status    |
| ------------------------------ | -------------------------------- | --------- |
| Account holder confirmation    | `bank_account_holder`            | BANK_ONLY |
| Account opening date           | `bank_account_opening_date`      | BANK_ONLY |
| Initial deposit                | `bank_initial_deposit`           | BANK_ONLY |
| Account number                 | `bank_account_number`            | BANK_ONLY |
| Customer Identification Number | `customer_identification_number` | BANK_ONLY |
| Nomination registration number | `nomination_registration_number` | BANK_ONLY |
| Nomination registration date   | `nomination_registration_date`   | BANK_ONLY |
| Bank signature/seal            | `bank_authorization`             | BANK_ONLY |

SwarSahay must never ask the user for these fields.

---

# 25. Complete Field Inventory

## Required User Information

```text
depositor_name
depositor_dob

guardian_name
guardian_relationship
guardian_parent_spouse_name
guardian_dob
guardian_aadhaar
guardian_pan

present_address
permanent_address

mobile_number

initial_subscription
payment_mode
payment_date

birth_certificate_number
birth_certificate_issue_date
birth_certificate_issuing_authority

identification_proof
address_proof

account_operation
```

---

# 26. Optional Information

```text
telephone_number
email
nominee.aadhaar
```

Optional fields should not block form completion unless required by the specific current application process.

---

# 27. Conditional Information

```text
payment_reference
instrument_date

nominee.date_of_birth

minor_nominee_appointee.*

```

Conditional fields are activated only when their corresponding condition is satisfied.

---

# 28. Derived Information

```text
depositor_dob_words
guardian_dob_words
initial_subscription_words
account_type
application_date
```

---

# 29. Manual Information

```text
applicant_photo

specimen_signature_1
specimen_signature_2
specimen_signature_3

guardian_signature
guardian_thumb_impression

witness_signature_1
witness_signature_2
```

---

# 30. Bank-Only Information

```text
bank_account_holder
bank_account_opening_date
bank_initial_deposit
bank_account_number
customer_identification_number
nomination_registration_number
nomination_registration_date
bank_authorization
```

---

# 31. Speech Ambiguities

The following information is particularly challenging when collected through speech.

## Dates

Examples:

```text
15 March 2018
March 15 2018
15/03/2018
15 3 2018
पंद्रह मार्च दो हजार अठारह
```

All unambiguous expressions should normalize to:

```text
YYYY-MM-DD
```

---

## Names

Possible variations:

```text
Ananya Sharma
अनन्या शर्मा
Ananya ji
meri beti Ananya Sharma
```

The system must separate the person's actual name from conversational context.

Transliteration must not silently change official spelling.

---

## Numbers

Users may speak numbers:

```text
123456789012
```

as:

```text
"one two three four..."
```

or:

```text
"ek do teen..."
```

or:

```text
"बारह हजार..."
```

The normalization layer must convert recognized numeric speech into a canonical representation.

---

## Aadhaar

Expected canonical representation:

```text
12 numeric digits
```

Speech should be normalized before validation.

---

## PAN

Expected canonical representation:

```text
5 letters + 4 digits + 1 letter
```

The system should preserve character order.

---

## Amount

Users may say:

```text
"पांच सौ रुपये"
"500 rupees"
"पाँच सौ"
```

These should normalize to a numeric value such as:

```text
500
```

---

# 32. Core Principle

The paper form defines **what information is required**.

The conversational system defines **how that information is collected**.

Therefore, SwarSahay should not simply read the paper form field-by-field.

A user may provide multiple fields in a single utterance.

Example:

```text
"Meri beti Ananya Sharma hai,
15 March 2018 ko paida hui thi,
aur main Rahul Sharma uska father hoon."
```

Possible extraction:

```json
{
  "depositor_name": "Ananya Sharma",
  "depositor_dob": "2018-03-15",
  "guardian_name": "Rahul Sharma",
  "guardian_relationship": "father"
}
```

The system then asks only for information that remains missing.
