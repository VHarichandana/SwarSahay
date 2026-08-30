# SwarSahay — Feasibility Notes

## 1. Purpose

This document records observations about the practical feasibility of SwarSahay.

It will capture findings from:

* User research
* Speech recognition testing
* Hindi language testing
* Form-completion experiments
* Usability testing
* Technical limitations
* Privacy considerations
* Conversation failures

The purpose is to ensure that the final project is based not only on technical implementation but also on observed user needs and system limitations.

---

# 2. Current Hypothesis

The initial hypothesis is:

> Users who struggle with traditional digital forms may be able to provide the required information more easily through natural Hindi conversation.

The MVP will test whether a voice-first interaction can reliably convert natural speech into structured application information.

---

# 3. User Research

Status:

```text
NOT STARTED
```

Questions to investigate:

1. Do users understand the purpose of the service?
2. Do users prefer speaking over typing?
3. Which form fields are difficult to understand?
4. Which questions are difficult to answer verbally?
5. Do users naturally provide multiple pieces of information in one response?
6. Which Hindi words or phrases create confusion?
7. Are users comfortable speaking sensitive information aloud?
8. Do users trust an AI-assisted form-filling system?
9. What type of confirmation do users expect before finalizing the form?

---

# 4. Speech Feasibility

Status:

```text
TO BE TESTED
```

Test:

* Clean Hindi speech
* Different speaking speeds
* Hindi-English mixed speech
* Number pronunciation
* Date pronunciation
* Names
* Addresses
* Aadhaar digits
* PAN characters

---

# 5. Information Extraction Feasibility

Status:

```text
TO BE TESTED
```

Evaluate whether the system can reliably extract:

```text
Names
Dates
Numbers
Addresses
Relationships
Document types
Payment information
Nominee information
Declarations
```

---

# 6. Date Normalization

Status:

```text
TO BE TESTED
```

Test examples:

```text
15 March 2018
March 15 2018
15/03/2018
15-03-2018
पंद्रह मार्च दो हजार अठारह
15 March
March 2018
```

The system should clarify incomplete or ambiguous dates instead of guessing.

---

# 7. Privacy Considerations

The application may involve sensitive personal information such as:

* Aadhaar
* PAN
* Mobile number
* Address
* Date of birth

The prototype should therefore:

* Avoid unnecessary logging of raw sensitive information
* Avoid exposing sensitive information in debugging output
* Avoid storing real user data in the GitHub repository
* Use synthetic/test data during development
* Clearly distinguish prototype behavior from real KYC verification

---

# 8. Known Technical Risks

Potential risks include:

```text
Hindi ASR errors
↓
Incorrect names

Speech number recognition errors
↓
Incorrect Aadhaar/PAN/mobile numbers

Date ambiguity
↓
Incorrect DOB

Address complexity
↓
Incomplete extraction

Code-switching
↓
Hindi + English recognition errors

Long conversations
↓
Incorrect form state

LLM hallucination
↓
Invented information
```

These risks will be tested during later development phases.

---

# 9. Mitigation Strategy

The system should prefer:

```text
Extract
   ↓
Validate
   ↓
Confirm
```

rather than:

```text
Extract
   ↓
Assume correct
```

Important personal information should not be silently invented or guessed.

---

# 10. User Testing Results

This section will be populated after testing.

| Test | User Type | Task          | Result | Problems | Notes |
| ---- | --------- | ------------- | ------ | -------- | ----- |
| T001 | TBD       | Complete form | TBD    | TBD      | TBD   |
| T002 | TBD       | Provide dates | TBD    | TBD      | TBD   |
| T003 | TBD       | Provide names | TBD    | TBD      | TBD   |

---

# 11. Feasibility Conclusion

Status:

```text
PENDING
```

The final conclusion will be based on:

* Field extraction accuracy
* Date normalization accuracy
* Conversation completion rate
* Number of clarification turns
* User feedback
* Error rate
* Privacy/usability observations
