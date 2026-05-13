import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Local storage service — history, settings, onboarding flag.
class LocalStorageService {
  static const _historyKey = 'meal_history';
  static const _onboardedKey = 'has_onboarded';
  static const _themeKey = 'theme_mode';
  static const _profileKey = 'patient_profile';

  late SharedPreferences _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // ─── Onboarding ───
  bool get hasOnboarded => _prefs.getBool(_onboardedKey) ?? false;
  Future<void> setOnboarded() => _prefs.setBool(_onboardedKey, true);

  // ─── Theme ───
  String get themeMode => _prefs.getString(_themeKey) ?? 'dark';
  Future<void> setThemeMode(String mode) => _prefs.setString(_themeKey, mode);

  // ─── Patient Profile ───
  Map<String, dynamic>? get patientProfile {
    final json = _prefs.getString(_profileKey);
    if (json == null) return null;
    return jsonDecode(json) as Map<String, dynamic>;
  }

  Future<void> savePatientProfile(Map<String, dynamic> profile) =>
      _prefs.setString(_profileKey, jsonEncode(profile));

  // ─── Meal History ───
  List<Map<String, dynamic>> get mealHistory {
    final json = _prefs.getString(_historyKey);
    if (json == null) return [];
    final list = jsonDecode(json) as List;
    return list.cast<Map<String, dynamic>>();
  }

  Future<void> addMealToHistory(Map<String, dynamic> meal) async {
    final history = mealHistory;
    history.insert(0, {
      ...meal,
      'timestamp': DateTime.now().toIso8601String(),
    });
    // Keep last 50 meals
    if (history.length > 50) history.removeRange(50, history.length);
    await _prefs.setString(_historyKey, jsonEncode(history));
  }

  Future<void> clearHistory() => _prefs.remove(_historyKey);
}
