# SwarSahay — MVP Scope

## 1. Project Overview

**SwarSahay** is a voice-assisted service access platform designed to help people complete complicated digital or paper-based service processes through natural conversation.

The core problem is:

> People often know what they want to do, but do not know how to navigate the digital process required to do it.

For the first MVP, SwarSahay focuses on one specific use case:

> **Helping a Hindi-speaking user complete a Sukanya Samriddhi Yojana Form-1 through guided voice interaction.**

---

# 2. V1 Scope

## 2.1 Selected Service

**Sukanya Samriddhi Account — Form-1**

The system will assist the user in collecting and organizing the information required for the account-opening application.

The system will generate a structured application draft based on the information provided by the user.

---

## 2.2 Language

### V1 Language

**Hindi**

Hindi is the only supported conversational language in V1.

The system should support naturally spoken Hindi, including common conversational variations and Hindi-English mixed speech where practical.

Examples:

```text
"Meri beti ka naam Ananya Sharma hai."

"Main uska father hoon."

"Uski date of birth 15 March 2018 hai."

"Mera mobile number..."
```

### Future Languages

Telugu, English, and other Indian languages are future extensions.

They are explicitly excluded from V1.

---

# 3. V1 Input

The primary input is:

> **User speech in Hindi**

The user should be able to provide information naturally rather than reading individual form fields.

For example:

```text
"Meri beti Ananya Sharma hai aur uska janam
15 March 2018 ko hua tha."
```

The system should attempt to extract multiple fields from a single response.

---

# 4. V1 Output

The system will provide:

1. Voice-guided questions
2. Structured extracted information
3. Validation feedback
4. Confirmation prompts
5. A completed application draft

The application draft represents the information collected by SwarSahay.

It does **not** represent successful submission to a bank.

---

# 5. Core V1 Pipeline

```text
Hindi Speech
     ↓
Speech-to-Text
     ↓
Natural Language Understanding
     ↓
Information Extraction
     ↓
Form State
     ↓
Validation
     ↓
Missing Field Detection
     ↓
Next Question
     ↓
User Response
     ↓
Update Form State
     ↓
Final Verification
     ↓
Application Draft
```

---

# 6. V1 Functional Requirements

SwarSahay V1 should be able to:

### FR-1 — Understand Hindi Speech

Convert spoken Hindi into text.

### FR-2 — Extract Information

Extract one or more form fields from a natural-language response.

Example:

```text
User:
"Meri beti ka naam Ananya Sharma hai aur uska
janam 15 March 2018 ko hua tha."

Output:

{
  "depositor_name": "Ananya Sharma",
  "depositor_dob": "2018-03-15"
}
```

### FR-3 — Maintain Form State

The system should remember information already provided.

### FR-4 — Detect Missing Information

The system should identify which required fields are still missing.

### FR-5 — Ask the Next Relevant Question

The system should ask only for information that is still required.

### FR-6 — Validate Information

The system should perform basic format and logical validation.

### FR-7 — Handle Corrections

Users should be able to correct previously provided information.

### FR-8 — Confirm Final Information

The system should summarize the collected information and ask for confirmation.

### FR-9 — Generate Application Draft

The system should generate a structured representation of the completed application.

---

# 7. Explicitly OUT OF SCOPE

The following are intentionally NOT part of V1.

## 7.1 Multi-Scheme Support

NOT building:

```text
Sukanya + Jan Dhan + PM-KISAN + other schemes
```

V1 supports only:

> Sukanya Samriddhi Form-1

---

## 7.2 Real Bank Submission

SwarSahay will NOT:

* Submit the application to SBI
* Open a real account
* Communicate with bank systems
* Receive an actual account number
* Perform real bank-side processing

The output is an application draft.

---

## 7.3 Bank API Integration

No bank APIs will be integrated in V1.

---

## 7.4 Aadhaar Authentication

The system may perform basic format validation of an Aadhaar number.

It will NOT:

* Authenticate Aadhaar
* Verify identity
* Query UIDAI
* Perform biometric authentication

---

## 7.5 PAN Verification

The system may perform basic format validation.

It will NOT verify the PAN against external systems.

---

## 7.6 OTP Verification

OTP generation and verification are outside V1.

---

## 7.7 Payment Processing

The system may collect the payment mode and relevant application information.

It will NOT:

* Process payments
* Connect to banking payment systems
* Verify cheque/DD clearance
* Process cash

---

## 7.8 Multi-Language Support

Only Hindi is supported in V1.

Telugu and other languages will be considered after the Hindi pipeline is stable.

---

## 7.9 OCR / Document Understanding

V1 will NOT automatically read:

* Aadhaar cards
* PAN cards
* Birth certificates
* Passports
* Other KYC documents

Document upload/OCR is future work.

---

## 7.10 Digital Signature

SwarSahay will not generate, imitate, or digitally reproduce signatures.

Signature and thumb-impression fields will remain manual.

---

## 7.11 Facial Recognition

Not part of V1.

---

## 7.12 Live Server Deployment

V1 is a local development/demo application.

The project will NOT initially be deployed as a production cloud service.

Live server deployment is future work.

---

## 7.13 Production-Grade Security Infrastructure

V1 is a research/prototype implementation.

It will not attempt to implement a complete production banking security architecture.

Sensitive information should nevertheless be handled carefully and should not be unnecessarily logged.

---

# 8. V1 Success Criteria

The MVP should be evaluated using a fixed test set rather than only demonstrating a few successful conversations.

## 8.1 Field Extraction Accuracy

Target:

> **≥ 90% field-level extraction accuracy on a clean Hindi speech/text test set.**

The test set should contain natural variations such as:

```text
"15 March 2018"

"15 March, 2018"

"15/03/2018"

"March 15 2018"

"पंद्रह मार्च दो हजार अठारह"
```

The exact evaluation methodology will be defined during the testing phase.

---

## 8.2 Date Normalization Accuracy

Target:

> **≥ 95% correct normalization of unambiguous dates in the test set.**

Examples:

```text
15 March 2018
↓
2018-03-15
```

```text
15/03/2018
↓
2018-03-15
```

Ambiguous dates should trigger clarification rather than guessing.

---

## 8.3 Required Field Completion

For a clean test scenario:

> **≥ 95% of required supported fields should be successfully collected or explicitly marked as requiring manual completion.**

---

## 8.4 Conversation Efficiency

Target:

> **Complete a standard test application in ≤ 20 conversational turns for a user who provides one or more fields per response.**

The system should not ask separately for every field when the user has already provided the information.

---

## 8.5 Correction Handling

Target:

> The system should correctly update previously provided information when the user explicitly corrects it.

Example:

```text
User:
"Ananya Sharma."

Later:

"Nahi, naam Arya Sharma hai."

Final value:
Arya Sharma
```

---

## 8.6 Final Verification

The system should not finalize the application until:

1. Required information has been collected
2. Validation has passed
3. User has confirmed the final information

---

# 9. V1 Definition of Done

V1 is considered complete when:

* [ ] Hindi speech can be processed
* [ ] Natural-language responses can be mapped to form fields
* [ ] Form state is maintained
* [ ] Missing fields are detected
* [ ] Required-first questioning works
* [ ] Basic validation works
* [ ] Date normalization works
* [ ] Corrections work
* [ ] Final verification works
* [ ] Application draft is generated
* [ ] Fixed test set is evaluated
* [ ] Results are documented
* [ ] Project can be demonstrated locally

---

# 10. Future Scope

After V1 is stable, possible future extensions include:

```text
V2
→ Telugu support

V3
→ Multiple government schemes

V4
→ Document OCR

V5
→ External verification integrations

V6
→ Real service/bank integration

V7
→ Production deployment
```

These are future possibilities and are not commitments for the MVP.

---

# 11. Scope Lock Statement

For the V1 development cycle, the following combination is frozen:

> **One service: Sukanya Samriddhi Form-1**

> **One conversational language: Hindi**

> **One primary interaction method: Voice**

> **One core outcome: Validated application draft**

Any feature outside this definition should be treated as future scope rather than added to V1.
