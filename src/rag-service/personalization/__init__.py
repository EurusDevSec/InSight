"""
InSight Personalization Module — Task 3.3

Components:
    - emergency: Emergency detection & clinical protocols
    - clinical_rules: Rule-based insulin dose engine
    - grounding: Strict RAG grounding & anti-hallucination
"""

from personalization.clinical_rules import ClinicalRules
from personalization.emergency import EmergencyDetector
from personalization.grounding import GroundingValidator

__all__ = [
    "ClinicalRules",
    "EmergencyDetector",
    "GroundingValidator",
]
