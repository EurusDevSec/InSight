import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/constants.dart';
import '../../ui/widgets/insight_card.dart';
import '../../ui/widgets/gl_indicator.dart';
import '../../ui/widgets/food_emoji_icon.dart';

/// Meal Detail Screen — shows full details of a past meal analysis.
class MealDetailScreen extends StatelessWidget {
  final Map<String, dynamic> meal;
  const MealDetailScreen({super.key, required this.meal});

  @override
  Widget build(BuildContext context) {
    final name = meal['food_name'] as String? ?? 'Không rõ';
    final gl = (meal['gl'] as num?)?.toDouble() ?? 0.0;
    final level = meal['gl_level'] as String? ?? 'unknown';
    final carbs = (meal['carbs_g'] as num?)?.toDouble();
    final weight = (meal['weight_g'] as num?)?.toDouble();
    final volume = (meal['volume_ml'] as num?)?.toDouble();
    final confidence = (meal['confidence'] as num?)?.toDouble();
    final advice = meal['advice'] as String?;
    final insulin = meal['insulin_suggestion'] as String?;
    final ts = meal['timestamp'] as String?;

    String dateStr = '';
    String timeStr = '';
    if (ts != null) {
      final dt = DateTime.tryParse(ts);
      if (dt != null) {
        timeStr =
            '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
        dateStr = '${dt.day}/${dt.month}/${dt.year}';
      }
    }

    final levelColor = switch (level.toLowerCase()) {
      'low' => AppColors.glLow,
      'medium' => AppColors.glMedium,
      'high' => AppColors.glHigh,
      _ => AppColors.textMuted,
    };

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            FoodEmojiIcon(foodName: name, size: 22),
            const SizedBox(width: 8),
            Flexible(
              child: Text(name, overflow: TextOverflow.ellipsis),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // ─── GL Indicator ───
            Center(child: GlIndicator(glycemicLoad: gl, glLevel: level)),
            const SizedBox(height: AppSpacing.lg),

            // ─── Nutrition Info ───
            InsightCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Thông tin dinh dưỡng',
                    style: GoogleFonts.inter(
                        fontWeight: FontWeight.w600, fontSize: 16),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  _InfoRow(
                      icon: Icons.restaurant,
                      label: 'Carbohydrate',
                      value: carbs != null ? '${carbs.toStringAsFixed(1)}g' : '—'),
                  const Divider(height: 24),
                  _InfoRow(
                      icon: Icons.scale,
                      label: 'Khối lượng',
                      value:
                          weight != null ? '${weight.toStringAsFixed(0)}g' : '—'),
                  const Divider(height: 24),
                  _InfoRow(
                      icon: Icons.water_drop,
                      label: 'Thể tích',
                      value: volume != null
                          ? '${volume.toStringAsFixed(0)} mL'
                          : '—'),
                  const Divider(height: 24),
                  _InfoRow(
                      icon: Icons.verified,
                      label: 'Độ tin cậy',
                      value: confidence != null
                          ? '${(confidence * 100).toStringAsFixed(0)}%'
                          : '—'),
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.md),

            // ─── Advice ───
            if (advice != null && advice.isNotEmpty)
              InsightCard(
                gradientColors: [levelColor, levelColor.withAlpha(180)],
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.tips_and_updates,
                            color: Colors.white, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'Tư vấn',
                          style: GoogleFonts.inter(
                            fontWeight: FontWeight.w600,
                            fontSize: 15,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      advice,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Colors.white.withAlpha(230),
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),

            if (insulin != null && insulin.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.md),
              InsightCard(
                child: Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: AppColors.info.withAlpha(25),
                        borderRadius: BorderRadius.circular(AppRadius.sm),
                      ),
                      child:
                          const Icon(Icons.medication, color: AppColors.info, size: 22),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Gợi ý Insulin',
                              style: GoogleFonts.inter(
                                  fontWeight: FontWeight.w600, fontSize: 14)),
                          const SizedBox(height: 4),
                          Text(
                            insulin,
                            style: GoogleFonts.inter(
                                fontSize: 13, color: AppColors.textMuted),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: AppSpacing.md),

            // ─── Timestamp ───
            if (dateStr.isNotEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.access_time,
                        size: 16, color: AppColors.textMuted),
                    const SizedBox(width: 6),
                    Text(
                      '$timeStr — $dateStr',
                      style: GoogleFonts.inter(
                          fontSize: 13, color: AppColors.textMuted),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: AppSpacing.md),

            // ─── Disclaimer ───
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.accent.withAlpha(15),
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(color: AppColors.accent.withAlpha(40)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber,
                      color: AppColors.accent, size: 18),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ.',
                      style: GoogleFonts.inter(
                          fontSize: 12, color: AppColors.accent),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _InfoRow(
      {required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppColors.primary),
        const SizedBox(width: AppSpacing.sm),
        Text(label, style: GoogleFonts.inter(fontSize: 14)),
        const Spacer(),
        Text(
          value,
          style: GoogleFonts.inter(
              fontWeight: FontWeight.w600, fontSize: 14),
        ),
      ],
    );
  }
}
