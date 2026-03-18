import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:insight_app/data/models/meal_analysis.dart';
import 'package:insight_app/data/models/patient_context.dart';
import 'package:insight_app/data/services/api_service.dart';
import 'package:insight_app/viewmodels/meal_viewmodel.dart';

/// Fake API service for testing.
class FakeApiService extends ApiService {
  bool analyzeCalled = false;
  bool shouldThrow = false;

  FakeApiService() : super(gatewayBaseUrl: 'http://fake');

  @override
  Future<MealAnalysis> analyzePipeline({
    required File imageFile,
    String? foodId,
    PatientContext? patient,
  }) async {
    analyzeCalled = true;
    if (shouldThrow) throw Exception('Network error');

    return MealAnalysis.fromJson({
      'food_name': 'Test Food',
      'volume_ml': 200.0,
      'weight_g': 150.0,
      'carbs_g': 40.0,
      'glycemic_load': 20.0,
      'gl_level': 'high',
      'confidence': 0.9,
      'advice': 'Test advice',
      'insulin_suggestion': 'Test insulin',
    });
  }
}

void main() {
  group('MealViewModel', () {
    late MealViewModel vm;
    late FakeApiService fakeApi;

    setUp(() {
      fakeApi = FakeApiService();
      vm = MealViewModel(fakeApi);
    });

    test('initial state is clean', () {
      expect(vm.selectedImage, isNull);
      expect(vm.selectedFoodType, isNull);
      expect(vm.result, isNull);
      expect(vm.advice, isNull);
      expect(vm.isLoading, isFalse);
      expect(vm.error, isNull);
    });

    test('setImage updates state and clears previous result', () {
      var notified = false;
      vm.addListener(() => notified = true);

      final file = File('test.jpg');
      vm.setImage(file);

      expect(vm.selectedImage, file);
      expect(vm.result, isNull);
      expect(notified, isTrue);
    });

    test('setFoodType updates state', () {
      vm.setFoodType('Phở');
      expect(vm.selectedFoodType, 'Phở');
    });

    test('setSize updates state', () {
      vm.setSize('Lớn');
      expect(vm.selectedSize, 'Lớn');
    });

    test('analyze without image sets error', () async {
      await vm.analyze();
      expect(vm.error, 'No image selected');
      expect(vm.isLoading, isFalse);
    });

    test('updatePatientContext updates state', () {
      const ctx = PatientContext(glucoseLevel: 200);
      vm.updatePatientContext(ctx);
      expect(vm.patientContext.glucoseLevel, 200);
    });

    test('reset clears all state', () {
      vm.setFoodType('Cơm');
      vm.setSize('Vừa');

      vm.reset();

      expect(vm.selectedImage, isNull);
      expect(vm.selectedFoodType, isNull);
      expect(vm.selectedSize, isNull);
      expect(vm.result, isNull);
      expect(vm.advice, isNull);
      expect(vm.insulinSuggestion, isNull);
      expect(vm.error, isNull);
      expect(vm.isLoading, isFalse);
    });

    test('default patient context has values', () {
      expect(vm.patientContext.glucoseLevel, isNotNull);
      expect(vm.patientContext.insulinCarbRatio, isNotNull);
    });
  });
}
