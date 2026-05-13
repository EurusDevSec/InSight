import 'package:flutter/material.dart';

/// InSight color constants — medical-grade palette.
class AppColors {
  AppColors._();

  // Primary — Teal (y tế, tin cậy)
  static const primary = Color(0xFF009688);
  static const primaryLight = Color(0xFF4DB6AC);
  static const primaryDark = Color(0xFF00796B);

  // Accent
  static const accent = Color(0xFFFFC107);
  static const accentLight = Color(0xFFFFD54F);

  // Surface — Dark mode
  static const surfaceDark = Color(0xFF1A1D21);
  static const cardDark = Color(0xFF242830);
  static const cardDarkElevated = Color(0xFF2C3038);

  // Surface — Light mode
  static const surfaceLight = Color(0xFFF5F7FA);
  static const cardLight = Colors.white;

  // GL Levels
  static const glLow = Color(0xFF4CAF50);
  static const glMedium = Color(0xFFFF9800);
  static const glHigh = Color(0xFFE53935);

  // Emergency
  static const emergency = Color(0xFFE53935);
  static const emergencyLight = Color(0xFFFFCDD2);
  static const panicGradientStart = Color(0xFFFF6B35);
  static const panicGradientEnd = Color(0xFFE53935);

  // Misc
  static const success = Color(0xFF4CAF50);
  static const info = Color(0xFF2196F3);
  static const textMuted = Color(0xFF9E9E9E);
}

/// Spacing constants.
class AppSpacing {
  AppSpacing._();
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 16.0;
  static const lg = 24.0;
  static const xl = 32.0;
  static const xxl = 48.0;
}

/// Animation durations.
class AppDurations {
  AppDurations._();
  static const fast = Duration(milliseconds: 200);
  static const normal = Duration(milliseconds: 350);
  static const slow = Duration(milliseconds: 600);
  static const countUp = Duration(milliseconds: 1200);
}

/// Border radius.
class AppRadius {
  AppRadius._();
  static const sm = 8.0;
  static const md = 12.0;
  static const lg = 16.0;
  static const xl = 24.0;
  static const pill = 100.0;
}
