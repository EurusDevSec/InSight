import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';

import '../data/models/meal_analysis.dart';
import '../data/models/patient_context.dart';
import '../data/services/api_service.dart';

/// ViewModel for the main meal analysis flow.
///
/// Flow: pick image → analyzePipeline (Gateway) → show result.
class MealViewModel extends ChangeNotifier {
  final ApiService _apiService;

  MealViewModel(this._apiService);

  // ── State ──────────────────────────────────────────────────

  XFile? selectedImage;
  String? selectedFoodType;
  String? customFoodName;
  String? selectedSize;
  MealAnalysis? result;
  String? advice;
  String? insulinSuggestion;
  bool isLoading = false;
  String? error;
  bool debugMode = false;

  // ── Patient context (persisted across analyses) ────────────

  PatientContext patientContext = const PatientContext(
    glucoseLevel: 120,
    insulinCarbRatio: 10,
    correctionFactor: 50,
    targetGlucose: 100,
  );

  // ── Commands ───────────────────────────────────────────────

  void setImage(XFile image) {
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

  void setCustomFoodName(String? name) {
    customFoodName = name;
    notifyListeners();
  }

  void setSize(String? size) {
    selectedSize = size;
    notifyListeners();
  }

  void toggleDebugMode() {
    debugMode = !debugMode;
    notifyListeners();
  }

  void updatePatientContext(PatientContext ctx) {
    patientContext = ctx;
    notifyListeners();
  }

  /// Run the full analysis pipeline via the API Gateway.
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
      // Single Gateway call: Vision → RAG → combined result
      final analysis = await _apiService.analyzePipeline(
        imageFile: selectedImage!,
        foodId: selectedFoodType,
        customFoodName: customFoodName,
        patient: patientContext,
        debug: debugMode,
      );
      result = analysis;
      advice = analysis.advice;
      insulinSuggestion = analysis.insulinSuggestion;
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
    // Keep debugMode across resets
    notifyListeners();
  }
}
