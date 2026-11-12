from __future__ import annotations

APPLICATION_COLUMNS = [
    "application_id", "applicant_id", "application_timestamp", "full_name", "date_of_birth",
    "email", "phone", "address", "device_id", "ip_address", "employment_status",
    "annual_income", "requested_credit", "application_channel",
]
LABEL_COLUMNS = ["fraud_label", "fraud_scenario"]
EMPLOYMENT = ["employed", "self_employed", "unemployed", "student", "retired"]
CHANNELS = ["web", "mobile", "branch", "partner"]
SCENARIOS = [
    "legitimate", "synthetic_identity", "device_ring", "shared_contact",
    "velocity_burst", "identity_inconsistency", "income_anomaly",
]

DATA_DICTIONARY = {
    "application_id": "Unique application id",
    "applicant_id": "Applicant identifier (a fraudster may hold several)",
    "application_timestamp": "UTC timestamp of submission",
    "full_name": "Synthetic applicant name",
    "date_of_birth": "Synthetic date of birth",
    "email": "Synthetic email",
    "phone": "Synthetic phone",
    "address": "Synthetic address",
    "device_id": "Synthetic device fingerprint",
    "ip_address": "Synthetic IPv4",
    "employment_status": f"One of {EMPLOYMENT}",
    "annual_income": "Declared annual income (USD)",
    "requested_credit": "Requested credit amount (USD)",
    "application_channel": f"One of {CHANNELS}",
    "fraud_label": "TRAINING ONLY. 1 = simulated fraud. Never sent in online scoring.",
    "fraud_scenario": f"TRAINING ONLY. One of {SCENARIOS}",
}
