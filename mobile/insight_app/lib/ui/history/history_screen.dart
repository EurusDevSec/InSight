import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/history_viewmodel.dart';

/// History screen — grouped meal history list.
class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<HistoryViewModel>();
    final grouped = vm.groupedMeals;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lịch sử bữa ăn'),
        actions: [
          if (vm.meals.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              tooltip: 'Xoá lịch sử',
              onPressed: () => _confirmClear(context, vm),
            ),
        ],
      ),
      body: vm.meals.isEmpty
          ? _buildEmpty(context)
          : ListView.builder(
              padding: const EdgeInsets.all(AppSpacing.md),
              itemCount: grouped.length,
              itemBuilder: (context, i) {
                final date = grouped.keys.elementAt(i);
                final meals = grouped[date]!;
                return _buildGroup(context, date, meals);
              },
            ),
    );
  }

  Widget _buildEmpty(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history, size: 80, color: AppColors.textMuted.withAlpha(80)),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Chưa có bữa ăn nào',
            style: GoogleFonts.inter(
              fontSize: 18,
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Chụp ảnh phân tích để bắt đầu',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: AppColors.textMuted.withAlpha(150),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGroup(
      BuildContext context, String date, List<Map<String, dynamic>> meals) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
          child: Text(
            date,
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppColors.textMuted,
            ),
          ),
        ),
        ...meals.map((meal) => _buildMealItem(context, meal)),
        const SizedBox(height: AppSpacing.sm),
      ],
    );
  }

  Widget _buildMealItem(BuildContext context, Map<String, dynamic> meal) {
    final name = meal['food_name'] as String? ?? 'Không rõ';
    final gl = (meal['gl'] as num?)?.toDouble() ?? 0.0;
    final level = meal['gl_level'] as String? ?? 'unknown';
    final ts = meal['timestamp'] as String?;
    String time = '';
    if (ts != null) {
      final dt = DateTime.tryParse(ts);
      if (dt != null) {
        time = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
      }
    }

    final levelColor = switch (level.toLowerCase()) {
      'low' => AppColors.glLow,
      'medium' => AppColors.glMedium,
      'high' => AppColors.glHigh,
      _ => AppColors.textMuted,
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: InsightCard(
        child: Row(
          children: [
            // GL circle
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: levelColor.withAlpha(25),
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: Text(
                gl.toStringAsFixed(0),
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: levelColor,
                ),
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: GoogleFonts.inter(
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      if (time.isNotEmpty) ...[
                        Icon(Icons.access_time,
                            size: 13, color: AppColors.textMuted),
                        const SizedBox(width: 4),
                        Text(
                          time,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: AppColors.textMuted,
                          ),
                        ),
                        const SizedBox(width: AppSpacing.sm),
                      ],
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: levelColor,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _levelLabel(level),
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: levelColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: AppColors.textMuted.withAlpha(100)),
          ],
        ),
      ),
    );
  }

  String _levelLabel(String level) => switch (level.toLowerCase()) {
        'low' => 'Thấp',
        'medium' => 'Trung bình',
        'high' => 'Cao',
        _ => level,
      };

  void _confirmClear(BuildContext context, HistoryViewModel vm) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xoá lịch sử'),
        content: const Text('Bạn có chắc muốn xoá toàn bộ lịch sử bữa ăn?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Huỷ'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.emergency),
            onPressed: () {
              vm.clearHistory();
              Navigator.pop(ctx);
            },
            child: const Text('Xoá'),
          ),
        ],
      ),
    );
  }
}
