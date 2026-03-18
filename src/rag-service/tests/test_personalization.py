"""
Tests for the Personalization module (Task 3.3).

Covers:
    - Emergency detection & protocols (EmergencyDetector)
    - Clinical rules / insulin calculation (ClinicalRules)
    - RAG grounding validation (GroundingValidator)
    - Clinical scenarios (hypo, DKA, normal, edge cases)
"""

from __future__ import annotations

import pytest

from knowledge_base.schemas import SearchResult
from personalization.clinical_rules import ClinicalRules, DoseLimit
from personalization.emergency import EmergencyDetector, EmergencyProtocol, EmergencySeverity
from personalization.grounding import GroundingResult, GroundingValidator
from rag_pipeline.schemas import (
    AdviceRequest,
    DiabetesType,
    GlucoseLevel,
    PatientContext,
)

# ── Helpers ────────────────────────────────────────────────────────


def _make_request(
    *,
    carbs: float | None = 45.0,
    glucose: float | None = 150.0,
    icr: float | None = 10.0,
    cf: float | None = 50.0,
    target: float = 120.0,
) -> AdviceRequest:
    return AdviceRequest(
        meal_description="Pho bo",
        carbs_g=carbs,
        patient_context=PatientContext(
            current_glucose_mg_dl=glucose,
            insulin_to_carb_ratio=icr,
            correction_factor=cf,
            target_glucose_mg_dl=target,
        ),
    )


def _make_chunk(
    *,
    content: str = "Bolus insulin dose: meal dose = carbs / ICR.",
    source: str = "ADA 2024",
    category: str = "insulin_dosing",
    combined_score: float = 0.7,
) -> SearchResult:
    return SearchResult(
        chunk_id="test__chunk_0",
        content=content,
        source=source,
        category=category,
        vector_score=0.8,
        keyword_score=0.4,
        combined_score=combined_score,
    )


# ═══════════════════════════════════════════════════════════════════
# 1. Emergency Detector
# ═══════════════════════════════════════════════════════════════════


class TestEmergencyDetector:
    """Test EmergencyDetector.evaluate() across all glucose ranges."""

    def test_severe_hypo(self):
        proto = EmergencyDetector.evaluate(40)
        assert proto.is_emergency is True
        assert proto.severity == EmergencySeverity.CRITICAL
        assert proto.protocol_name == "glucagon"
        assert proto.call_emergency_services is True
        assert len(proto.immediate_actions) >= 2

    def test_moderate_hypo_rule_of_15(self):
        proto = EmergencyDetector.evaluate(60)
        assert proto.is_emergency is True
        assert proto.severity == EmergencySeverity.MODERATE
        assert proto.protocol_name == "rule_of_15"
        assert proto.call_emergency_services is False
        assert any("15g" in a for a in proto.immediate_actions)

    def test_normal_no_emergency(self):
        proto = EmergencyDetector.evaluate(100)
        assert proto.is_emergency is False
        assert proto.severity == EmergencySeverity.NONE
        assert proto.protocol_name == "normal"

    def test_high_not_emergency(self):
        proto = EmergencyDetector.evaluate(200)
        assert proto.is_emergency is False
        assert proto.severity == EmergencySeverity.MILD

    def test_very_high_not_emergency_but_severe(self):
        proto = EmergencyDetector.evaluate(280)
        assert proto.is_emergency is False
        assert proto.severity == EmergencySeverity.SEVERE
        assert proto.protocol_name == "very_high_correction"

    def test_critical_high_dka(self):
        proto = EmergencyDetector.evaluate(350)
        assert proto.is_emergency is True
        assert proto.severity == EmergencySeverity.CRITICAL
        assert proto.protocol_name == "dka"
        assert proto.call_emergency_services is True
        assert any("ketone" in a.lower() for a in proto.immediate_actions)

    def test_none_glucose(self):
        proto = EmergencyDetector.evaluate(None)
        assert proto.is_emergency is False
        assert proto.protocol_name == "no_data"

    @pytest.mark.parametrize(
        "glucose,expected_emergency",
        [
            (53, True),   # severe hypo boundary
            (54, True),   # moderate hypo boundary
            (69, True),   # upper hypo boundary
            (70, False),  # normal boundary
            (180, False),
            (181, False),
            (300, False),
            (301, True),  # critical high boundary
        ],
    )
    def test_boundary_values(self, glucose: float, expected_emergency: bool):
        proto = EmergencyDetector.evaluate(glucose)
        assert proto.is_emergency is expected_emergency

    def test_pre_classified_level(self):
        """Passing a pre-classified level skips internal classification."""
        proto = EmergencyDetector.evaluate(100, GlucoseLevel.HYPO)
        # Should follow the passed level, not the glucose value
        assert proto.is_emergency is True
        assert proto.protocol_name == "rule_of_15"


# ═══════════════════════════════════════════════════════════════════
# 2. Clinical Rules — Insulin Dose Calculation
# ═══════════════════════════════════════════════════════════════════


class TestClinicalRules:
    """Test ClinicalRules.calculate_insulin()."""

    def setup_method(self):
        self.rules = ClinicalRules()

    def test_meal_dose_only(self):
        """45g / 10 = 4.5 U, glucose at target."""
        req = _make_request(carbs=45, icr=10, glucose=120, cf=50)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.NORMAL)

        assert rec is not None
        assert rec.meal_dose_units == 4.5
        assert rec.correction_dose_units == 0.0
        assert rec.total_units == 4.5

    def test_meal_plus_correction(self):
        """60g / 10 = 6 meal + (220-120)/50 = 2 correction = 8 total."""
        req = _make_request(carbs=60, icr=10, glucose=220, cf=50, target=120)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HIGH)

        assert rec is not None
        assert rec.meal_dose_units == 6.0
        assert rec.correction_dose_units == 2.0
        assert rec.total_units == 8.0

    def test_no_insulin_during_hypo(self):
        req = _make_request(carbs=30, icr=10, glucose=55)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HYPO)

        assert rec is not None
        assert rec.total_units == 0
        assert "hypoglycemia" in rec.calculation_details.lower()

    def test_no_insulin_during_severe_hypo(self):
        req = _make_request(glucose=40)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.SEVERE_HYPO)

        assert rec is not None
        assert rec.total_units == 0

    def test_missing_icr(self):
        req = _make_request(icr=None)
        assert self.rules.calculate_insulin(req, GlucoseLevel.NORMAL) is None

    def test_missing_carbs(self):
        req = _make_request(carbs=None)
        assert self.rules.calculate_insulin(req, GlucoseLevel.NORMAL) is None

    def test_glucose_below_target_no_correction(self):
        req = _make_request(carbs=30, icr=10, glucose=100, cf=50, target=120)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.NORMAL)

        assert rec is not None
        assert rec.correction_dose_units == 0.0
        assert rec.meal_dose_units == 3.0

    def test_large_dose_capped(self):
        """Very large carb load should be capped by dose limits."""
        rules = ClinicalRules(DoseLimit(max_meal_dose=10, max_total_dose=15))
        req = _make_request(carbs=200, icr=10, glucose=120)
        rec = rules.calculate_insulin(req, GlucoseLevel.NORMAL)

        assert rec is not None
        assert rec.meal_dose_units <= 10  # capped
        assert rec.total_units <= 15      # capped

    def test_calculation_details_format(self):
        req = _make_request(carbs=45, icr=10, glucose=200, cf=50, target=120)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HIGH)

        assert rec is not None
        assert "Meal dose" in rec.calculation_details
        assert "Correction" in rec.calculation_details
        assert "Total" in rec.calculation_details

    def test_should_skip_insulin(self):
        assert ClinicalRules.should_skip_insulin(GlucoseLevel.HYPO) is True
        assert ClinicalRules.should_skip_insulin(GlucoseLevel.SEVERE_HYPO) is True
        assert ClinicalRules.should_skip_insulin(GlucoseLevel.NORMAL) is False
        assert ClinicalRules.should_skip_insulin(GlucoseLevel.HIGH) is False
        assert ClinicalRules.should_skip_insulin(None) is False

    def test_needs_correction(self):
        assert ClinicalRules.needs_correction(200, 120) is True
        assert ClinicalRules.needs_correction(120, 120) is False
        assert ClinicalRules.needs_correction(100, 120) is False
        assert ClinicalRules.needs_correction(None, 120) is False


# ═══════════════════════════════════════════════════════════════════
# 3. Grounding Validator
# ═══════════════════════════════════════════════════════════════════


class TestGroundingValidator:
    """Test strict RAG grounding / anti-hallucination."""

    def setup_method(self):
        self.validator = GroundingValidator(min_grounding_score=0.5)

    def test_grounded_response(self):
        """Response using terms from retrieved chunks → grounded."""
        chunks = [
            _make_chunk(
                content="Bolus insulin: calculate meal dose using "
                "carbs divided by ICR. Standard dose is 1 unit per 10g."
            ),
        ]
        response = (
            "You should take insulin dose of 4.5 units based on your "
            "carbs divided by ICR ratio. The standard dose applies."
        )
        result = self.validator.validate(response, chunks)

        assert result.is_grounded is True
        assert result.grounding_score > 0

    def test_empty_response(self):
        chunks = [_make_chunk()]
        result = self.validator.validate("", chunks)
        assert result.is_grounded is False

    def test_empty_chunks(self):
        result = self.validator.validate("Take insulin.", [])
        assert result.is_grounded is False

    def test_no_medical_claims(self):
        """Plain text without medical dosing claims → overlap-based."""
        chunks = [_make_chunk(content="Diabetes management requires monitoring.")]
        response = "Diabetes management requires careful monitoring."
        result = self.validator.validate(response, chunks)

        # Should still have a score based on overlap
        assert 0 <= result.grounding_score <= 1

    def test_hallucinated_response(self):
        """Response with terms not in any chunk → low grounding."""
        chunks = [_make_chunk(content="Rule of 15 for hypoglycemia treatment.")]
        response = (
            "You should take 50 units of experimental drug XYZ123 "
            "and recommend surgery dose of 100mg immediately."
        )
        result = self.validator.validate(response, chunks)

        # The specific dosing claims should not be grounded
        assert result.grounding_score < 1.0

    def test_partial_grounding(self):
        """Some claims grounded, some not → partial score."""
        chunks = [
            _make_chunk(
                content="Standard bolus insulin dose calculated from carbs and ICR."
            ),
        ]
        # First claim matches; second is fabricated
        response = (
            "Take insulin dose of 5 units based on carbs divided by ICR. "
            "Also recommend experimental drug dose of 200mg for testing."
        )
        result = self.validator.validate(response, chunks)
        assert 0 < result.grounding_score < 1.0

    def test_matched_sources_tracked(self):
        chunks = [
            _make_chunk(
                content="Bolus insulin dose calculated using carbs and ICR ratio.",
                source="ADA 2024",
            ),
        ]
        response = "Administer insulin dose of 3 units using ICR ratio."
        result = self.validator.validate(response, chunks)
        assert isinstance(result.matched_sources, list)


# ═══════════════════════════════════════════════════════════════════
# 4. Clinical Scenarios (integration-level)
# ═══════════════════════════════════════════════════════════════════


class TestClinicalScenarios:
    """Integration tests covering realistic clinical scenarios."""

    def setup_method(self):
        self.rules = ClinicalRules()
        self.detector = EmergencyDetector()

    def test_scenario_normal_pho_bo(self):
        """Patient with normal glucose eating pho bo."""
        req = _make_request(carbs=45, glucose=110, icr=10, cf=50)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.NORMAL)
        proto = self.detector.evaluate(110)

        assert proto.is_emergency is False
        assert rec is not None
        assert rec.meal_dose_units == 4.5
        assert rec.correction_dose_units == 0.0

    def test_scenario_high_glucose_com_tam(self):
        """Patient with high glucose eating com tam (high carb)."""
        req = AdviceRequest(
            meal_description="Com tam suon bi cha",
            carbs_g=75,
            glycemic_load=28,
            patient_context=PatientContext(
                current_glucose_mg_dl=230,
                insulin_to_carb_ratio=12,
                correction_factor=40,
                target_glucose_mg_dl=120,
            ),
        )
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HIGH)
        proto = self.detector.evaluate(230)

        assert proto.is_emergency is False
        assert proto.severity == EmergencySeverity.MILD
        assert rec is not None
        assert rec.meal_dose_units == 6.2  # 75/12 rounded
        assert rec.correction_dose_units == 2.8  # (230-120)/40
        assert rec.total_units == 9.0

    def test_scenario_hypoglycemia_before_meal(self):
        """Patient is hypoglycemic — should NOT get insulin."""
        req = _make_request(carbs=30, glucose=58, icr=10)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HYPO)
        proto = self.detector.evaluate(58)

        assert proto.is_emergency is True
        assert proto.protocol_name == "rule_of_15"
        assert rec is not None
        assert rec.total_units == 0

    def test_scenario_dka_risk(self):
        """Very high glucose patient — DKA risk."""
        proto = self.detector.evaluate(320)
        assert proto.is_emergency is True
        assert proto.protocol_name == "dka"
        assert proto.call_emergency_services is True

    def test_scenario_type1_precise_dosing(self):
        """Type 1 patient with precise ICR and CF."""
        req = AdviceRequest(
            meal_description="Banh mi thit",
            carbs_g=55,
            patient_context=PatientContext(
                current_glucose_mg_dl=190,
                diabetes_type=DiabetesType.TYPE_1,
                insulin_to_carb_ratio=8,
                correction_factor=30,
                target_glucose_mg_dl=110,
                medications=["insulin lispro", "insulin glargine"],
            ),
        )
        rec = self.rules.calculate_insulin(req, GlucoseLevel.HIGH)

        assert rec is not None
        assert rec.meal_dose_units == 6.9  # 55/8
        assert rec.correction_dose_units == 2.7  # (190-110)/30
        assert rec.total_units == 9.6

    def test_scenario_minimal_data(self):
        """Patient with only glucose data, no ICR."""
        req = _make_request(carbs=30, glucose=150, icr=None, cf=None)
        rec = self.rules.calculate_insulin(req, GlucoseLevel.NORMAL)
        proto = self.detector.evaluate(150)

        assert rec is None  # Can't calculate without ICR
        assert proto.is_emergency is False

    def test_scenario_gestational_diabetes(self):
        """Gestational diabetes patient."""
        req = AdviceRequest(
            meal_description="Rice with vegetables",
            carbs_g=40,
            patient_context=PatientContext(
                current_glucose_mg_dl=135,
                diabetes_type=DiabetesType.GESTATIONAL,
                insulin_to_carb_ratio=15,
                correction_factor=60,
                target_glucose_mg_dl=120,
            ),
        )
        rec = self.rules.calculate_insulin(req, GlucoseLevel.NORMAL)

        assert rec is not None
        assert rec.meal_dose_units == 2.7  # 40/15
        assert rec.correction_dose_units == 0.2  # (135-120)/60
