import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'app.dart';
import 'data/services/api_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load .env if present (won't crash if missing)
  try {
    await dotenv.load(fileName: '.env');
  } catch (_) {
    // .env file not required for dev
  }

  final apiService = ApiService(
    visionBaseUrl: dotenv.env['VISION_BASE_URL'] ?? 'http://10.0.2.2:8000',
    ragBaseUrl: dotenv.env['RAG_BASE_URL'] ?? 'http://10.0.2.2:8001',
  );

  runApp(InsightApp(apiService: apiService));
}
