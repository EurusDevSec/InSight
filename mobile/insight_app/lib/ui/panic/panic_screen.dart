import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/gl_indicator.dart';
import '../../ui/widgets/disclaimer_banner.dart';
import '../../ui/widgets/food_emoji_icon.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/panic_viewmodel.dart';

/// Panic Mode — 1-tap instant GL estimation from cached data.
class PanicScreen extends StatelessWidget {
  const PanicScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<PanicViewModel>();

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.flash_on, color: AppColors.panicGradientStart, size: 22),
            const SizedBox(width: 6),
            Text('Ước lượng nhanh',
              style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            vm.reset();
            context.go('/');
          },
        ),
      ),
      body: SafeArea(
        child: vm.isSelected ? _buildResult(context, vm) : _buildGrid(context, vm),
      ),
    );
  }

  Widget _buildGrid(BuildContext context, PanicViewModel vm) {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with gradient accent
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppColors.panicGradientStart.withAlpha(25),
                  AppColors.panicGradientEnd.withAlpha(15),
                ],
              ),
              borderRadius: BorderRadius.circular(AppRadius.md),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Chọn món đang ăn',
                  style: GoogleFonts.inter(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Chạm 1 lần để ước lượng GL ngay • Không cần mạng',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.4,
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
              ),
              itemCount: PanicViewModel.commonDishes.length,
              itemBuilder: (context, index) {
                final dish = PanicViewModel.commonDishes[index];
                return _DishCard(
                  name: dish['name'] as String,
                  carbsG: dish['carbs_g'] as double,
                  onTap: () => vm.selectDish(index),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResult(BuildContext context, PanicViewModel vm) {
    final dish = vm.selectedDish!;
    final level = dish['gl_level'] as String;
    final levelColor = switch (level.toLowerCase()) {
      'low' => AppColors.glLow,
      'medium' => AppColors.glMedium,
      'high' => AppColors.glHigh,
      _ => AppColors.textMuted,
    };

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Column(
        children: [
          GlIndicator(
            glycemicLoad: dish['glycemic_load'] as double,
            glLevel: level,
          ),
          const SizedBox(height: AppSpacing.lg),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              FoodEmojiIcon(foodName: dish['name'] as String, size: 28),
              const SizedBox(width: AppSpacing.sm),
              Text(
                dish['name'] as String,
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          InsightCard(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _stat('Carb', '${(dish['carbs_g'] as double).toStringAsFixed(0)}g', levelColor),
                Container(width: 1, height: 40, color: Colors.white.withAlpha(15)),
                _stat('GL', (dish['glycemic_load'] as double).toStringAsFixed(0), levelColor),
                Container(width: 1, height: 40, color: Colors.white.withAlpha(15)),
                _stat('Mức', _levelLabel(level), levelColor),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          InsightCard(
            child: Row(
              children: [
                Icon(Icons.info_outline, size: 18, color: AppColors.info),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    'Kết quả dựa trên trung bình thống kê.\nĐể chính xác hơn, hãy dùng chế độ Chụp ảnh phân tích.',
                    style: GoogleFonts.inter(fontSize: 13, color: AppColors.textMuted),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          const DisclaimerBanner(),
          const SizedBox(height: AppSpacing.lg),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 48,
                  child: OutlinedButton(
                    onPressed: () => vm.reset(),
                    child: const Text('Chọn món khác'),
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: SizedBox(
                  height: 48,
                  child: FilledButton(
                    onPressed: () {
                      vm.reset();
                      context.go('/');
                    },
                    child: const Text('Xong'),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _stat(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.inter(fontSize: 12, color: AppColors.textMuted),
        ),
      ],
    );
  }

  String _levelLabel(String level) => switch (level.toLowerCase()) {
        'low' => 'Thấp',
        'medium' => 'TB',
        'high' => 'Cao',
        _ => level,
      };
}

/// Panic dish card with emoji.
class _DishCard extends StatelessWidget {
  final String name;
  final double carbsG;
  final VoidCallback onTap;

  const _DishCard({
    required this.name,
    required this.carbsG,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InsightCard(
      onTap: onTap,
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          FoodEmojiIcon(foodName: name, size: 28),
          const SizedBox(height: 6),
          Text(
            name,
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14),
          ),
          const SizedBox(height: 2),
          Text(
            '~${carbsG.toStringAsFixed(0)}g Carb',
            style: GoogleFonts.inter(
              color: AppColors.textMuted,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
