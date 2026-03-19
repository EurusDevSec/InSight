"""
Main RAG orchestration service.

Task 3.2.2 — Query → Retrieve chunks → Augment prompt → Generate response.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from knowledge_base.schemas import SearchQuery, SearchResult
from knowledge_base.search import SearchService
from rag_pipeline.llm_client import LLMClient
from rag_pipeline.prompt_builder import PromptBuilder
from rag_pipeline.schemas import (
    AdviceRequest,
    AdviceResponse,
    Confidence,
    EmergencyAlert,
    GlucoseLevel,
    InsulinRecommendation,
    SourceCitation,
)

logger = logging.getLogger(__name__)

# Categories to boost for different glucose situations
_EMERGENCY_CATEGORIES = ("emergency_protocol",)
_INSULIN_CATEGORIES = ("insulin_dosing", "carb_counting")


@dataclass
class RAGService:
    """Orchestrates the full Retrieval-Augmented Generation pipeline."""

    search_service: SearchService
    llm_client: LLMClient
    top_k: int = 5

    # ── Public API ─────────────────────────────────────────────────

    def advise(self, request: AdviceRequest, *, debug: bool = False) -> AdviceResponse:
        """End-to-end RAG advisory: retrieve → augment → generate.

        Args:
            request: Meal + patient context.
            debug: If True, include retrieved chunks, prompt preview, raw LLM output.

        Returns:
            Structured advisory response.
        """
        glucose = request.patient_context.current_glucose_mg_dl
        glucose_level = PromptBuilder.classify_glucose(glucose)
        is_emergency = PromptBuilder.is_emergency(glucose_level)

        # 1. Retrieve relevant medical chunks
        search_results = self._retrieve(request, glucose_level)

        # 2. Build prompts
        system_prompt = PromptBuilder.build_system_prompt(glucose_level)
        user_prompt = PromptBuilder.build_user_prompt(
            request, search_results, glucose_level
        )

        # 3. Generate LLM response (capture raw for debug)
        raw_llm_text = self.llm_client.generate(system_prompt, user_prompt) if debug else None
        if raw_llm_text is not None:
            cleaned = LLMClient._extract_json(raw_llm_text)
            import json as _json
            try:
                llm_output = _json.loads(cleaned)
            except _json.JSONDecodeError:
                llm_output = {"advice": LLMClient._clean_markdown(raw_llm_text)}
        else:
            llm_output = self.llm_client.generate_json(system_prompt, user_prompt)

        # 4. Compute insulin recommendation (rule-based, not from LLM)
        insulin_rec = self._compute_insulin(request, glucose_level)

        # 5. Build emergency alert if needed
        emergency_alert = (
            self._build_emergency_alert(glucose_level, glucose)
            if is_emergency
            else None
        )

        # 6. Build source citations
        sources = [
            SourceCitation(
                chunk_id=r.chunk_id,
                source=r.source,
                category=r.category,
                relevance_score=round(r.combined_score, 3),
            )
            for r in search_results
        ]

        # 7. Determine confidence
        confidence = self._assess_confidence(search_results, request)

        advice_text = llm_output.get("advice", "")
        # Clean any residual markdown formatting from the LLM output
        advice_text = LLMClient._clean_markdown(advice_text)
        if emergency_alert:
            # Prepend emergency prefix if LLM didn't
            if not advice_text.upper().startswith(("WARNING", "EMERGENCY", "⚠")):
                advice_text = (
                    f"⚠️ {emergency_alert.alert_type.upper()} ALERT: "
                    + advice_text
                )

        # 8. Debug data
        debug_chunks = None
        debug_prompt = None
        debug_raw = None
        if debug:
            debug_chunks = [
                {
                    "source": r.source,
                    "category": r.category,
                    "score": round(r.combined_score, 3),
                    "content_preview": r.content[:200],
                }
                for r in search_results
            ]
            debug_prompt = user_prompt[:500]
            debug_raw = raw_llm_text

        return AdviceResponse(
            advice=advice_text,
            insulin_recommendation=insulin_rec,
            emergency_alert=emergency_alert,
            glucose_classification=glucose_level,
            sources=sources,
            confidence=confidence,
            debug_retrieved_chunks=debug_chunks,
            debug_prompt_preview=debug_prompt,
            debug_llm_raw=debug_raw,
        )

    # ── Retrieval ──────────────────────────────────────────────────

    def _retrieve(
        self,
        request: AdviceRequest,
        glucose_level: GlucoseLevel | None,
    ) -> list[SearchResult]:
        """Retrieve relevant chunks from the knowledge base."""
        queries: list[SearchQuery] = []

        # Emergency: prioritise emergency protocol chunks
        if PromptBuilder.is_emergency(glucose_level):
            queries.append(
                SearchQuery(
                    query="hypoglycemia emergency treatment protocol glucose low",
                    top_k=self.top_k,
                    category_filter="emergency_protocol",
                )
            )

        # Always retrieve for the meal + insulin context
        meal_query = request.meal_description
        if request.carbs_g is not None:
            meal_query += f" {request.carbs_g:.0f}g carbohydrate"
        meal_query += " insulin dose"

        queries.append(SearchQuery(query=meal_query, top_k=self.top_k))

        # Deduplicate results by chunk_id
        seen: set[str] = set()
        results: list[SearchResult] = []
        for q in queries:
            resp = self.search_service.search(q)
            for r in resp.results:
                if r.chunk_id not in seen:
                    seen.add(r.chunk_id)
                    results.append(r)

        # Sort by combined_score descending
        results.sort(key=lambda r: r.combined_score, reverse=True)
        return results[: self.top_k]

    # ── Insulin Calculation (rule-based) ───────────────────────────

    @staticmethod
    def _compute_insulin(
        request: AdviceRequest,
        glucose_level: GlucoseLevel | None,
    ) -> InsulinRecommendation | None:
        """Rule-based insulin dose calculation.

        Formula:
            meal_dose = carbs_g / ICR
            correction_dose = max(0, (glucose - target) / CF)
            total = meal_dose + correction_dose

        Returns None if insufficient data or if glucose is dangerously low.
        """
        ctx = request.patient_context

        # No insulin during hypoglycemia
        if glucose_level in (GlucoseLevel.SEVERE_HYPO, GlucoseLevel.HYPO):
            return InsulinRecommendation(
                meal_dose_units=0,
                correction_dose_units=0,
                total_units=0,
                calculation_details=(
                    "No insulin recommended — treat hypoglycemia first. "
                    "Apply Rule of 15: 15g fast-acting glucose, recheck in 15 min."
                ),
            )

        # Need ICR and carbs for meal dose
        if ctx.insulin_to_carb_ratio is None or request.carbs_g is None:
            return None

        meal_dose = round(request.carbs_g / ctx.insulin_to_carb_ratio, 1)
        details = (
            f"Meal dose: {request.carbs_g:.1f}g / {ctx.insulin_to_carb_ratio}g/U "
            f"= {meal_dose} U"
        )

        correction_dose = 0.0
        if (
            ctx.correction_factor is not None
            and ctx.current_glucose_mg_dl is not None
            and ctx.current_glucose_mg_dl > ctx.target_glucose_mg_dl
        ):
            correction_dose = round(
                (ctx.current_glucose_mg_dl - ctx.target_glucose_mg_dl)
                / ctx.correction_factor,
                1,
            )
            details += (
                f"\nCorrection: ({ctx.current_glucose_mg_dl:.0f} - "
                f"{ctx.target_glucose_mg_dl:.0f}) / {ctx.correction_factor} "
                f"= {correction_dose} U"
            )

        total = round(meal_dose + correction_dose, 1)
        details += f"\nTotal: {meal_dose} + {correction_dose} = {total} U"

        return InsulinRecommendation(
            meal_dose_units=meal_dose,
            correction_dose_units=correction_dose,
            total_units=total,
            calculation_details=details,
        )

    # ── Emergency Alert ────────────────────────────────────────────

    @staticmethod
    def _build_emergency_alert(
        glucose_level: GlucoseLevel | None,
        glucose_mg_dl: float | None,
    ) -> EmergencyAlert | None:
        """Create an emergency alert based on glucose classification."""
        if glucose_level == GlucoseLevel.SEVERE_HYPO:
            return EmergencyAlert(
                alert_type="hypoglycemia",
                severity="severe",
                immediate_action=(
                    "SEVERE HYPOGLYCEMIA (<54 mg/dL). "
                    "If conscious: give 15-20g fast-acting glucose (juice, glucose tabs). "
                    "If unconscious: administer glucagon, call emergency services."
                ),
                follow_up=(
                    "Recheck glucose in 15 minutes. "
                    "If still <70 mg/dL, repeat treatment. "
                    "Seek medical attention."
                ),
            )
        if glucose_level == GlucoseLevel.HYPO:
            return EmergencyAlert(
                alert_type="hypoglycemia",
                severity="moderate",
                immediate_action=(
                    "HYPOGLYCEMIA (54-69 mg/dL). "
                    "Apply Rule of 15: consume 15g fast-acting carbohydrate "
                    "(4 glucose tablets, 1/2 cup juice, or 1 tbsp honey)."
                ),
                follow_up=(
                    "Wait 15 minutes and recheck blood glucose. "
                    "If still <70 mg/dL, repeat. "
                    "Once normalized, eat a snack with protein."
                ),
            )
        if glucose_level == GlucoseLevel.CRITICAL_HIGH:
            return EmergencyAlert(
                alert_type="dka_risk",
                severity="critical",
                immediate_action=(
                    "CRITICALLY HIGH glucose (>300 mg/dL) — DKA risk. "
                    "Check urine or blood ketones immediately. "
                    "If ketones positive: seek emergency medical care."
                ),
                follow_up=(
                    "Administer correction insulin per your provider's protocol. "
                    "Hydrate with water. "
                    "Contact your diabetes care team."
                ),
            )
        return None

    # ── Confidence Assessment ──────────────────────────────────────

    @staticmethod
    def _assess_confidence(
        search_results: list[SearchResult],
        request: AdviceRequest,
    ) -> Confidence:
        """Assess confidence based on retrieval quality and data completeness."""
        if not search_results:
            return Confidence.LOW

        top_score = search_results[0].combined_score if search_results else 0
        has_carbs = request.carbs_g is not None
        has_glucose = request.patient_context.current_glucose_mg_dl is not None
        has_icr = request.patient_context.insulin_to_carb_ratio is not None

        if top_score >= 0.5 and has_carbs and has_glucose and has_icr:
            return Confidence.HIGH
        if top_score >= 0.3 and (has_carbs or has_glucose):
            return Confidence.MEDIUM
        return Confidence.LOW
