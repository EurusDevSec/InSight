import 'package:flutter/material.dart';
import '../../config/constants.dart';

/// Glassmorphism-style card with subtle gradient border.
class InsightCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;
  final List<Color>? gradientColors;

  const InsightCard({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
    this.gradientColors,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? AppColors.cardDark : AppColors.cardLight;

    Widget card = Container(
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: gradientColors != null
            ? null
            : Border.all(
                color: isDark
                    ? Colors.white.withAlpha(15)
                    : Colors.black.withAlpha(10),
              ),
        boxShadow: isDark
            ? null
            : [
                BoxShadow(
                  color: Colors.black.withAlpha(8),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(AppSpacing.md),
        child: child,
      ),
    );

    if (gradientColors != null) {
      card = Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors!,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(AppRadius.lg),
        ),
        padding: const EdgeInsets.all(1.5),
        child: card,
      );
    }

    if (onTap != null) {
      return GestureDetector(onTap: onTap, child: card);
    }
    return card;
  }
}
