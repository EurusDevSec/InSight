"""
Prompt builder for the RAG advisory pipeline.

Task 3.2.2 — Constructs system + user prompts for insulin/meal advice,
injecting retrieved knowledge chunks and patient context.
"""

from __future__ import annotations

from knowledge_base.schemas import SearchResult
from rag_pipeline.schemas import AdviceRequest, GlucoseLevel

# ── System Prompt ──────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are InSight Medical Advisor, a clinical decision-support assistant for \
diabetes management.

STRICT RULES:
1. Base ALL recommendations ONLY on the provided medical guidelines below.
2. Do NOT invent facts. If the guidelines do not cover a question, say so.
3. Always include the disclaimer that this is educational, not medical advice.
4. When recommending insulin doses, show your calculation step-by-step.
5. For emergency situations (hypoglycemia <70 mg/dL, DKA risk >300 mg/dL), \
   lead with the emergency protocol FIRST.
6. Cite sources by name (e.g. "ADA Standards of Care 2024").

RESPONSE FORMAT (JSON):
{
  "advice": "<main advice text with source citations>",
  "calculation": "<step-by-step insulin calculation if applicable>",
  "emergency_note": "<emergency note if glucose is dangerous, else null>",
  "confidence": "high | medium | low"
}
"""

# ── Emergency Prompt Override ──────────────────────────────────────

EMERGENCY_SYSTEM_PROMPT = """\
You are InSight Emergency Advisor. The patient may be in a DANGEROUS \
glucose state. Respond with URGENCY.

STRICT RULES:
1. Lead with the emergency protocol IMMEDIATELY.
2. Use ONLY the emergency guidelines provided below.
3. Be clear, concise, and actionable.
4. Include when to call emergency services.

RESPONSE FORMAT (JSON):
{
  "advice": "<emergency advice with immediate steps>",
  "calculation": null,
  "emergency_note": "<severity and what to do>",
  "confidence": "high"
}
"""


# ── Builder ────────────────────────────────────────────────────────


class PromptBuilder:
    """Constructs prompts for the LLM from retrieved chunks + patient context."""

    @staticmethod
    def classify_glucose(glucose_mg_dl: float | None) -> GlucoseLevel | None:
        """Classify a blood glucose reading into a clinical category."""
        if glucose_mg_dl is None:
            return None
        if glucose_mg_dl < 54:
            return GlucoseLevel.SEVERE_HYPO
        if glucose_mg_dl < 70:
            return GlucoseLevel.HYPO
        if glucose_mg_dl <= 180:
            return GlucoseLevel.NORMAL
        if glucose_mg_dl <= 250:
            return GlucoseLevel.HIGH
        if glucose_mg_dl <= 300:
            return GlucoseLevel.VERY_HIGH
        return GlucoseLevel.CRITICAL_HIGH

    @staticmethod
    def is_emergency(glucose_level: GlucoseLevel | None) -> bool:
        """Return True if the glucose level warrants an emergency response."""
        if glucose_level is None:
            return False
        return glucose_level in (
            GlucoseLevel.SEVERE_HYPO,
            GlucoseLevel.HYPO,
            GlucoseLevel.CRITICAL_HIGH,
        )

    @staticmethod
    def build_system_prompt(glucose_level: GlucoseLevel | None) -> str:
        """Select the appropriate system prompt."""
        if PromptBuilder.is_emergency(glucose_level):
            return EMERGENCY_SYSTEM_PROMPT
        return SYSTEM_PROMPT

    @staticmethod
    def build_user_prompt(
        request: AdviceRequest,
        search_results: list[SearchResult],
        glucose_level: GlucoseLevel | None,
    ) -> str:
        """Build the context-augmented user prompt.

        Sections:
        1. Patient context (glucose, meds, diabetes type)
        2. Meal information (name, carbs, GL)
        3. Retrieved medical guidelines (numbered chunks)
        4. Specific question
        """
        lines: list[str] = []

        # --- Section 1: Patient Context ---
        ctx = request.patient_context
        lines.append("=== PATIENT CONTEXT ===")
        if ctx.current_glucose_mg_dl is not None:
            level_str = glucose_level.value if glucose_level else "unknown"
            lines.append(
                f"Current blood glucose: {ctx.current_glucose_mg_dl} mg/dL "
                f"(classification: {level_str})"
            )
        lines.append(f"Diabetes type: {ctx.diabetes_type.value}")
        if ctx.medications:
            lines.append(f"Medications: {', '.join(ctx.medications)}")
        if ctx.insulin_to_carb_ratio is not None:
            lines.append(
                f"Insulin-to-Carb Ratio (ICR): 1 Unit per {ctx.insulin_to_carb_ratio}g carb"
            )
        if ctx.correction_factor is not None:
            lines.append(
                f"Correction Factor (CF): 1 Unit per {ctx.correction_factor} mg/dL"
            )
        lines.append(f"Target glucose: {ctx.target_glucose_mg_dl} mg/dL")
        lines.append("")

        # --- Section 2: Meal Information ---
        lines.append("=== MEAL INFORMATION ===")
        lines.append(f"Meal: {request.meal_description}")
        if request.carbs_g is not None:
            lines.append(f"Estimated carbohydrates: {request.carbs_g:.1f} g")
        if request.glycemic_load is not None:
            lines.append(f"Estimated Glycemic Load: {request.glycemic_load:.1f}")
        lines.append("")

        # --- Section 3: Retrieved Medical Guidelines ---
        lines.append("=== MEDICAL GUIDELINES (from verified sources) ===")
        if search_results:
            for i, r in enumerate(search_results, 1):
                lines.append(
                    f"[{i}] Source: {r.source} | Category: {r.category} "
                    f"| Relevance: {r.combined_score:.2f}"
                )
                lines.append(r.content)
                lines.append("")
        else:
            lines.append("No matching guidelines found for this query.")
            lines.append("")

        # --- Section 4: Question ---
        lines.append("=== QUESTION ===")
        if PromptBuilder.is_emergency(glucose_level):
            lines.append(
                "The patient's glucose is at a DANGEROUS level. "
                "Provide the emergency protocol FIRST, then any meal advice."
            )
        else:
            lines.append(
                f"Based on the guidelines above, provide insulin dosing advice "
                f"for this meal ({request.meal_description}) considering the "
                f"patient's current glucose and medications."
            )

        return "\n".join(lines)
