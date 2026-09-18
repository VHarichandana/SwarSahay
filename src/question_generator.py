from normalizer import is_ambiguous_date_missing_year

NON_CONVERSATIONAL_FIELDS = {
    "applicant_photograph",
    "guardian_signature",
    "specimen_signatures",
    "account_type",
    "date_of_birth_words",
    "guardian_dob_words",
    "initial_deposit_words",
    "bank_account_holder",
    "bank_account_opening_date",
    "bank_initial_deposit",
    "bank_account_number",
    "customer_identification_number",
    "nomination_registration_number",
    "nomination_registration_date",
    "bank_signature_and_seal"
}

SENSITIVE_CONFIRMATION_FIELDS = {
    "account_holder_name",
    "guardian_full_name",
    "guardian_parent_spouse_name",
    "date_of_birth",
    "guardian_dob",
    "instrument_date",
    "guardian_aadhaar",
    "guardian_pan",
    "mobile_number"
}


def is_sensitive_field(field_id: str) -> bool:
    return field_id in SENSITIVE_CONFIRMATION_FIELDS


def generate_question(field_id: str) -> str:
    if field_id in NON_CONVERSATIONAL_FIELDS:
        return None

    questions = {
        # Section A: Application Details
        "bank_name": "Aap kis bank mein account kholna chahte hain?",
        "branch_name": "Bank ki branch ka naam kya hai?",
        "initial_deposit_amount": "Aap shuruaat mein kitni rashi jama karna chahte hain?",
        "deposit_mode": "Aap deposit cash, cheque ya demand draft se karenge?",
        "instrument_date": "Cheque ya Demand Draft ki date (taareekh) kya hai?",

        # Section B: Depositor Details
        "account_holder_name": "Bachchi ka poora naam kya hai?",
        "date_of_birth": "Bachchi ki janam tithi kya hai?",

        # Section C & D: Guardian Details & KYC
        "guardian_full_name": "Guardian ka poora naam kya hai?",
        "guardian_relationship": "Aapka bachchi se kya rishta hai (jaise father, mother)?",
        "guardian_parent_spouse_name": "Guardian ke pita ya pati ka naam kya hai?",
        "guardian_dob": "Guardian ki janam tithi kya hai?",
        "guardian_aadhaar": "Guardian ka 12 digit ka Aadhaar number kya hai?",
        "guardian_pan": "Guardian ka PAN number kya hai?",

        # Section E & F: Address and Contact
        "present_address": "Aapka vartamaan pata (present address) kya hai?",
        "permanent_same_as_present": "Kya aapka permanent address bhi yahi hai?",
        "permanent_address": "Aapka sthayi pata (permanent address) kya hai?",
        "telephone_number": "Aapka landline telephone number kya hai?",
        "mobile_number": "Aapka 10 digit ka mobile number kya hai?",
        "email": "Aapka email ID kya hai?",

        # Section H & I: Birth Certificate & KYC Documents
        "birth_cert_number": "Bachchi ke birth certificate ka number kya hai?",
        "birth_cert_issue_date": "Birth certificate jari hone ki taareekh (issue date) kya hai?",
        "birth_cert_issuing_authority": "Birth certificate jari karne wali authority ka naam kya hai?",
        "identification_proof_type": "Pehchan praman (ID proof) ke liye kaun sa document de rahe hain (passport, driving_license, voter_id, nrega_job_card, npr_letter)?",
        "address_proof_type": "Address proof ke liye kaun sa document de rahe hain (passport, driving_license, voter_id, nrega_job_card, npr_letter)?",

        # Section J: Account Operation
        "account_operation": "Account operation kis prakaar hoga: guardian until majority ya depositor after majority?",

        # Section L: Declarations
        "existing_account_declaration": "Kya aap pushti karte hain ki bachchi ke naam par pehle se koi Sukanya Samriddhi khata nahi hai?",
        "residency_citizenship_declaration": "Kya guardian aur bachchi dono Bharat ke niwasi nagrik hain?",
        "terms_acceptance": "Kya aap Sukanya Samriddhi Yojana ke sabhi niyamon aur sharton ko sweekar karte hain?",

        # Section N & O: Nomination & Minor Nominee Appointee
        "nomination_present": "Kya aap nomination ki jaankari darj karna chahte hain?",
        "appointee_name": "Minor nominee ke appointee ka naam kya hai?",
        "appointee_parent_spouse_name": "Appointee ke pita ya pati ka naam kya hai?",
        "appointee_address": "Appointee ka pata kya hai?"
    }

    return questions.get(
        field_id,
        f"Kripya {field_id.replace('_', ' ')} batayein."
    )


def generate_reask_question(field_id: str, raw_value: str = None) -> str:
    if field_id == "mobile_number":
        return "Kripya 10 digit ka sahi mobile number batayein (jaise 9876543210)."

    if field_id in ["date_of_birth", "guardian_dob", "birth_cert_issue_date", "instrument_date"]:
        if raw_value and is_ambiguous_date_missing_year(raw_value):
            return "Kripya janam ka saal bhi batayein. Saal ke bina taareekh darj nahi ki ja sakti."
        return f"Kripya {field_id.replace('_', ' ')} sahi format (YYYY-MM-DD ya 15 March 2018) mein batayein. Saal batana zaroori hai."

    if field_id == "guardian_aadhaar":
        return "Kripya 12 digit ka sahi Aadhaar number batayein."

    if field_id == "guardian_pan":
        return "Kripya 10 akshar ka sahi PAN number batayein (jaise ABCDE1234F)."

    if field_id == "initial_deposit_amount":
        return "Kripya sahi rashi batayein (kam se kam 250 aur zyada se zyada 1,50,000 rupaye)."

    if field_id == "deposit_mode":
        return "Kripya sahi payment mode batayein: cash, cheque, ya dd."

    if field_id == "guardian_relationship":
        return "Kripya maanya rishta batayein (mother, father, husband ya legal_guardian)."

    if field_id in ["identification_proof_type", "address_proof_type"]:
        return "Kripya maanya document chunein: passport, driving_license, voter_id, nrega_job_card, ya npr_letter."

    if field_id == "account_operation":
        return "Kripya chunein: guardian until majority ya depositor after majority."

    if field_id in ["permanent_same_as_present", "existing_account_declaration", "residency_citizenship_declaration", "terms_acceptance"]:
        return "Kripya spasht roop se haan ya nahi mein batayein."

    if field_id == "email":
        return "Kripya sahi email ID batayein (jaise name@example.com)."

    return f"Kripya {field_id.replace('_', ' ')} ka sahi format batayein."


def generate_confirmation_prompt(field_id: str, value) -> str:
    if field_id == "account_holder_name":
        return f"Maine bachchi ka naam '{value}' darj kiya hai. Kya yeh sahi hai?"

    if field_id == "guardian_full_name":
        return f"Maine guardian ka naam '{value}' darj kiya hai. Kya yeh sahi hai?"

    if field_id == "guardian_parent_spouse_name":
        return f"Maine guardian ke pita/pati ka naam '{value}' darj kiya hai. Kya yeh sahi hai?"

    if field_id in ["date_of_birth", "guardian_dob", "birth_cert_issue_date", "instrument_date"]:
        return f"Maine {field_id.replace('_', ' ')} {value} darj ki hai. Kya yeh sahi hai?"

    if field_id == "guardian_aadhaar":
        val_str = str(value)
        if len(val_str) == 12:
            formatted = f"{val_str[:4]} {val_str[4:8]} {val_str[8:]}"
        else:
            formatted = val_str
        return f"Maine Aadhaar number {formatted} darj kiya hai. Kya yeh sahi hai?"

    if field_id == "guardian_pan":
        return f"Maine PAN number {value} darj kiya hai. Kya yeh sahi hai?"

    if field_id == "mobile_number":
        return f"Maine mobile number {value} darj kiya hai. Kya yeh sahi hai?"

    return f"Maine {field_id.replace('_', ' ')}: '{value}' darj kiya hai. Kya yeh sahi hai?"


if __name__ == "__main__":
    field_id = "bank_name"
    question = generate_question(field_id)
    print("Question:", question)

    reask = generate_reask_question("mobile_number", "1234")
    print("Re-ask:", reask)

    confirm = generate_confirmation_prompt("guardian_aadhaar", "123456789012")
    print("Confirmation:", confirm)