import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'config/routes.dart';
import 'config/theme.dart';
import 'data/services/api_service.dart';
import 'data/services/local_storage_service.dart';
import 'viewmodels/meal_viewmodel.dart';
import 'viewmodels/panic_viewmodel.dart';
import 'viewmodels/history_viewmodel.dart';
import 'viewmodels/settings_viewmodel.dart';
import 'viewmodels/chat_viewmodel.dart';

/// Root app widget with MVVM + Provider setup.
class InsightApp extends StatelessWidget {
  final ApiService apiService;
  final LocalStorageService storageService;

  const InsightApp({
    super.key,
    required this.apiService,
    required this.storageService,
  });

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => MealViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => PanicViewModel()),
        ChangeNotifierProvider(create: (_) => HistoryViewModel(storageService)),
        ChangeNotifierProvider(create: (_) => SettingsViewModel(storageService)),
        ChangeNotifierProvider(create: (_) => ChatViewModel(apiService)),
      ],
      child: Consumer<SettingsViewModel>(
        builder: (context, settings, _) {
          final router = createRouter(hasOnboarded: settings.hasOnboarded);
          return MaterialApp.router(
            title: 'InSight',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: settings.themeMode,
            routerConfig: router,
          );
        },
      ),
    );
  }
}
