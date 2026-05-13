import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/insight_card.dart';
import '../../ui/widgets/food_emoji_icon.dart';
import '../../viewmodels/history_viewmodel.dart';

/// Home screen — dashboard with greeting, quick actions, recent meals, tips.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  String get _greeting {
    final hour = DateTime.now().hour;
    if (hour < 6) return 'Khuya rồi';
    if (hour < 12) return 'Chào buổi sáng';
    if (hour < 18) return 'Chào buổi chiều';
    return 'Chào buổi tối';
  }

  String get _greetingEmoji {
    final hour = DateTime.now().hour;
    if (hour < 6) return '🌙';
    if (hour < 12) return '☀️';
    if (hour < 18) return '🌤️';
    return '🌙';
  }

  @override
  Widget build(BuildContext context) {
    final history = context.watch<HistoryViewModel>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: AppSpacing.sm),

              // ─── Greeting ───
              Row(
                children: [
                  Text(_greetingEmoji, style: const TextStyle(fontSize: 28)),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _greeting,
                          style: GoogleFonts.inter(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Hôm nay bạn đã phân tích ${history.totalMealsToday} bữa ăn',
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  GestureDetector(
                    onTap: () => context.push('/profile'),
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: AppColors.primary.withAlpha(25),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.person, color: AppColors.primary, size: 22),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Quick Actions ───
              Row(
                children: [
                  Expanded(
                    child: _ActionCard(
                      icon: Icons.camera_alt_rounded,
                      label: 'Chụp ảnh\nphân tích',
                      gradientColors: const [AppColors.primary, AppColors.primaryDark],
                      onTap: () => context.go('/camera'),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: _ActionCard(
                      icon: Icons.flash_on_rounded,
                      label: 'Ước lượng\nnhanh ⚡',
                      gradientColors: const [AppColors.panicGradientStart, AppColors.panicGradientEnd],
                      onTap: () => context.go('/panic'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Recent Meals ───
              if (history.meals.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Bữa ăn gần đây',
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    TextButton(
                      onPressed: () => context.go('/history'),
                      child: Text(
                        'Xem tất cả',
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.sm),
                SizedBox(
                  height: 100,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: history.meals.take(5).length,
                    separatorBuilder: (_, __) =>
                        const SizedBox(width: AppSpacing.sm),
                    itemBuilder: (context, i) {
                      final meal = history.meals[i];
                      return _RecentMealChip(meal: meal);
                    },
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
              ],

              // ─── Tips ───
              Text(
                '💡 Mẹo sử dụng',
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              _TipCard(
                tip: 'Chụp từ trên xuống (top-down) để có kết quả chính xác nhất',
                icon: Icons.camera_alt,
              ),
              const SizedBox(height: AppSpacing.sm),
              _TipCard(
                tip: 'Đặt bát, thìa hoặc đũa cạnh món ăn làm vật tham chiếu',
                icon: Icons.straighten,
              ),
              const SizedBox(height: AppSpacing.sm),
              _TipCard(
                tip: 'Dùng Ước lượng nhanh khi không có mạng hoặc cần kết quả ngay',
                icon: Icons.flash_on,
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Disclaimer ───
              Container(
                padding: const EdgeInsets.all(AppSpacing.md),
                decoration: BoxDecoration(
                  color: AppColors.accent.withAlpha(isDark ? 15 : 30),
                  borderRadius: BorderRadius.circular(AppRadius.md),
                  border: Border.all(color: AppColors.accent.withAlpha(40)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber, color: AppColors.accent, size: 20),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: Text(
                        'Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ.',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: AppColors.accent,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.md),
            ],
          ),
        ),
      ),
    );
  }
}

/// Gradient action card.
class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final List<Color> gradientColors;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.label,
    required this.gradientColors,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 130,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(AppRadius.lg),
          boxShadow: [
            BoxShadow(
              color: gradientColors.first.withAlpha(60),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: Colors.white.withAlpha(40),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Icon(icon, color: Colors.white, size: 24),
            ),
            Text(
              label,
              style: GoogleFonts.inter(
                color: Colors.white,
                fontWeight: FontWeight.w600,
                fontSize: 14,
                height: 1.3,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Recent meal horizontal chip.
class _RecentMealChip extends StatelessWidget {
  final Map<String, dynamic> meal;
  const _RecentMealChip({required this.meal});

  @override
  Widget build(BuildContext context) {
    final name = meal['food_name'] as String? ?? '?';
    final gl = (meal['gl'] as num?)?.toDouble() ?? 0;
    final level = meal['gl_level'] as String? ?? '';
    final levelColor = switch (level.toLowerCase()) {
      'low' => AppColors.glLow,
      'medium' => AppColors.glMedium,
      'high' => AppColors.glHigh,
      _ => AppColors.textMuted,
    };

    return InsightCard(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: SizedBox(
        width: 120,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                FoodEmojiIcon(foodName: name, size: 20),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            Row(
              children: [
                Text(
                  'GL ${gl.toStringAsFixed(0)}',
                  style: GoogleFonts.inter(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: levelColor,
                  ),
                ),
                const SizedBox(width: 4),
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: levelColor,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Tip card with icon.
class _TipCard extends StatelessWidget {
  final String tip;
  final IconData icon;
  const _TipCard({required this.tip, required this.icon});

  @override
  Widget build(BuildContext context) {
    return InsightCard(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.primary),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Text(
              tip,
              style: GoogleFonts.inter(fontSize: 13, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}
