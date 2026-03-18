/// Domain model for a food item in a meal analysis.
class FoodItem {
  final String name;
  final double volumeMl;
  final double weightG;
  final double carbsG;
  final double confidenceScore;

  const FoodItem({
    required this.name,
    required this.volumeMl,
    required this.weightG,
    required this.carbsG,
    required this.confidenceScore,
  });

  factory FoodItem.fromJson(Map<String, dynamic> json) {
    return FoodItem(
      name: json['name'] as String? ?? '',
      volumeMl: (json['volume_ml'] as num?)?.toDouble() ?? 0,
      weightG: (json['weight_g'] as num?)?.toDouble() ?? 0,
      carbsG: (json['carbs_g'] as num?)?.toDouble() ?? 0,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'volume_ml': volumeMl,
        'weight_g': weightG,
        'carbs_g': carbsG,
        'confidence_score': confidenceScore,
      };
}
