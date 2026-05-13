import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'app.dart';
import 'data/services/api_service.dart';
import 'data/services/local_storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: '.env');

  final apiService = ApiService(
    gatewayBaseUrl: dotenv.env['GATEWAY_BASE_URL'] ?? 'http://localhost:8080',
  );
  final storageService = LocalStorageService();
  await storageService.init();

  runApp(InsightApp(
    apiService: apiService,
    storageService: storageService,
  ));
}
