from __future__ import annotations
from dataclasses import dataclass


class ThreatLevel:
    """Auto-generated from Ape enum 'ThreatLevel'."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class Email:
    """Auto-generated from Ape entity 'Email'."""
    from_domain: str
    subject: str
    body: str

@dataclass
class EmailAssessment:
    """Auto-generated from Ape entity 'EmailAssessment'."""
    email: "Email"
    level: "ThreatLevel"
    reason: str

def assess_email(email: "Email") -> "EmailAssessment":
    """Auto-generated from Ape task 'assess_email'.

    Constraints:
        - deterministic

    Steps:
        - check if from_domain is in trusted safelist
        - if domain is trusted return LOW threat level
        - check subject for suspicious keywords
        - if suspicious keywords found return HIGH threat level with reason
        - check body length and structure
        - if body is empty then return MEDIUM threat level
        - if body is malformed then return MEDIUM threat level
        - otherwise return LOW threat level
    """
    raise NotImplementedError

POLICY_email_threat_policy = {
    "name": "email_threat_policy",
    "scope": "global",
    "rules": [
        "Emails from trusted domains are always assessed as LOW",
        "Emails with HIGH assessment must be quarantined immediately",
        "Emails with MEDIUM assessment require manual review within 24 hours",
        "All email assessments must be logged with timestamp and assessor",
        "Safelist must be reviewed quarterly",
    ],
    "enforcement": {},  # TODO: add enforcement metadata
}
