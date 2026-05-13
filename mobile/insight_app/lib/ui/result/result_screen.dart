import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../data/models/meal_analysis.dart';
import '../../ui/widgets/gl_indicator.dart';
import '../../ui/widgets/disclaimer_banner.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/meal_viewmodel.dart';
import '../../viewmodels/history_viewmodel.dart';

/// Result screen showing GL analysis — animated, patient-friendly.
class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _savedToHistory = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _saveToHistory());
  }

  void _saveToHistory() {
    if (_savedToHistory) return;
    final vm = context.read<MealViewModel>();
    final result = vm.result;
    if (result == null) return;

    final history = context.read<HistoryViewModel>();
    history.addMeal({
      'food_name': result.foodName,
      'gl': result.glycemicLoad,
      'gl_level': result.glLevel,
      'volume_ml': result.volumeMl,
      'weight_g': result.weightG,
      'carbs_g': result.carbsG,
      'confidence': result.confidence,
      'advice': vm.advice,
      'insulin_suggestion': vm.insulinSuggestion,
    });

    _savedToHistory = true;
  }

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<MealViewModel>();
    final result = vm.result;

    if (result == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Kết quả')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.analytics_outlined,
                  size: 64, color: AppColors.textMuted.withAlpha(80)),
              const SizedBox(height: AppSpacing.md),
              Text(
                'Chưa có kết quả phân tích',
                style: GoogleFonts.inter(color: AppColors.textMuted),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kết quả GL'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            vm.reset();
            context.go('/');
          },
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            children: [
              // GL Indicator (animated)
              GlIndicator(
                glycemicLoad: result.glycemicLoad,
                glLevel: result.glLevel,
              ),
              const SizedBox(height: AppSpacing.lg),

              // Food name
              Text(
                result.foodName,
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSpacing.md),

              // Warnings
              if (result.warnings.isNotEmpty) ...[
                ...result.warnings.map((w) {
                  final isCritical = w.contains('CẢNH BÁO');
                  return Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: AppSpacing.sm),
                    padding: const EdgeInsets.all(AppSpacing.md),
                    decoration: BoxDecoration(
                      color: isCritical
                          ? AppColors.emergency.withAlpha(20)
                          : AppColors.accent.withAlpha(15),
                      borderRadius: BorderRadius.circular(AppRadius.md),
                      border: Border.all(
                        color: isCritical
                            ? AppColors.emergency.withAlpha(60)
                            : AppColors.accent.withAlpha(40),
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          isCritical ? Icons.dangerous : Icons.warning_amber,
                          color: isCritical ? AppColors.emergency : AppColors.accent,
                          size: 20,
                        ),
                        const SizedBox(width: AppSpacing.sm),
                        Expanded(
                          child: Text(
                            w,
                            style: GoogleFonts.inter(
                              color: isCritical ? AppColors.emergency : null,
                              fontWeight: isCritical ? FontWeight.bold : null,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: AppSpacing.sm),
              ],

              // Nutrition details
              InsightCard(
                child: Column(
                  children: [
                    _buildRow('Thể tích', '${result.volumeMl.toStringAsFixed(1)} mL'),
                    Divider(color: Colors.white.withAlpha(12)),
                    _buildRow('Khối lượng', '${result.weightG.toStringAsFixed(1)} g'),
                    Divider(color: Colors.white.withAlpha(12)),
                    _buildRow('Carbohydrate', '${result.carbsG.toStringAsFixed(1)} g'),
                    Divider(color: Colors.white.withAlpha(12)),
                    _buildRow(
                      'Độ tin cậy',
                      result.confidence <= 0.5
                          ? '⚠️ Thấp'
                          : '${(result.confidence * 100).toStringAsFixed(0)}%',
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.md),

              // Insulin advice
              if (vm.advice != null || vm.insulinSuggestion != null)
                InsightCard(
                  gradientColors: const [AppColors.info, AppColors.primary],
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.medical_information,
                              color: AppColors.info, size: 22),
                          const SizedBox(width: AppSpacing.sm),
                          Text(
                            'Tư vấn Insulin',
                            style: GoogleFonts.inter(
                              fontWeight: FontWeight.bold,
                              color: AppColors.info,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                      if (vm.insulinSuggestion != null) ...[
                        const SizedBox(height: AppSpacing.md),
                        Text(
                          vm.insulinSuggestion!,
                          style: GoogleFonts.inter(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                      if (vm.advice != null) ...[
                        const SizedBox(height: AppSpacing.sm),
                        Text(
                          vm.advice!,
                          style: GoogleFonts.inter(fontSize: 14, height: 1.5),
                        ),
                      ],
                    ],
                  ),
                ),

              const SizedBox(height: AppSpacing.md),
              const DisclaimerBanner(),
              const SizedBox(height: AppSpacing.md),

              // Developer Mode toggle + panel
              if (result.debug != null) _DeveloperModePanel(debug: result.debug!),

              const SizedBox(height: AppSpacing.lg),

              // New analysis button
              SizedBox(
                width: double.infinity,
                height: 48,
                child: OutlinedButton.icon(
                  onPressed: () {
                    vm.reset();
                    context.go('/camera');
                  },
                  icon: const Icon(Icons.refresh),
                  label: Text('Phân tích món mới',
                      style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: GoogleFonts.inter(color: AppColors.textMuted, fontSize: 14)),
          Text(value,
              style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
        ],
      ),
    );
  }
}

/// Collapsible pipeline visualization — user-friendly debug info.
class _DeveloperModePanel extends StatelessWidget {
  final DebugData debug;
  const _DeveloperModePanel({required this.debug});

  @override
  Widget build(BuildContext context) {
    return InsightCard(
      padding: EdgeInsets.zero,
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
          leading: Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.primary.withAlpha(25),
              borderRadius: BorderRadius.circular(AppRadius.sm),
            ),
            child: const Icon(Icons.insights, color: AppColors.primary, size: 20),
          ),
          title: Text(
            'Chi tiết phân tích',
            style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 15),
          ),
          subtitle: Text(
            'Xem cách AI hoạt động',
            style: GoogleFonts.inter(color: AppColors.textMuted, fontSize: 12),
          ),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(
                  AppSpacing.md, 0, AppSpacing.md, AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Divider(),
                  const SizedBox(height: AppSpacing.sm),

                  // 1. Depth Map
                  if (debug.depthPreview != null)
                    _section(
                      Icons.layers, const Color(0xFF64B5F6),
                      'Bản đồ độ sâu', 'Depth Anything V2',
                      ClipRRect(
                        borderRadius: BorderRadius.circular(AppRadius.sm),
                        child: Image.memory(
                          base64Decode(debug.depthPreview!),
                          width: double.infinity,
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),

                  // 2. Food Mask
                  if (debug.foodMaskPreview != null)
                    _section(
                      Icons.crop_free, const Color(0xFF81C784),
                      'Vùng thực phẩm', 'Food Segmentation',
                      ClipRRect(
                        borderRadius: BorderRadius.circular(AppRadius.sm),
                        child: Image.memory(
                          base64Decode(debug.foodMaskPreview!),
                          width: double.infinity,
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),

                  // 3. Reference Objects
                  _section(
                    Icons.straighten, const Color(0xFFFFB74D),
                    'Vật tham chiếu',
                    debug.referenceObjects != null &&
                            debug.referenceObjects!.isNotEmpty
                        ? '${debug.referenceObjects!.length} đối tượng'
                        : 'Dùng scale mặc định',
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (debug.referenceObjects != null &&
                            debug.referenceObjects!.isNotEmpty)
                          ...debug.referenceObjects!.map((obj) => Padding(
                                padding: const EdgeInsets.only(bottom: 4),
                                child: Row(
                                  children: [
                                    const Icon(Icons.circle, size: 6,
                                        color: Color(0xFFFFB74D)),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        '${obj['class']}  •  ${((obj['confidence'] as num) * 100).toStringAsFixed(0)}%',
                                        style: GoogleFonts.inter(
                                          fontSize: 13, color: Colors.white),
                                      ),
                                    ),
                                  ],
                                ),
                              )),
                        if (debug.scalePxPerCm != null)
                          _kvRow('Tỷ lệ', '${debug.scalePxPerCm} px/cm'),
                        if (debug.tableLevelCm != null)
                          _kvRow('Mặt bàn', '${debug.tableLevelCm} cm'),
                      ],
                    ),
                  ),

                  // 4. Volume Formula
                  if (debug.formula != null)
                    _section(
                      Icons.calculate, const Color(0xFFCE93D8),
                      'Công thức tính', 'Tích phân thể tích',
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(AppSpacing.md),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E1E2E),
                          borderRadius: BorderRadius.circular(AppRadius.sm),
                        ),
                        child: SelectableText(
                          debug.formula!,
                          style: GoogleFonts.firaCode(
                            color: const Color(0xFFE0E0E0),
                            fontSize: 12, height: 1.5),
                        ),
                      ),
                    ),

                  // 5. RAG Sources
                  if (debug.retrievedChunks != null &&
                      debug.retrievedChunks!.isNotEmpty)
                    _section(
                      Icons.menu_book, const Color(0xFF4FC3F7),
                      'Nguồn y khoa',
                      '${debug.retrievedChunks!.length} tài liệu',
                      Column(
                        children: debug.retrievedChunks!.asMap().entries
                            .map((entry) {
                          final i = entry.key + 1;
                          final c = entry.value;
                          return Container(
                            width: double.infinity,
                            margin: const EdgeInsets.only(bottom: AppSpacing.sm),
                            padding: const EdgeInsets.all(AppSpacing.md),
                            decoration: BoxDecoration(
                              color: AppColors.cardDarkElevated,
                              borderRadius: BorderRadius.circular(AppRadius.sm),
                              border: Border.all(
                                  color: const Color(0xFF4FC3F7).withAlpha(30)),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF4FC3F7).withAlpha(25),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text('#$i',
                                        style: GoogleFonts.inter(
                                          fontSize: 11,
                                          fontWeight: FontWeight.bold,
                                          color: const Color(0xFF4FC3F7))),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text('${c['source']}',
                                        style: GoogleFonts.inter(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                          color: Colors.white)),
                                  ),
                                ]),
                                const SizedBox(height: 6),
                                Row(children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: AppColors.primary.withAlpha(20),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text('${c['category']}',
                                        style: GoogleFonts.inter(
                                          fontSize: 11,
                                          color: AppColors.primary)),
                                  ),
                                  const Spacer(),
                                  Text(
                                    'Score: ${(c['score'] as num?)?.toStringAsFixed(2) ?? '?'}',
                                    style: GoogleFonts.inter(
                                        fontSize: 11, color: AppColors.textMuted),
                                  ),
                                ]),
                                const SizedBox(height: 6),
                                Text('${c['content_preview']}',
                                    maxLines: 3,
                                    overflow: TextOverflow.ellipsis,
                                    style: GoogleFonts.inter(
                                      fontSize: 12,
                                      color: Colors.white.withAlpha(180),
                                      height: 1.4)),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ),

                  // 6. LLM Response
                  if (debug.llmRaw != null)
                    _section(
                      Icons.smart_toy, const Color(0xFFA5D6A7),
                      'Phản hồi AI', 'Gemini 2.0 Flash',
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(AppSpacing.md),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E1E2E),
                          borderRadius: BorderRadius.circular(AppRadius.sm),
                        ),
                        child: SelectableText(
                          debug.llmRaw!,
                          style: GoogleFonts.inter(
                            color: const Color(0xFFE0E0E0),
                            fontSize: 13, height: 1.5),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _section(IconData icon, Color color, String title, String sub, Widget child) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              width: 28, height: 28,
              decoration: BoxDecoration(
                color: color.withAlpha(25),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(icon, size: 16, color: color),
            ),
            const SizedBox(width: AppSpacing.sm),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: GoogleFonts.inter(
                    fontWeight: FontWeight.w600, fontSize: 14, color: Colors.white)),
                Text(sub, style: GoogleFonts.inter(
                    fontSize: 11, color: AppColors.textMuted)),
              ],
            ),
          ]),
          const SizedBox(height: AppSpacing.sm),
          child,
        ],
      ),
    );
  }

  Widget _kvRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Row(children: [
        Text('$label: ', style: GoogleFonts.inter(
            fontSize: 12, color: AppColors.textMuted)),
        Text(value, style: GoogleFonts.inter(
            fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white)),
      ]),
    );
  }
}
