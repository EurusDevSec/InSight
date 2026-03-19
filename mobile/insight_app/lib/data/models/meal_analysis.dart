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

  // Debug / Developer Mode data
  final DebugData? debug;

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
    this.debug,
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
      debug: json['debug'] != null
          ? DebugData.fromJson(json['debug'] as Map<String, dynamic>)
          : null,
    );
  }
}

/// Developer mode debug data from the pipeline.
class DebugData {
  // Vision debug
  final String? depthPreview;
  final String? foodMaskPreview;
  final List<Map<String, dynamic>>? referenceObjects;
  final double? scalePxPerCm;
  final double? tableLevelCm;
  final String? formula;

  // RAG debug
  final List<Map<String, dynamic>>? retrievedChunks;
  final String? promptPreview;
  final String? llmRaw;

  const DebugData({
    this.depthPreview,
    this.foodMaskPreview,
    this.referenceObjects,
    this.scalePxPerCm,
    this.tableLevelCm,
    this.formula,
    this.retrievedChunks,
    this.promptPreview,
    this.llmRaw,
  });

  factory DebugData.fromJson(Map<String, dynamic> json) {
    return DebugData(
      depthPreview: json['depth_preview'] as String?,
      foodMaskPreview: json['food_mask_preview'] as String?,
      referenceObjects: (json['reference_objects'] as List<dynamic>?)
          ?.map((e) => Map<String, dynamic>.from(e as Map))
          .toList(),
      scalePxPerCm: (json['scale_px_per_cm'] as num?)?.toDouble(),
      tableLevelCm: (json['table_level_cm'] as num?)?.toDouble(),
      formula: json['formula'] as String?,
      retrievedChunks: (json['retrieved_chunks'] as List<dynamic>?)
          ?.map((e) => Map<String, dynamic>.from(e as Map))
          .toList(),
      promptPreview: json['prompt_preview'] as String?,
      llmRaw: json['llm_raw'] as String?,
    );
  }
}
