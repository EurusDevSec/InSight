import 'package:flutter/material.dart';
import '../data/services/local_storage_service.dart';

/// History ViewModel — manages meal history from local storage.
class HistoryViewModel extends ChangeNotifier {
  final LocalStorageService _storage;

  HistoryViewModel(this._storage);

  List<Map<String, dynamic>> get meals => _storage.mealHistory;

  /// Group meals by date.
  Map<String, List<Map<String, dynamic>>> get groupedMeals {
    final groups = <String, List<Map<String, dynamic>>>{};
    for (final meal in meals) {
      final ts = meal['timestamp'] as String?;
      if (ts == null) continue;
      final date = DateTime.tryParse(ts);
      if (date == null) continue;

      final now = DateTime.now();
      String label;
      if (date.year == now.year &&
          date.month == now.month &&
          date.day == now.day) {
        label = 'Hôm nay';
      } else if (date.year == now.year &&
          date.month == now.month &&
          date.day == now.day - 1) {
        label = 'Hôm qua';
      } else {
        label = '${date.day}/${date.month}/${date.year}';
      }

      groups.putIfAbsent(label, () => []).add(meal);
    }
    return groups;
  }

  Future<void> clearHistory() async {
    await _storage.clearHistory();
    notifyListeners();
  }

  void refresh() => notifyListeners();

  int get totalMealsToday {
    final now = DateTime.now();
    return meals.where((m) {
      final ts = m['timestamp'] as String?;
      if (ts == null) return false;
      final date = DateTime.tryParse(ts);
      if (date == null) return false;
      return date.year == now.year &&
          date.month == now.month &&
          date.day == now.day;
    }).length;
  }
}
