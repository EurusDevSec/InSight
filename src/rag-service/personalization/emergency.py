"""
Emergency detection and clinical protocols.

Task 3.3 — Detects dangerous glucose levels and returns
structured emergency protocols (Rule of 15, DKA, glucagon).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rag_pipeline.schemas import GlucoseLevel


class EmergencySeverity(str, Enum):
    """Severity classification for emergency situations."""

    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass(frozen=True)
class EmergencyProtocol:
    """A structured emergency response protocol."""

    is_emergency: bool
    severity: EmergencySeverity
    glucose_level: GlucoseLevel | None
    protocol_name: str  # e.g. "rule_of_15", "glucagon", "dka"
    immediate_actions: list[str]
    follow_up_actions: list[str]
    call_emergency_services: bool


class EmergencyDetector:
    """Detects emergency glucose conditions and returns clinical protocols."""

    @staticmethod
    def evaluate(
        glucose_mg_dl: float | None,
        glucose_level: GlucoseLevel | None = None,
    ) -> EmergencyProtocol:
        """Evaluate glucose reading and return the appropriate protocol.

        Args:
            glucose_mg_dl: Blood glucose in mg/dL.
            glucose_level: Pre-classified level (optional; calculated if None).

        Returns:
            EmergencyProtocol with actions.
        """
        if glucose_mg_dl is None:
            return EmergencyProtocol(
                is_emergency=False,
                severity=EmergencySeverity.NONE,
                glucose_level=None,
                protocol_name="no_data",
                immediate_actions=[],
                follow_up_actions=["Check blood glucose before meals."],
                call_emergency_services=False,
            )

        if glucose_level is None:
            glucose_level = _classify(glucose_mg_dl)

        if glucose_level == GlucoseLevel.SEVERE_HYPO:
            return _severe_hypo_protocol(glucose_level)
        if glucose_level == GlucoseLevel.HYPO:
            return _moderate_hypo_protocol(glucose_level)
        if glucose_level == GlucoseLevel.CRITICAL_HIGH:
            return _dka_risk_protocol(glucose_level)
        if glucose_level == GlucoseLevel.VERY_HIGH:
            return _very_high_protocol(glucose_level)
        if glucose_level == GlucoseLevel.HIGH:
            return _high_protocol(glucose_level)

        # Normal range
        return EmergencyProtocol(
            is_emergency=False,
            severity=EmergencySeverity.NONE,
            glucose_level=glucose_level,
            protocol_name="normal",
            immediate_actions=[],
            follow_up_actions=["Continue your normal diabetes management routine."],
            call_emergency_services=False,
        )


# ── Internal helpers ───────────────────────────────────────────────

def _classify(glucose: float) -> GlucoseLevel:
    if glucose < 54:
        return GlucoseLevel.SEVERE_HYPO
    if glucose < 70:
        return GlucoseLevel.HYPO
    if glucose <= 180:
        return GlucoseLevel.NORMAL
    if glucose <= 250:
        return GlucoseLevel.HIGH
    if glucose <= 300:
        return GlucoseLevel.VERY_HIGH
    return GlucoseLevel.CRITICAL_HIGH


def _severe_hypo_protocol(gl: GlucoseLevel) -> EmergencyProtocol:
    """< 54 mg/dL — potential loss of consciousness."""
    return EmergencyProtocol(
        is_emergency=True,
        severity=EmergencySeverity.CRITICAL,
        glucose_level=gl,
        protocol_name="glucagon",
        immediate_actions=[
            "If conscious: give 15-20g fast-acting glucose immediately.",
            "If unconscious or unable to swallow: administer glucagon.",
            "Place patient in recovery position if unconscious.",
            "Call emergency services (115 / 911).",
        ],
        follow_up_actions=[
            "Recheck glucose every 15 minutes until > 70 mg/dL.",
            "Once stable, provide a meal with complex carbs and protein.",
            "Contact diabetes care team today.",
            "DO NOT administer insulin.",
        ],
        call_emergency_services=True,
    )


def _moderate_hypo_protocol(gl: GlucoseLevel) -> EmergencyProtocol:
    """54-69 mg/dL — Rule of 15."""
    return EmergencyProtocol(
        is_emergency=True,
        severity=EmergencySeverity.MODERATE,
        glucose_level=gl,
        protocol_name="rule_of_15",
        immediate_actions=[
            "Apply Rule of 15: consume 15g fast-acting carbohydrate.",
            "Choices: 4 glucose tablets, 1/2 cup (120ml) juice, "
            "1 tablespoon honey, or 3-4 hard candies.",
            "Sit down and rest.",
        ],
        follow_up_actions=[
            "Wait 15 minutes, then recheck blood glucose.",
            "If still < 70 mg/dL: repeat 15g carb treatment.",
            "Once > 70 mg/dL: eat a snack with protein (cheese, nuts).",
            "DO NOT take insulin until glucose normalizes.",
        ],
        call_emergency_services=False,
    )


def _dka_risk_protocol(gl: GlucoseLevel) -> EmergencyProtocol:
    """> 300 mg/dL — DKA risk."""
    return EmergencyProtocol(
        is_emergency=True,
        severity=EmergencySeverity.CRITICAL,
        glucose_level=gl,
        protocol_name="dka",
        immediate_actions=[
            "CRITICALLY HIGH glucose — DKA risk.",
            "Check urine or blood ketones immediately.",
            "If ketones are positive: seek emergency medical care.",
            "Drink water to stay hydrated (250ml every 30 min).",
        ],
        follow_up_actions=[
            "Administer correction insulin per your provider's sick-day protocol.",
            "Contact your diabetes care team immediately.",
            "Monitor glucose every 1-2 hours.",
            "Do NOT exercise when glucose > 300 mg/dL.",
        ],
        call_emergency_services=True,
    )


def _very_high_protocol(gl: GlucoseLevel) -> EmergencyProtocol:
    """251-300 mg/dL — monitor closely."""
    return EmergencyProtocol(
        is_emergency=False,
        severity=EmergencySeverity.SEVERE,
        glucose_level=gl,
        protocol_name="very_high_correction",
        immediate_actions=[
            "Glucose 251-300 mg/dL — consider checking ketones.",
            "Apply correction insulin dose per your care plan.",
            "Drink water and avoid sugary foods.",
        ],
        follow_up_actions=[
            "Recheck glucose in 2 hours.",
            "If no improvement, contact your care team.",
            "Review recent food, stress, illness, or missed insulin.",
        ],
        call_emergency_services=False,
    )


def _high_protocol(gl: GlucoseLevel) -> EmergencyProtocol:
    """181-250 mg/dL — correction dose."""
    return EmergencyProtocol(
        is_emergency=False,
        severity=EmergencySeverity.MILD,
        glucose_level=gl,
        protocol_name="high_correction",
        immediate_actions=[
            "Apply correction insulin dose if prescribed.",
            "Choose low-glycemic foods for next meal.",
        ],
        follow_up_actions=[
            "Recheck glucose before next meal.",
            "Review carb intake at previous meal.",
        ],
        call_emergency_services=False,
    )
