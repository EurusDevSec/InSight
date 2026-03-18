"""
Clinical rules engine for insulin dose calculation.

Task 3.3 — Rule-based (NOT LLM-based) insulin dose computation
following ADA Standards of Care 2024 formulas.
"""

from __future__ import annotations

from dataclasses import dataclass

from rag_pipeline.schemas import (
    AdviceRequest,
    GlucoseLevel,
    InsulinRecommendation,
)


@dataclass(frozen=True)
class DoseLimit:
    """Safety guard-rails for insulin dose calculation."""

    max_meal_dose: float = 25.0   # units
    max_correction_dose: float = 10.0  # units
    max_total_dose: float = 30.0  # units


DEFAULT_LIMITS = DoseLimit()


class ClinicalRules:
    """Rule-based clinical engine for insulin dose calculations.

    Formulas (ADA 2024):
        meal_dose = carbs_g / ICR
        correction_dose = max(0, (glucose - target) / CF)
        total_dose = meal_dose + correction_dose

    Safety:
        - No insulin during hypoglycemia (< 70 mg/dL)
        - Dose capping per DoseLimit
        - Requires ICR for meal dose; CF for correction
    """

    def __init__(self, limits: DoseLimit = DEFAULT_LIMITS) -> None:
        self.limits = limits

    def calculate_insulin(
        self,
        request: AdviceRequest,
        glucose_level: GlucoseLevel | None,
    ) -> InsulinRecommendation | None:
        """Compute insulin recommendation from patient data.

        Returns None when insufficient data (no ICR or no carbs).
        Returns zero-dose when hypoglycemic.
        """
        ctx = request.patient_context

        # No insulin during hypoglycemia
        if glucose_level in (GlucoseLevel.SEVERE_HYPO, GlucoseLevel.HYPO):
            return InsulinRecommendation(
                meal_dose_units=0,
                correction_dose_units=0,
                total_units=0,
                calculation_details=(
                    "No insulin — treat hypoglycemia first. "
                    "Apply Rule of 15: 15g fast-acting glucose, recheck in 15 min."
                ),
            )

        if ctx.insulin_to_carb_ratio is None or request.carbs_g is None:
            return None

        # Meal dose
        meal_dose = round(request.carbs_g / ctx.insulin_to_carb_ratio, 1)
        meal_dose = min(meal_dose, self.limits.max_meal_dose)
        details = (
            f"Meal dose: {request.carbs_g:.1f}g / "
            f"{ctx.insulin_to_carb_ratio}g/U = {meal_dose} U"
        )

        # Correction dose
        correction_dose = 0.0
        if (
            ctx.correction_factor is not None
            and ctx.current_glucose_mg_dl is not None
            and ctx.current_glucose_mg_dl > ctx.target_glucose_mg_dl
        ):
            raw_corr = (
                ctx.current_glucose_mg_dl - ctx.target_glucose_mg_dl
            ) / ctx.correction_factor
            correction_dose = round(max(0.0, raw_corr), 1)
            correction_dose = min(correction_dose, self.limits.max_correction_dose)
            details += (
                f"\nCorrection: ({ctx.current_glucose_mg_dl:.0f} - "
                f"{ctx.target_glucose_mg_dl:.0f}) / {ctx.correction_factor} "
                f"= {correction_dose} U"
            )

        total = round(meal_dose + correction_dose, 1)
        total = min(total, self.limits.max_total_dose)
        details += f"\nTotal: {meal_dose} + {correction_dose} = {total} U"

        return InsulinRecommendation(
            meal_dose_units=meal_dose,
            correction_dose_units=correction_dose,
            total_units=total,
            calculation_details=details,
        )

    @staticmethod
    def should_skip_insulin(glucose_level: GlucoseLevel | None) -> bool:
        """Return True if insulin should NOT be administered."""
        return glucose_level in (GlucoseLevel.SEVERE_HYPO, GlucoseLevel.HYPO)

    @staticmethod
    def needs_correction(
        glucose_mg_dl: float | None,
        target: float = 120.0,
    ) -> bool:
        """Return True if a correction dose is indicated."""
        if glucose_mg_dl is None:
            return False
        return glucose_mg_dl > target
