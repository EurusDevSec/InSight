import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/settings_viewmodel.dart';
import '../../viewmodels/history_viewmodel.dart';

/// Settings screen — theme, dev mode, about.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = context.watch<SettingsViewModel>();
    final history = context.watch<HistoryViewModel>();

    return Scaffold(
      appBar: AppBar(title: const Text('Cài đặt')),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.md),
        children: [
          // ─── Appearance ───
          _sectionTitle(context, 'Giao diện'),
          InsightCard(
            child: Column(
              children: [
                _themeTile(context, settings, 'Dark', ThemeMode.dark, Icons.dark_mode),
                const Divider(height: 1),
                _themeTile(context, settings, 'Light', ThemeMode.light, Icons.light_mode),
                const Divider(height: 1),
                _themeTile(context, settings, 'Hệ thống', ThemeMode.system, Icons.settings_brightness),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // ─── Data ───
          _sectionTitle(context, 'Dữ liệu'),
          InsightCard(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.history, color: AppColors.primary),
                  title: Text('Lịch sử bữa ăn', style: GoogleFonts.inter()),
                  subtitle: Text(
                    '${history.meals.length} bữa ăn đã lưu',
                    style: GoogleFonts.inter(fontSize: 13, color: AppColors.textMuted),
                  ),
                  trailing: TextButton(
                    onPressed: history.meals.isEmpty
                        ? null
                        : () => _confirmClear(context, history),
                    child: const Text('Xoá', style: TextStyle(color: AppColors.emergency)),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // ─── About ───
          _sectionTitle(context, 'Thông tin'),
          InsightCard(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.info_outline, color: AppColors.primary),
                  title: Text('Phiên bản', style: GoogleFonts.inter()),
                  trailing: Text(
                    '1.0.0',
                    style: GoogleFonts.inter(color: AppColors.textMuted),
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.school, color: AppColors.primary),
                  title: Text('Dự án', style: GoogleFonts.inter()),
                  subtitle: Text(
                    'Đồ án tốt nghiệp — InSight',
                    style: GoogleFonts.inter(fontSize: 13, color: AppColors.textMuted),
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.people, color: AppColors.primary),
                  title: Text('Nhóm phát triển', style: GoogleFonts.inter()),
                  subtitle: Text(
                    'Hoàng • Việt • Hoài',
                    style: GoogleFonts.inter(fontSize: 13, color: AppColors.textMuted),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // Disclaimer
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              color: AppColors.accent.withAlpha(15),
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
          const SizedBox(height: AppSpacing.xxl),
        ],
      ),
    );
  }

  Widget _sectionTitle(BuildContext context, String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: AppSpacing.sm),
      child: Text(
        text.toUpperCase(),
        style: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: AppColors.textMuted,
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _themeTile(BuildContext context, SettingsViewModel vm, String label,
      ThemeMode mode, IconData icon) {
    final selected = vm.themeMode == mode;
    return ListTile(
      leading: Icon(icon, color: selected ? AppColors.primary : AppColors.textMuted),
      title: Text(label, style: GoogleFonts.inter()),
      trailing: selected
          ? const Icon(Icons.check_circle, color: AppColors.primary, size: 20)
          : null,
      onTap: () => vm.setThemeMode(mode),
    );
  }

  void _confirmClear(BuildContext context, HistoryViewModel vm) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xoá lịch sử'),
        content: const Text('Bạn có chắc muốn xoá toàn bộ lịch sử bữa ăn?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Huỷ')),
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
