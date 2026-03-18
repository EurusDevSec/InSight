import 'package:flutter/material.dart';

/// Large GL indicator widget — patient-friendly, big numbers.
class GlIndicator extends StatelessWidget {
  final double glycemicLoad;
  final String glLevel;

  const GlIndicator({
    super.key,
    required this.glycemicLoad,
    required this.glLevel,
  });

  Color get _color {
    switch (glLevel.toLowerCase()) {
      case 'low':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'high':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String get _label {
    switch (glLevel.toLowerCase()) {
      case 'low':
        return 'Thấp';
      case 'medium':
        return 'Trung bình';
      case 'high':
        return 'Cao';
      default:
        return glLevel;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 180,
      height: 180,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _color.withAlpha(30),
        border: Border.all(color: _color, width: 4),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('GL', style: TextStyle(fontSize: 14, color: Colors.grey)),
          Text(
            glycemicLoad.toStringAsFixed(1),
            style: TextStyle(
              fontSize: 42,
              fontWeight: FontWeight.bold,
              color: _color,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
            decoration: BoxDecoration(
              color: _color,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              _label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
