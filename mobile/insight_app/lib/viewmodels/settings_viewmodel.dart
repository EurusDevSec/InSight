import 'package:flutter/material.dart';
import '../data/services/local_storage_service.dart';

/// Settings ViewModel — theme mode, dev mode, server config.
class SettingsViewModel extends ChangeNotifier {
  final LocalStorageService _storage;

  SettingsViewModel(this._storage);

  // ─── Theme ───
  ThemeMode get themeMode {
    switch (_storage.themeMode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.dark; // default dark for medical app
    }
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    final value = switch (mode) {
      ThemeMode.light => 'light',
      ThemeMode.dark => 'dark',
      ThemeMode.system => 'system',
    };
    await _storage.setThemeMode(value);
    notifyListeners();
  }

  // ─── Onboarding ───
  bool get hasOnboarded => _storage.hasOnboarded;
  Future<void> completeOnboarding() async {
    await _storage.setOnboarded();
    notifyListeners();
  }
}
