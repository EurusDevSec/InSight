import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../models/meal_analysis.dart';
import '../models/patient_context.dart';

/// Stateless service wrapping the InSight backend APIs.
///
/// Routes all requests through the API Gateway, which orchestrates
/// Vision → RAG pipeline and returns combined results.
class ApiService {
  final String gatewayBaseUrl;
  final http.Client _client;

  ApiService({
    required this.gatewayBaseUrl,
    http.Client? client,
  }) : _client = client ?? http.Client();

  // ── Gateway: Full pipeline ───────────────────────────────────

  /// Send image + context through the Gateway pipeline.
  ///
  /// Gateway flow: image → Vision (volume/GL) → RAG (advice) → combined.
  Future<MealAnalysis> analyzePipeline({
    required XFile imageFile,
    String? foodId,
    PatientContext? patient,
  }) async {
    final uri = Uri.parse('$gatewayBaseUrl/api/gateway/analyze');

    final bytes = await imageFile.readAsBytes();
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes('image', bytes, filename: imageFile.name),
      );
    if (foodId != null) request.fields['food_id'] = foodId;
    if (patient != null) {
      if (patient.glucoseLevel != null) {
        request.fields['glucose_level'] = patient.glucoseLevel.toString();
      }
      if (patient.medicationType != null) {
        request.fields['diabetes_type'] = patient.medicationType!;
      }
      if (patient.insulinCarbRatio != null) {
        request.fields['insulin_carb_ratio'] =
            patient.insulinCarbRatio.toString();
      }
      if (patient.correctionFactor != null) {
        request.fields['correction_factor'] =
            patient.correctionFactor.toString();
      }
      if (patient.targetGlucose != null) {
        request.fields['target_glucose'] = patient.targetGlucose.toString();
      }
    }

    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);

    if (response.statusCode == 200) {
      return MealAnalysis.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    throw Exception(
      'Gateway analysis failed (${response.statusCode}): ${response.body}',
    );
  }

  // ── Health check ─────────────────────────────────────────────

  Future<bool> checkGatewayHealth() async {
    try {
      final resp = await _client.get(
        Uri.parse('$gatewayBaseUrl/api/health'),
      );
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
