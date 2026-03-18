import 'package:flutter_test/flutter_test.dart';

import 'package:insight_app/data/models/food_item.dart';
import 'package:insight_app/data/models/meal_analysis.dart';
import 'package:insight_app/data/models/patient_context.dart';

void main() {
  group('FoodItem', () {
    test('fromJson parses correctly', () {
      final json = {
        'name': 'Cơm trắng',
        'volume_ml': 200.0,
        'weight_g': 180.5,
        'carbs_g': 45.0,
        'confidence_score': 0.95,
      };

      final item = FoodItem.fromJson(json);
      expect(item.name, 'Cơm trắng');
      expect(item.volumeMl, 200.0);
      expect(item.weightG, 180.5);
      expect(item.carbsG, 45.0);
      expect(item.confidenceScore, 0.95);
    });

    test('fromJson handles missing fields', () {
      final item = FoodItem.fromJson({});
      expect(item.name, '');
      expect(item.volumeMl, 0);
      expect(item.weightG, 0);
      expect(item.carbsG, 0);
      expect(item.confidenceScore, 0);
    });

    test('toJson round-trips', () {
      const item = FoodItem(
        name: 'Phở',
        volumeMl: 350,
        weightG: 400,
        carbsG: 50,
        confidenceScore: 0.8,
      );
      final json = item.toJson();
      expect(json['name'], 'Phở');
      expect(json['volume_ml'], 350);
      expect(json['weight_g'], 400);
      expect(json['carbs_g'], 50);
      expect(json['confidence_score'], 0.8);

      final roundTrip = FoodItem.fromJson(json);
      expect(roundTrip.name, item.name);
      expect(roundTrip.volumeMl, item.volumeMl);
    });
  });

  group('MealAnalysis', () {
    test('fromJson parses full response', () {
      final json = {
        'food_name': 'Phở bò',
        'volume_ml': 433.3,
        'weight_g': 132.6,
        'carbs_g': 29.8,
        'glycemic_load': 13.7,
        'gl_level': 'medium',
        'confidence': 0.945,
        'advice': 'Nên ăn kèm rau xanh',
        'insulin_suggestion': 'Tiêm thêm 3 Unit',
        'warnings': ['Liều cao hơn bình thường'],
      };

      final analysis = MealAnalysis.fromJson(json);
      expect(analysis.foodName, 'Phở bò');
      expect(analysis.volumeMl, 433.3);
      expect(analysis.carbsG, 29.8);
      expect(analysis.glycemicLoad, 13.7);
      expect(analysis.glLevel, 'medium');
      expect(analysis.confidence, 0.945);
      expect(analysis.advice, 'Nên ăn kèm rau xanh');
      expect(analysis.insulinSuggestion, 'Tiêm thêm 3 Unit');
      expect(analysis.warnings, hasLength(1));
    });

    test('fromJson handles minimal data', () {
      final analysis = MealAnalysis.fromJson({});
      expect(analysis.foodName, '');
      expect(analysis.volumeMl, 0);
      expect(analysis.glycemicLoad, 0);
      expect(analysis.glLevel, 'unknown');
      expect(analysis.warnings, isEmpty);
      expect(analysis.advice, isNull);
      expect(analysis.insulinSuggestion, isNull);
    });

    test('fromJson parses integer values as doubles', () {
      final json = {
        'food_name': 'Cơm',
        'volume_ml': 200,
        'weight_g': 180,
        'carbs_g': 45,
        'glycemic_load': 33,
        'gl_level': 'high',
        'confidence': 1,
      };
      final analysis = MealAnalysis.fromJson(json);
      expect(analysis.volumeMl, 200.0);
      expect(analysis.glycemicLoad, 33.0);
      expect(analysis.confidence, 1.0);
    });
  });

  group('PatientContext', () {
    test('toJson includes only non-null fields', () {
      const ctx = PatientContext(
        glucoseLevel: 180,
        insulinCarbRatio: 10,
      );
      final json = ctx.toJson();
      expect(json['glucose_level'], 180);
      expect(json['insulin_carb_ratio'], 10);
      expect(json.containsKey('medication_type'), isFalse);
      expect(json.containsKey('correction_factor'), isFalse);
      expect(json.containsKey('target_glucose'), isFalse);
    });

    test('toJson with all fields', () {
      const ctx = PatientContext(
        glucoseLevel: 200,
        medicationType: 'rapid_acting',
        insulinCarbRatio: 12,
        correctionFactor: 50,
        targetGlucose: 100,
      );
      final json = ctx.toJson();
      expect(json.length, 5);
      expect(json['medication_type'], 'rapid_acting');
    });

    test('toJson with no fields returns empty map', () {
      const ctx = PatientContext();
      expect(ctx.toJson(), isEmpty);
    });
  });
}
