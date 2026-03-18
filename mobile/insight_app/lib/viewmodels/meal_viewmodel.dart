import 'dart:io';

import 'package:flutter/foundation.dart';

import '../data/models/meal_analysis.dart';
import '../data/models/patient_context.dart';
import '../data/services/api_service.dart';

/// ViewModel for the main meal analysis flow.
///
/// Flow: pick image → analyzeMeal → (optional) getAdvice → show result.
class MealViewModel extends ChangeNotifier {
  final ApiService _apiService;

  MealViewModel(this._apiService);

  // ── State ──────────────────────────────────────────────────

  File? selectedImage;
  String? selectedFoodType;
  String? selectedSize;
  MealAnalysis? result;
  String? advice;
  String? insulinSuggestion;
  bool isLoading = false;
  String? error;

  // ── Patient context (persisted across analyses) ────────────

  PatientContext patientContext = const PatientContext(
    glucoseLevel: 120,
    insulinCarbRatio: 10,
    correctionFactor: 50,
    targetGlucose: 100,
  );

  // ── Commands ───────────────────────────────────────────────

  void setImage(File image) {
    selectedImage = image;
    result = null;
    advice = null;
    insulinSuggestion = null;
    error = null;
    notifyListeners();
  }

  void setFoodType(String? type) {
    selectedFoodType = type;
    notifyListeners();
  }

  void setSize(String? size) {
    selectedSize = size;
    notifyListeners();
  }

  void updatePatientContext(PatientContext ctx) {
    patientContext = ctx;
    notifyListeners();
  }

  /// Run the full analysis pipeline: Vision → RAG.
  Future<void> analyze() async {
    if (selectedImage == null) {
      error = 'No image selected';
      notifyListeners();
      return;
    }

    isLoading = true;
    error = null;
    notifyListeners();

    try {
      // Step 1: Vision analysis
      final analysis = await _apiService.analyzeMeal(
        imageFile: selectedImage!,
        foodType: selectedFoodType,
      );
      result = analysis;
      notifyListeners();

      // Step 2: RAG advice
      final ragResult = await _apiService.getAdvice(
        carbsG: analysis.carbsG,
        glycemicLoad: analysis.glycemicLoad,
        glLevel: analysis.glLevel,
        foodName: analysis.foodName,
        patient: patientContext,
      );
      advice = ragResult['advice'] as String?;
      insulinSuggestion = ragResult['insulin_suggestion'] as String?;
    } catch (e) {
      error = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  void reset() {
    selectedImage = null;
    selectedFoodType = null;
    selectedSize = null;
    result = null;
    advice = null;
    insulinSuggestion = null;
    error = null;
    isLoading = false;
    notifyListeners();
  }
}
