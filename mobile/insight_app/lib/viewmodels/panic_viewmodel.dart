import 'package:flutter/foundation.dart';

/// ViewModel for Panic Mode — instant GL estimation from cached data.
class PanicViewModel extends ChangeNotifier {
  /// Pre-cached common Vietnamese dishes with average GL values.
  static const List<Map<String, dynamic>> commonDishes = [
    {
      'name': 'Cơm trắng (1 chén)',
      'carbs_g': 45.0,
      'glycemic_load': 33.0,
      'gl_level': 'high',
    },
    {
      'name': 'Phở bò (1 tô)',
      'carbs_g': 50.0,
      'glycemic_load': 30.0,
      'gl_level': 'high',
    },
    {
      'name': 'Bún bò Huế (1 tô)',
      'carbs_g': 55.0,
      'glycemic_load': 28.0,
      'gl_level': 'high',
    },
    {
      'name': 'Cơm tấm (đĩa vừa)',
      'carbs_g': 60.0,
      'glycemic_load': 35.0,
      'gl_level': 'high',
    },
    {
      'name': 'Bánh mì thịt',
      'carbs_g': 40.0,
      'glycemic_load': 22.0,
      'gl_level': 'high',
    },
    {
      'name': 'Xôi (1 nắm)',
      'carbs_g': 35.0,
      'glycemic_load': 20.0,
      'gl_level': 'high',
    },
    {
      'name': 'Bún chả (1 suất)',
      'carbs_g': 42.0,
      'glycemic_load': 22.0,
      'gl_level': 'high',
    },
    {
      'name': 'Cháo (1 tô)',
      'carbs_g': 30.0,
      'glycemic_load': 25.0,
      'gl_level': 'high',
    },
    {
      'name': 'Rau xào (1 đĩa)',
      'carbs_g': 8.0,
      'glycemic_load': 3.0,
      'gl_level': 'low',
    },
    {
      'name': 'Trái cây (1 phần)',
      'carbs_g': 15.0,
      'glycemic_load': 8.0,
      'gl_level': 'medium',
    },
  ];

  Map<String, dynamic>? selectedDish;
  bool isSelected = false;

  void selectDish(int index) {
    selectedDish = commonDishes[index];
    isSelected = true;
    notifyListeners();
  }

  void reset() {
    selectedDish = null;
    isSelected = false;
    notifyListeners();
  }
}
