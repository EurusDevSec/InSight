import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'config/routes.dart';
import 'data/services/api_service.dart';
import 'viewmodels/meal_viewmodel.dart';
import 'viewmodels/panic_viewmodel.dart';

/// Root app widget with MVVM + Provider setup.
class InsightApp extends StatelessWidget {
  final ApiService apiService;

  const InsightApp({super.key, required this.apiService});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => MealViewModel(apiService),
        ),
        ChangeNotifierProvider(
          create: (_) => PanicViewModel(),
        ),
      ],
      child: MaterialApp.router(
        title: 'InSight',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorSchemeSeed: const Color(0xFF1565C0),
          useMaterial3: true,
          brightness: Brightness.light,
        ),
        routerConfig: router,
      ),
    );
  }
}
