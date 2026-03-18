import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'app.dart';
import 'data/services/api_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load .env — must be declared in pubspec.yaml assets
  try {
    await dotenv.load(fileName: '.env');
  } catch (_) {
    // .env not found: fallback to default URL
  }

  final gatewayBaseUrl = dotenv.isInitialized
      ? (dotenv.env['GATEWAY_BASE_URL'] ?? 'http://10.0.2.2:8080')
      : 'http://10.0.2.2:8080';

  final apiService = ApiService(
    gatewayBaseUrl: gatewayBaseUrl,
  );

  runApp(InsightApp(apiService: apiService));
}
