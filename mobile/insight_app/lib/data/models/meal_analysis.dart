/// Domain model for the result of a meal analysis.
class MealAnalysis {
  final String foodName;
  final double volumeMl;
  final double weightG;
  final double carbsG;
  final double glycemicLoad;
  final String glLevel; // low / medium / high
  final double confidence;
  final String? advice;
  final String? insulinSuggestion;
  final List<String> warnings;

  const MealAnalysis({
    required this.foodName,
    required this.volumeMl,
    required this.weightG,
    required this.carbsG,
    required this.glycemicLoad,
    required this.glLevel,
    required this.confidence,
    this.advice,
    this.insulinSuggestion,
    this.warnings = const [],
  });

  factory MealAnalysis.fromJson(Map<String, dynamic> json) {
    return MealAnalysis(
      foodName: json['food_name'] as String? ?? '',
      volumeMl: (json['volume_ml'] as num?)?.toDouble() ?? 0,
      weightG: (json['weight_g'] as num?)?.toDouble() ?? 0,
      carbsG: (json['carbs_g'] as num?)?.toDouble() ?? 0,
      glycemicLoad: (json['glycemic_load'] as num?)?.toDouble() ?? 0,
      glLevel: json['gl_level'] as String? ?? 'unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
      advice: json['advice'] as String?,
      insulinSuggestion: json['insulin_suggestion'] as String?,
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}
