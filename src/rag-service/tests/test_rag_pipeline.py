"""
Tests for the RAG Pipeline (Task 3.2).

Covers:
    - Prompt construction (PromptBuilder)
    - Glucose classification & emergency detection
    - LLM client (mocked)
    - Insulin dose calculation (rule-based)
    - Full RAG service orchestration (mocked search + mocked LLM)
    - Edge cases (missing data, extreme glucose)
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from knowledge_base.schemas import SearchResult
from rag_pipeline.llm_client import LLMClient
from rag_pipeline.prompt_builder import EMERGENCY_SYSTEM_PROMPT, SYSTEM_PROMPT, PromptBuilder
from rag_pipeline.rag_service import RAGService
from rag_pipeline.schemas import (
    AdviceRequest,
    AdviceResponse,
    Confidence,
    DiabetesType,
    GlucoseLevel,
    InsulinRecommendation,
    PatientContext,
)

# ── Fixtures ───────────────────────────────────────────────────────


def _make_search_result(
    *,
    chunk_id: str = "test__chunk_0",
    content: str = "Bolus insulin: meal dose = carbs / ICR.",
    source: str = "ADA 2024",
    category: str = "insulin_dosing",
    vector_score: float = 0.8,
    keyword_score: float = 0.5,
    combined_score: float = 0.71,
) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        content=content,
        source=source,
        category=category,
        vector_score=vector_score,
        keyword_score=keyword_score,
        combined_score=combined_score,
    )


def _make_request(
    *,
    meal: str = "Pho bo",
    carbs: float | None = 45.0,
    gl: float | None = 16.0,
    glucose: float | None = 150.0,
    icr: float | None = 10.0,
    cf: float | None = 50.0,
    target: float = 120.0,
    dtype: DiabetesType = DiabetesType.TYPE_2,
    meds: list[str] | None = None,
) -> AdviceRequest:
    return AdviceRequest(
        meal_description=meal,
        glycemic_load=gl,
        carbs_g=carbs,
        patient_context=PatientContext(
            current_glucose_mg_dl=glucose,
            diabetes_type=dtype,
            medications=meds or ["metformin 500mg"],
            insulin_to_carb_ratio=icr,
            correction_factor=cf,
            target_glucose_mg_dl=target,
        ),
    )


def _mock_search_response(results: list[SearchResult] | None = None):
    """Return a mock SearchService whose search() returns given results."""
    from knowledge_base.schemas import SearchResponse

    svc = MagicMock()
    results = results or [_make_search_result()]
    svc.search.return_value = SearchResponse(
        query="test",
        results=results,
        total_found=len(results),
    )
    return svc


def _mock_llm(advice_text: str = "Take insulin with meal.") -> LLMClient:
    """Return a mocked LLMClient that returns a canned JSON dict."""
    llm = MagicMock(spec=LLMClient)
    llm.generate_json.return_value = {"advice": advice_text}
    return llm


# ═══════════════════════════════════════════════════════════════════
# 1. Glucose Classification
# ═══════════════════════════════════════════════════════════════════


class TestGlucoseClassification:
    """Test PromptBuilder.classify_glucose() across all clinical ranges."""

    @pytest.mark.parametrize(
        "glucose,expected",
        [
            (30, GlucoseLevel.SEVERE_HYPO),
            (53, GlucoseLevel.SEVERE_HYPO),
            (54, GlucoseLevel.HYPO),
            (69, GlucoseLevel.HYPO),
            (70, GlucoseLevel.NORMAL),
            (120, GlucoseLevel.NORMAL),
            (180, GlucoseLevel.NORMAL),
            (181, GlucoseLevel.HIGH),
            (250, GlucoseLevel.HIGH),
            (251, GlucoseLevel.VERY_HIGH),
            (300, GlucoseLevel.VERY_HIGH),
            (301, GlucoseLevel.CRITICAL_HIGH),
            (500, GlucoseLevel.CRITICAL_HIGH),
        ],
    )
    def test_classification(self, glucose: float, expected: GlucoseLevel):
        assert PromptBuilder.classify_glucose(glucose) == expected

    def test_none_returns_none(self):
        assert PromptBuilder.classify_glucose(None) is None


class TestEmergencyDetection:
    """Test PromptBuilder.is_emergency()."""

    @pytest.mark.parametrize(
        "level,expected",
        [
            (GlucoseLevel.SEVERE_HYPO, True),
            (GlucoseLevel.HYPO, True),
            (GlucoseLevel.NORMAL, False),
            (GlucoseLevel.HIGH, False),
            (GlucoseLevel.VERY_HIGH, False),
            (GlucoseLevel.CRITICAL_HIGH, True),
            (None, False),
        ],
    )
    def test_emergency_flag(self, level, expected):
        assert PromptBuilder.is_emergency(level) == expected


# ═══════════════════════════════════════════════════════════════════
# 2. Prompt Builder
# ═══════════════════════════════════════════════════════════════════


class TestPromptBuilder:
    """Test prompt construction logic."""

    def test_system_prompt_normal(self):
        assert PromptBuilder.build_system_prompt(GlucoseLevel.NORMAL) == SYSTEM_PROMPT

    def test_system_prompt_emergency_hypo(self):
        prompt = PromptBuilder.build_system_prompt(GlucoseLevel.HYPO)
        assert prompt == EMERGENCY_SYSTEM_PROMPT

    def test_system_prompt_emergency_critical(self):
        prompt = PromptBuilder.build_system_prompt(GlucoseLevel.CRITICAL_HIGH)
        assert prompt == EMERGENCY_SYSTEM_PROMPT

    def test_user_prompt_contains_patient_context(self):
        req = _make_request(glucose=150, meal="Com tam")
        results = [_make_search_result()]
        prompt = PromptBuilder.build_user_prompt(req, results, GlucoseLevel.NORMAL)

        assert "150" in prompt  # glucose
        assert "type_2" in prompt  # diabetes type
        assert "metformin" in prompt  # medication
        assert "Com tam" in prompt  # meal
        assert "PATIENT CONTEXT" in prompt
        assert "MEAL INFORMATION" in prompt
        assert "MEDICAL GUIDELINES" in prompt

    def test_user_prompt_includes_retrieved_chunks(self):
        results = [
            _make_search_result(content="Rule of 15 for hypoglycemia."),
            _make_search_result(
                chunk_id="ada__chunk_1",
                content="Correction factor formula.",
            ),
        ]
        req = _make_request()
        prompt = PromptBuilder.build_user_prompt(req, results, GlucoseLevel.NORMAL)

        assert "Rule of 15" in prompt
        assert "Correction factor formula" in prompt
        assert "[1]" in prompt
        assert "[2]" in prompt

    def test_user_prompt_emergency_question(self):
        req = _make_request(glucose=40)
        results = [_make_search_result()]
        prompt = PromptBuilder.build_user_prompt(
            req, results, GlucoseLevel.SEVERE_HYPO
        )
        assert "DANGEROUS" in prompt

    def test_user_prompt_no_results(self):
        req = _make_request()
        prompt = PromptBuilder.build_user_prompt(req, [], GlucoseLevel.NORMAL)
        assert "No matching guidelines found" in prompt

    def test_user_prompt_with_icr_and_cf(self):
        req = _make_request(icr=12, cf=40)
        prompt = PromptBuilder.build_user_prompt(
            req, [_make_search_result()], GlucoseLevel.NORMAL
        )
        assert "12" in prompt  # ICR
        assert "40" in prompt  # CF

    def test_user_prompt_with_glycemic_load(self):
        req = _make_request(gl=22.5)
        prompt = PromptBuilder.build_user_prompt(
            req, [_make_search_result()], GlucoseLevel.NORMAL
        )
        assert "22.5" in prompt


# ═══════════════════════════════════════════════════════════════════
# 3. LLM Client (unit tests with mocking)
# ═══════════════════════════════════════════════════════════════════


class TestLLMClient:
    """Test LLMClient with mocked OpenAI."""

    def test_generate_json_valid(self):
        llm = _mock_llm("Bolus dose 3U.")
        result = llm.generate_json("sys", "user")
        assert "advice" in result

    def test_connect_requires_openai(self):
        """Verify connect() imports openai."""
        client = LLMClient()
        # Without openai installed, this would raise RuntimeError
        # We test it doesn't crash with the package present
        try:
            client.connect()
        except RuntimeError as e:
            assert "openai" in str(e).lower()
        except Exception:
            # Connection error is fine — we just want the import to work
            pass

    def test_generate_without_connect_raises(self):
        client = LLMClient()
        with pytest.raises(RuntimeError, match="not connected"):
            client.generate("sys", "user")


# ═══════════════════════════════════════════════════════════════════
# 4. Insulin Dose Calculation (rule-based)
# ═══════════════════════════════════════════════════════════════════


class TestInsulinCalculation:
    """Test RAGService._compute_insulin() rule-based calculations."""

    def test_normal_meal_dose(self):
        """45g carbs / ICR 10 = 4.5 U."""
        req = _make_request(carbs=45, icr=10, glucose=120, cf=50)
        result = RAGService._compute_insulin(req, GlucoseLevel.NORMAL)

        assert result is not None
        assert result.meal_dose_units == 4.5
        assert result.correction_dose_units == 0.0
        assert result.total_units == 4.5

    def test_meal_plus_correction(self):
        """45g / 10 = 4.5 meal + (200-120)/50 = 1.6 correction = 6.1 total."""
        req = _make_request(carbs=45, icr=10, glucose=200, cf=50, target=120)
        result = RAGService._compute_insulin(req, GlucoseLevel.HIGH)

        assert result is not None
        assert result.meal_dose_units == 4.5
        assert result.correction_dose_units == 1.6
        assert result.total_units == 6.1

    def test_hypo_returns_zero_dose(self):
        """No insulin during hypoglycemia."""
        req = _make_request(glucose=55, carbs=30, icr=10)
        result = RAGService._compute_insulin(req, GlucoseLevel.HYPO)

        assert result is not None
        assert result.total_units == 0
        assert "treat hypoglycemia first" in result.calculation_details.lower()

    def test_severe_hypo_returns_zero_dose(self):
        req = _make_request(glucose=40, carbs=30, icr=10)
        result = RAGService._compute_insulin(req, GlucoseLevel.SEVERE_HYPO)

        assert result is not None
        assert result.total_units == 0

    def test_missing_icr_returns_none(self):
        req = _make_request(icr=None, carbs=30)
        result = RAGService._compute_insulin(req, GlucoseLevel.NORMAL)
        assert result is None

    def test_missing_carbs_returns_none(self):
        req = _make_request(carbs=None, icr=10)
        result = RAGService._compute_insulin(req, GlucoseLevel.NORMAL)
        assert result is None

    def test_no_correction_when_at_target(self):
        """Glucose == target → no correction."""
        req = _make_request(carbs=30, icr=10, glucose=120, cf=50, target=120)
        result = RAGService._compute_insulin(req, GlucoseLevel.NORMAL)

        assert result is not None
        assert result.correction_dose_units == 0.0

    def test_no_correction_when_below_target(self):
        """Glucose < target → no correction dose."""
        req = _make_request(carbs=30, icr=10, glucose=100, cf=50, target=120)
        result = RAGService._compute_insulin(req, GlucoseLevel.NORMAL)

        assert result is not None
        assert result.correction_dose_units == 0.0

    def test_calculation_details_present(self):
        req = _make_request(carbs=60, icr=15, glucose=250, cf=50, target=120)
        result = RAGService._compute_insulin(req, GlucoseLevel.HIGH)

        assert result is not None
        assert "60.0g" in result.calculation_details
        assert "15" in result.calculation_details
        assert "250" in result.calculation_details


# ═══════════════════════════════════════════════════════════════════
# 5. Emergency Alert Building
# ═══════════════════════════════════════════════════════════════════


class TestEmergencyAlert:
    """Test RAGService._build_emergency_alert()."""

    def test_severe_hypo_alert(self):
        alert = RAGService._build_emergency_alert(GlucoseLevel.SEVERE_HYPO, 40)
        assert alert is not None
        assert alert.alert_type == "hypoglycemia"
        assert alert.severity == "severe"
        assert "glucagon" in alert.immediate_action.lower()

    def test_moderate_hypo_alert(self):
        alert = RAGService._build_emergency_alert(GlucoseLevel.HYPO, 60)
        assert alert is not None
        assert alert.alert_type == "hypoglycemia"
        assert alert.severity == "moderate"
        assert "rule of 15" in alert.immediate_action.lower()

    def test_critical_high_alert(self):
        alert = RAGService._build_emergency_alert(GlucoseLevel.CRITICAL_HIGH, 350)
        assert alert is not None
        assert alert.alert_type == "dka_risk"
        assert alert.severity == "critical"
        assert "ketone" in alert.immediate_action.lower()

    def test_normal_returns_none(self):
        assert RAGService._build_emergency_alert(GlucoseLevel.NORMAL, 100) is None

    def test_high_returns_none(self):
        assert RAGService._build_emergency_alert(GlucoseLevel.HIGH, 200) is None


# ═══════════════════════════════════════════════════════════════════
# 6. Confidence Assessment
# ═══════════════════════════════════════════════════════════════════


class TestConfidenceAssessment:
    """Test RAGService._assess_confidence()."""

    def test_high_confidence(self):
        results = [_make_search_result(combined_score=0.7)]
        req = _make_request(carbs=30, glucose=150, icr=10)
        assert RAGService._assess_confidence(results, req) == Confidence.HIGH

    def test_medium_confidence(self):
        results = [_make_search_result(combined_score=0.4)]
        req = _make_request(carbs=30, glucose=None, icr=None)
        assert RAGService._assess_confidence(results, req) == Confidence.MEDIUM

    def test_low_confidence_no_results(self):
        req = _make_request()
        assert RAGService._assess_confidence([], req) == Confidence.LOW

    def test_low_confidence_low_score(self):
        results = [_make_search_result(combined_score=0.1)]
        req = _make_request(carbs=None, glucose=None, icr=None)
        assert RAGService._assess_confidence(results, req) == Confidence.LOW


# ═══════════════════════════════════════════════════════════════════
# 7. Full RAG Orchestration (mocked search + mocked LLM)
# ═══════════════════════════════════════════════════════════════════


class TestRAGServiceOrchestration:
    """End-to-end RAG pipeline with mocked external services."""

    def _build_rag_service(
        self,
        results: list[SearchResult] | None = None,
        llm_advice: str = "Take 4.5 units of bolus insulin with your meal.",
    ) -> RAGService:
        return RAGService(
            search_service=_mock_search_response(results),
            llm_client=_mock_llm(llm_advice),
            top_k=5,
        )

    def test_normal_flow(self):
        """Normal glucose, full data → complete AdviceResponse."""
        svc = self._build_rag_service()
        req = _make_request(glucose=150, carbs=45, icr=10, cf=50)
        resp = svc.advise(req)

        assert isinstance(resp, AdviceResponse)
        assert resp.advice
        assert resp.glucose_classification == GlucoseLevel.NORMAL
        assert resp.insulin_recommendation is not None
        assert resp.insulin_recommendation.meal_dose_units == 4.5
        assert resp.emergency_alert is None
        assert len(resp.sources) >= 1
        assert resp.confidence == Confidence.HIGH

    def test_emergency_hypo_flow(self):
        """Glucose 55 → emergency alert, no insulin."""
        svc = self._build_rag_service(
            llm_advice="Apply Rule of 15: take 15g fast-acting glucose."
        )
        req = _make_request(glucose=55, carbs=30, icr=10)
        resp = svc.advise(req)

        assert resp.glucose_classification == GlucoseLevel.HYPO
        assert resp.emergency_alert is not None
        assert resp.emergency_alert.severity == "moderate"
        assert resp.insulin_recommendation is not None
        assert resp.insulin_recommendation.total_units == 0

    def test_emergency_critical_high_flow(self):
        """Glucose 350 → DKA risk alert."""
        svc = self._build_rag_service(
            llm_advice="Check ketones immediately. DKA risk."
        )
        req = _make_request(glucose=350, carbs=None, icr=None)
        resp = svc.advise(req)

        assert resp.glucose_classification == GlucoseLevel.CRITICAL_HIGH
        assert resp.emergency_alert is not None
        assert resp.emergency_alert.alert_type == "dka_risk"

    def test_high_glucose_correction(self):
        """Glucose 220 → meal dose + correction dose."""
        svc = self._build_rag_service()
        req = _make_request(glucose=220, carbs=60, icr=10, cf=50, target=120)
        resp = svc.advise(req)

        assert resp.glucose_classification == GlucoseLevel.HIGH
        assert resp.insulin_recommendation is not None
        assert resp.insulin_recommendation.meal_dose_units == 6.0  # 60/10
        assert resp.insulin_recommendation.correction_dose_units == 2.0  # (220-120)/50
        assert resp.insulin_recommendation.total_units == 8.0

    def test_no_patient_context(self):
        """Request with minimal data still works."""
        svc = self._build_rag_service()
        req = AdviceRequest(
            meal_description="Rice",
            carbs_g=50,
            patient_context=PatientContext(),
        )
        resp = svc.advise(req)

        assert resp.advice
        assert resp.glucose_classification is None  # no glucose
        assert resp.insulin_recommendation is None  # no ICR

    def test_sources_populated(self):
        """Sources list reflects retrieved chunks."""
        results = [
            _make_search_result(chunk_id="a", source="ADA 2024"),
            _make_search_result(chunk_id="b", source="MOH Vietnam"),
        ]
        svc = self._build_rag_service(results=results)
        req = _make_request()
        resp = svc.advise(req)

        assert len(resp.sources) == 2
        sources = {s.source for s in resp.sources}
        assert "ADA 2024" in sources
        assert "MOH Vietnam" in sources

    def test_disclaimer_always_present(self):
        svc = self._build_rag_service()
        req = _make_request()
        resp = svc.advise(req)
        assert "NOT medical advice" in resp.disclaimer

    def test_llm_called_with_correct_prompts(self):
        """Verify LLM receives system + user prompts."""
        llm = _mock_llm()
        svc = RAGService(
            search_service=_mock_search_response(),
            llm_client=llm,
            top_k=5,
        )
        req = _make_request(glucose=110)
        svc.advise(req)

        llm.generate_json.assert_called_once()
        call_args = llm.generate_json.call_args
        system_prompt = call_args[0][0]
        user_prompt = call_args[0][1]
        assert "InSight" in system_prompt
        assert "Pho bo" in user_prompt


# ═══════════════════════════════════════════════════════════════════
# 8. Schema Validation
# ═══════════════════════════════════════════════════════════════════


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_advice_request_requires_meal(self):
        with pytest.raises(Exception):
            AdviceRequest(meal_description="")

    def test_advice_request_defaults(self):
        req = AdviceRequest(meal_description="Test")
        assert req.carbs_g is None
        assert req.glycemic_load is None
        assert req.patient_context is not None

    def test_patient_context_defaults(self):
        ctx = PatientContext()
        assert ctx.diabetes_type == DiabetesType.TYPE_2
        assert ctx.target_glucose_mg_dl == 120.0
        assert ctx.medications == []

    def test_advice_response_serialization(self):
        resp = AdviceResponse(
            advice="Test advice",
            glucose_classification=GlucoseLevel.NORMAL,
            confidence=Confidence.HIGH,
        )
        data = resp.model_dump()
        assert data["advice"] == "Test advice"
        assert data["glucose_classification"] == "normal"
        assert data["confidence"] == "high"
        assert "disclaimer" in data


# ═══════════════════════════════════════════════════════════════════
# 7. LLM Client — JSON Extraction & Markdown Cleaning (Task 4.4)
# ═══════════════════════════════════════════════════════════════════


class TestLLMClientExtractJson:
    """Test LLMClient._extract_json() static method."""

    def test_plain_json(self):
        text = '{"advice": "Take 4U insulin"}'
        assert LLMClient._extract_json(text) == '{"advice": "Take 4U insulin"}'

    def test_markdown_code_fence(self):
        text = '```json\n{"advice": "hello"}\n```'
        assert '"advice"' in LLMClient._extract_json(text)

    def test_code_fence_no_language(self):
        text = '```\n{"advice": "world"}\n```'
        result = LLMClient._extract_json(text)
        assert '"advice"' in result

    def test_json_embedded_in_text(self):
        text = 'Here is my response:\n{"advice": "eat less"}\nHope that helps!'
        result = LLMClient._extract_json(text)
        assert result == '{"advice": "eat less"}'

    def test_no_json_returns_original(self):
        text = "No JSON here, just text"
        assert LLMClient._extract_json(text) == text


class TestLLMClientCleanMarkdown:
    """Test LLMClient._clean_markdown() static method."""

    def test_bold_stripped(self):
        assert LLMClient._clean_markdown("**Bold text**") == "Bold text"

    def test_italic_stripped(self):
        assert LLMClient._clean_markdown("*italic text*") == "italic text"

    def test_code_fence_stripped(self):
        assert "```" not in LLMClient._clean_markdown("```json\ncode\n```")

    def test_excessive_newlines_collapsed(self):
        result = LLMClient._clean_markdown("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_mixed_markdown(self):
        text = "**Bold** and *italic* with ```code```"
        result = LLMClient._clean_markdown(text)
        assert "**" not in result
        assert "*" not in result or result.count("*") == 0
        assert "```" not in result
