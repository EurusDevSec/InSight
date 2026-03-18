/// Patient context sent with meal analysis requests.
class PatientContext {
  final double? glucoseLevel;
  final String? medicationType;
  final double? insulinCarbRatio;
  final double? correctionFactor;
  final double? targetGlucose;

  const PatientContext({
    this.glucoseLevel,
    this.medicationType,
    this.insulinCarbRatio,
    this.correctionFactor,
    this.targetGlucose,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (glucoseLevel != null) map['glucose_level'] = glucoseLevel;
    if (medicationType != null) map['medication_type'] = medicationType;
    if (insulinCarbRatio != null) map['insulin_carb_ratio'] = insulinCarbRatio;
    if (correctionFactor != null) map['correction_factor'] = correctionFactor;
    if (targetGlucose != null) map['target_glucose'] = targetGlucose;
    return map;
  }
}
