"""
Pydantic schemas for the RAG pipeline.

Task 3.2 — RAG Pipeline: request/response contracts.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────


class DiabetesType(str, Enum):
    TYPE_1 = "type_1"
    TYPE_2 = "type_2"
    GESTATIONAL = "gestational"


class GlucoseLevel(str, Enum):
    """Clinical classification of blood glucose."""

    SEVERE_HYPO = "severe_hypoglycemia"   # < 54 mg/dL
    HYPO = "hypoglycemia"                 # 54–69 mg/dL
    NORMAL = "normal"                     # 70–130 mg/dL (fasting) / 70–180 pp
    HIGH = "high"                         # 181–250 mg/dL
    VERY_HIGH = "very_high"               # 251–300 mg/dL
    CRITICAL_HIGH = "critical_high"       # > 300 mg/dL


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── Patient Context ───────────────────────────────────────────────


class PatientContext(BaseModel):
    """Patient-specific clinical context for personalization."""

    current_glucose_mg_dl: float | None = Field(
        default=None, description="Current blood glucose in mg/dL"
    )
    diabetes_type: DiabetesType = Field(
        default=DiabetesType.TYPE_2, description="Type of diabetes"
    )
    medications: list[str] = Field(
        default_factory=list, description="Current medications"
    )
    insulin_to_carb_ratio: float | None = Field(
        default=None,
        description="Insulin-to-Carbohydrate Ratio (1 Unit per X grams)",
    )
    correction_factor: float | None = Field(
        default=None,
        description="Correction Factor / Insulin Sensitivity Factor (mg/dL per 1 Unit)",
    )
    target_glucose_mg_dl: float = Field(
        default=120.0, description="Target blood glucose in mg/dL"
    )


# ── Request ────────────────────────────────────────────────────────


class AdviceRequest(BaseModel):
    """Input for the RAG advisory endpoint."""

    meal_description: str = Field(
        ..., min_length=1, description="Name or description of the meal"
    )
    glycemic_load: float | None = Field(
        default=None, ge=0, description="Estimated GL from Vision pipeline"
    )
    carbs_g: float | None = Field(
        default=None, ge=0, description="Estimated carbohydrate grams"
    )
    patient_context: PatientContext = Field(
        default_factory=PatientContext,
        description="Patient clinical context for personalization",
    )


# ── Insulin Recommendation ────────────────────────────────────────


class InsulinRecommendation(BaseModel):
    """Calculated insulin dose recommendation."""

    meal_dose_units: float = Field(
        default=0.0, ge=0, description="Meal bolus insulin dose"
    )
    correction_dose_units: float = Field(
        default=0.0, ge=0, description="Correction dose for hyperglycemia"
    )
    total_units: float = Field(
        default=0.0, ge=0, description="Total recommended insulin"
    )
    calculation_details: str = Field(
        default="", description="How the dose was calculated"
    )


# ── Source Citation ────────────────────────────────────────────────


class SourceCitation(BaseModel):
    """A source chunk cited in the RAG response."""

    chunk_id: str
    source: str
    category: str
    relevance_score: float = Field(ge=0, le=1)


# ── Emergency Alert ────────────────────────────────────────────────


class EmergencyAlert(BaseModel):
    """Alert for dangerous glucose levels."""

    alert_type: str = Field(..., description="hypoglycemia | hyperglycemia | dka_risk")
    severity: str = Field(..., description="mild | moderate | severe | critical")
    immediate_action: str = Field(..., description="What to do NOW")
    follow_up: str = Field(default="", description="Next steps after immediate action")


# ── Response ───────────────────────────────────────────────────────

DISCLAIMER = (
    "This is educational information only and NOT medical advice. "
    "Always consult your healthcare provider before adjusting insulin or medication."
)


class AdviceResponse(BaseModel):
    """Output of the RAG advisory endpoint."""

    advice: str = Field(..., description="RAG-generated clinical advice text")
    insulin_recommendation: InsulinRecommendation | None = Field(
        default=None, description="Calculated insulin dose"
    )
    emergency_alert: EmergencyAlert | None = Field(
        default=None, description="Emergency alert if glucose is dangerous"
    )
    glucose_classification: GlucoseLevel | None = Field(
        default=None, description="Clinical glucose classification"
    )
    sources: list[SourceCitation] = Field(
        default_factory=list, description="Medical sources cited"
    )
    confidence: Confidence = Field(
        default=Confidence.MEDIUM, description="Response confidence"
    )
    disclaimer: str = Field(default=DISCLAIMER)

    # ── Debug / Developer Mode ─────────────────────────────────────
    debug_retrieved_chunks: list[dict] | None = Field(
        default=None,
        description="Retrieved KB chunks [{source, category, score, content_preview}]",
    )
    debug_prompt_preview: str | None = Field(
        default=None,
        description="Truncated user prompt sent to LLM (first 500 chars)",
    )
    debug_llm_raw: str | None = Field(
        default=None,
        description="Raw LLM response text before JSON parsing",
    )
