import 'package:flutter/material.dart';

/// Maps Vietnamese food names to emoji icons.
class FoodEmojiIcon extends StatelessWidget {
  final String foodName;
  final double size;

  const FoodEmojiIcon({super.key, required this.foodName, this.size = 32});

  static const _emojiMap = {
    'Cơm tấm': '🍚',
    'Cơm trắng': '🍚',
    'Cơm gà': '🍗',
    'Cơm chiên': '🍳',
    'Cơm bình dân': '🍱',
    'Phở bò': '🍜',
    'Phở gà': '🍜',
    'Bún bò': '🍜',
    'Bún chả': '🥘',
    'Bún riêu': '🍲',
    'Bún mắm': '🍲',
    'Bún thịt nướng': '🥩',
    'Hủ tiếu': '🍜',
    'Mì xào': '🍝',
    'Mì Quảng': '🍝',
    'Cao lầu': '🍝',
    'Bánh canh': '🍲',
    'Bánh mì': '🥖',
    'Bánh cuốn': '🥟',
    'Bánh xèo': '🥞',
    'Gỏi cuốn': '🥗',
    'Xôi': '🍙',
    'Cháo': '🥣',
    'Bột chiên': '🧈',
    'Trà sữa': '🧋',
    'Khác': '🍽️',
  };

  String get _emoji => _emojiMap[foodName] ?? '🍽️';

  @override
  Widget build(BuildContext context) {
    return Text(_emoji, style: TextStyle(fontSize: size));
  }
}
