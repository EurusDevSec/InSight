import 'dart:math';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/history_viewmodel.dart';

/// Analytics screen — GL trends, carb tracking, distribution charts.
class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<HistoryViewModel>();
    final meals = vm.meals;

    return Scaffold(
      appBar: AppBar(title: const Text('Phân tích dinh dưỡng')),
      body: meals.isEmpty
          ? _buildEmpty(context)
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ─── Summary Cards ───
                  _SummaryRow(meals: meals),
                  const SizedBox(height: AppSpacing.lg),

                  // ─── GL Trend Line ───
                  _sectionTitle('Xu hướng GL (7 ngày)'),
                  const SizedBox(height: AppSpacing.sm),
                  InsightCard(
                    child: SizedBox(
                      height: 220,
                      child: _GlTrendChart(meals: meals),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  // ─── Daily Carb Bar ───
                  _sectionTitle('Carb hàng ngày (g)'),
                  const SizedBox(height: AppSpacing.sm),
                  InsightCard(
                    child: SizedBox(
                      height: 200,
                      child: _CarbBarChart(meals: meals),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  // ─── GL Distribution ───
                  _sectionTitle('Phân bố GL'),
                  const SizedBox(height: AppSpacing.sm),
                  InsightCard(
                    child: SizedBox(
                      height: 200,
                      child: _GlDistributionChart(meals: meals),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  // ─── Meal Timing ───
                  _sectionTitle('Giờ ăn & GL'),
                  const SizedBox(height: AppSpacing.sm),
                  InsightCard(
                    child: SizedBox(
                      height: 220,
                      child: _MealTimingChart(meals: meals),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),
                ],
              ),
            ),
    );
  }

  Widget _buildEmpty(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.bar_chart, size: 80, color: AppColors.textMuted.withAlpha(80)),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Chưa có dữ liệu phân tích',
            style: GoogleFonts.inter(fontSize: 18, color: AppColors.textMuted),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Phân tích bữa ăn để xem biểu đồ',
            style: GoogleFonts.inter(
                fontSize: 14, color: AppColors.textMuted.withAlpha(150)),
          ),
        ],
      ),
    );
  }

  static Widget _sectionTitle(String text) {
    return Text(
      text,
      style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Summary row with 3 stat cards
// ═══════════════════════════════════════════════════════════════════

class _SummaryRow extends StatelessWidget {
  final List<Map<String, dynamic>> meals;
  const _SummaryRow({required this.meals});

  @override
  Widget build(BuildContext context) {
    final avgGl = meals.isEmpty
        ? 0.0
        : meals.map((m) => (m['gl'] as num?)?.toDouble() ?? 0).reduce((a, b) => a + b) /
            meals.length;
    final totalCarbs = meals.fold<double>(
        0, (sum, m) => sum + ((m['carbs_g'] as num?)?.toDouble() ?? 0));
    final highCount =
        meals.where((m) => (m['gl_level'] as String? ?? '') == 'high').length;

    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.speed,
            label: 'GL trung bình',
            value: avgGl.toStringAsFixed(1),
            color: AppColors.primary,
          ),
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: _StatCard(
            icon: Icons.restaurant,
            label: 'Tổng Carb',
            value: '${totalCarbs.toStringAsFixed(0)}g',
            color: AppColors.info,
          ),
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: _StatCard(
            icon: Icons.warning_amber,
            label: 'GL Cao',
            value: '$highCount bữa',
            color: AppColors.glHigh,
          ),
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  const _StatCard(
      {required this.icon,
      required this.label,
      required this.value,
      required this.color});

  @override
  Widget build(BuildContext context) {
    return InsightCard(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 6),
          Text(value,
              style: GoogleFonts.inter(
                  fontWeight: FontWeight.bold, fontSize: 18, color: color)),
          const SizedBox(height: 2),
          Text(label,
              style: GoogleFonts.inter(fontSize: 11, color: AppColors.textMuted),
              textAlign: TextAlign.center),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Chart 1: GL Trend Line (7 days)
// ═══════════════════════════════════════════════════════════════════

class _GlTrendChart extends StatelessWidget {
  final List<Map<String, dynamic>> meals;
  const _GlTrendChart({required this.meals});

  @override
  Widget build(BuildContext context) {
    // Group by day, compute average GL
    final now = DateTime.now();
    final spots = <FlSpot>[];

    for (int i = 6; i >= 0; i--) {
      final day = now.subtract(Duration(days: i));
      final dayMeals = meals.where((m) {
        final ts = m['timestamp'] as String?;
        if (ts == null) return false;
        final dt = DateTime.tryParse(ts);
        return dt != null &&
            dt.year == day.year &&
            dt.month == day.month &&
            dt.day == day.day;
      }).toList();

      if (dayMeals.isNotEmpty) {
        final avg = dayMeals
                .map((m) => (m['gl'] as num?)?.toDouble() ?? 0)
                .reduce((a, b) => a + b) /
            dayMeals.length;
        spots.add(FlSpot((6 - i).toDouble(), avg));
      }
    }

    if (spots.isEmpty) {
      return Center(
        child: Text('Chưa có dữ liệu',
            style: GoogleFonts.inter(color: AppColors.textMuted)),
      );
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 10,
          getDrawingHorizontalLine: (_) => FlLine(
            color: AppColors.textMuted.withAlpha(30),
            strokeWidth: 1,
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 32,
              getTitlesWidget: (value, meta) => Text(
                '${value.toInt()}',
                style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final day = now.subtract(Duration(days: 6 - value.toInt()));
                return Text(
                  '${day.day}/${day.month}',
                  style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: AppColors.primary,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
                radius: 4,
                color: AppColors.primary,
                strokeWidth: 2,
                strokeColor: Colors.white,
              ),
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  AppColors.primary.withAlpha(60),
                  AppColors.primary.withAlpha(10),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ],
        // GL level zone lines
        extraLinesData: ExtraLinesData(
          horizontalLines: [
            HorizontalLine(
              y: 10,
              color: AppColors.glLow.withAlpha(60),
              strokeWidth: 1,
              dashArray: [5, 5],
              label: HorizontalLineLabel(
                show: true,
                alignment: Alignment.topRight,
                style: GoogleFonts.inter(fontSize: 9, color: AppColors.glLow),
                labelResolver: (_) => 'Low',
              ),
            ),
            HorizontalLine(
              y: 20,
              color: AppColors.glHigh.withAlpha(60),
              strokeWidth: 1,
              dashArray: [5, 5],
              label: HorizontalLineLabel(
                show: true,
                alignment: Alignment.topRight,
                style: GoogleFonts.inter(fontSize: 9, color: AppColors.glHigh),
                labelResolver: (_) => 'High',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Chart 2: Daily Carb Bar Chart
// ═══════════════════════════════════════════════════════════════════

class _CarbBarChart extends StatelessWidget {
  final List<Map<String, dynamic>> meals;
  const _CarbBarChart({required this.meals});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final barGroups = <BarChartGroupData>[];

    for (int i = 6; i >= 0; i--) {
      final day = now.subtract(Duration(days: i));
      final totalCarbs = meals.where((m) {
        final ts = m['timestamp'] as String?;
        if (ts == null) return false;
        final dt = DateTime.tryParse(ts);
        return dt != null &&
            dt.year == day.year &&
            dt.month == day.month &&
            dt.day == day.day;
      }).fold<double>(0, (sum, m) => sum + ((m['carbs_g'] as num?)?.toDouble() ?? 0));

      barGroups.add(BarChartGroupData(
        x: 6 - i,
        barRods: [
          BarChartRodData(
            toY: totalCarbs,
            width: 18,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
            gradient: LinearGradient(
              colors: [AppColors.info, AppColors.primary],
              begin: Alignment.bottomCenter,
              end: Alignment.topCenter,
            ),
          ),
        ],
      ));
    }

    return BarChart(
      BarChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 50,
          getDrawingHorizontalLine: (_) => FlLine(
            color: AppColors.textMuted.withAlpha(30),
            strokeWidth: 1,
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 32,
              getTitlesWidget: (value, meta) => Text(
                '${value.toInt()}',
                style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final day = now.subtract(Duration(days: 6 - value.toInt()));
                return Text(
                  '${day.day}/${day.month}',
                  style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        barGroups: barGroups,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Chart 3: GL Distribution Pie
// ═══════════════════════════════════════════════════════════════════

class _GlDistributionChart extends StatelessWidget {
  final List<Map<String, dynamic>> meals;
  const _GlDistributionChart({required this.meals});

  @override
  Widget build(BuildContext context) {
    final low = meals.where((m) => (m['gl_level'] as String?) == 'low').length;
    final med =
        meals.where((m) => (m['gl_level'] as String?) == 'medium').length;
    final high =
        meals.where((m) => (m['gl_level'] as String?) == 'high').length;
    final total = low + med + high;

    if (total == 0) {
      return Center(
        child: Text('Chưa có dữ liệu',
            style: GoogleFonts.inter(color: AppColors.textMuted)),
      );
    }

    return Row(
      children: [
        Expanded(
          flex: 3,
          child: PieChart(
            PieChartData(
              sectionsSpace: 3,
              centerSpaceRadius: 40,
              sections: [
                PieChartSectionData(
                  value: low.toDouble(),
                  title: '${(low / total * 100).toStringAsFixed(0)}%',
                  color: AppColors.glLow,
                  radius: 45,
                  titleStyle: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white),
                ),
                PieChartSectionData(
                  value: med.toDouble(),
                  title: '${(med / total * 100).toStringAsFixed(0)}%',
                  color: AppColors.glMedium,
                  radius: 45,
                  titleStyle: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white),
                ),
                PieChartSectionData(
                  value: high.toDouble(),
                  title: '${(high / total * 100).toStringAsFixed(0)}%',
                  color: AppColors.glHigh,
                  radius: 45,
                  titleStyle: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          flex: 2,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _LegendItem(color: AppColors.glLow, label: 'Thấp', count: low),
              const SizedBox(height: 8),
              _LegendItem(
                  color: AppColors.glMedium, label: 'Trung bình', count: med),
              const SizedBox(height: 8),
              _LegendItem(color: AppColors.glHigh, label: 'Cao', count: high),
            ],
          ),
        ),
      ],
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final int count;
  const _LegendItem(
      {required this.color, required this.label, required this.count});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text('$label ($count)',
            style: GoogleFonts.inter(fontSize: 12, color: AppColors.textMuted)),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Chart 4: Meal Timing Scatter
// ═══════════════════════════════════════════════════════════════════

class _MealTimingChart extends StatelessWidget {
  final List<Map<String, dynamic>> meals;
  const _MealTimingChart({required this.meals});

  @override
  Widget build(BuildContext context) {
    final spots = <ScatterSpot>[];

    for (final meal in meals) {
      final ts = meal['timestamp'] as String?;
      final gl = (meal['gl'] as num?)?.toDouble() ?? 0;
      if (ts == null) continue;
      final dt = DateTime.tryParse(ts);
      if (dt == null) continue;

      final hour = dt.hour + dt.minute / 60.0;
      final color = switch ((meal['gl_level'] as String? ?? '').toLowerCase()) {
        'low' => AppColors.glLow,
        'medium' => AppColors.glMedium,
        'high' => AppColors.glHigh,
        _ => AppColors.textMuted,
      };
      final carbs = (meal['carbs_g'] as num?)?.toDouble() ?? 30;
      final radius = max(4.0, min(12.0, carbs / 8.0));

      spots.add(ScatterSpot(hour, gl,
          dotPainter: FlDotCirclePainter(
            radius: radius,
            color: color.withAlpha(180),
            strokeWidth: 1.5,
            strokeColor: color,
          )));
    }

    if (spots.isEmpty) {
      return Center(
        child: Text('Chưa có dữ liệu',
            style: GoogleFonts.inter(color: AppColors.textMuted)),
      );
    }

    return ScatterChart(
      ScatterChartData(
        scatterSpots: spots,
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 32,
              interval: 10,
              getTitlesWidget: (value, meta) => Text(
                '${value.toInt()}',
                style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              interval: 4,
              getTitlesWidget: (value, meta) => Text(
                '${value.toInt()}h',
                style: GoogleFonts.inter(fontSize: 10, color: AppColors.textMuted),
              ),
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 10,
          getDrawingHorizontalLine: (_) => FlLine(
            color: AppColors.textMuted.withAlpha(30),
            strokeWidth: 1,
          ),
        ),
        minX: 5,
        maxX: 23,
        minY: 0,
        maxY: 50,
      ),
    );
  }
}
