import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../data/models/meal_analysis.dart';
import '../../viewmodels/meal_viewmodel.dart';
import '../widgets/gl_indicator.dart';
import '../widgets/disclaimer_banner.dart';

/// Result screen showing GL analysis — large numbers, patient-friendly.
class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<MealViewModel>();
    final result = vm.result;

    if (result == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Kết quả')),
        body: const Center(child: Text('Chưa có kết quả phân tích')),
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
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // GL Indicator (big number)
              GlIndicator(
                glycemicLoad: result.glycemicLoad,
                glLevel: result.glLevel,
              ),
              const SizedBox(height: 24),

              // Food name
              Text(
                result.foodName,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 16),

              // Warnings — shown prominently ABOVE nutrition details
              if (result.warnings.isNotEmpty) ...[
                ...result.warnings.map((w) {
                  final isCritical = w.contains('CẢNH BÁO');
                  final bgColor = isCritical ? Colors.red.shade50 : Colors.orange.shade50;
                  final borderColor = isCritical ? Colors.red.shade300 : Colors.orange.shade200;
                  final iconColor = isCritical ? Colors.red : Colors.orange;
                  final icon = isCritical ? Icons.dangerous : Icons.warning_amber;
                  return Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: bgColor,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: borderColor),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(icon, color: iconColor, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            w,
                            style: TextStyle(
                              color: isCritical ? Colors.red.shade900 : null,
                              fontWeight: isCritical ? FontWeight.bold : null,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 8),
              ],

              // Nutrition details card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _buildRow('Thể tích', '${result.volumeMl.toStringAsFixed(1)} mL'),
                      const Divider(),
                      _buildRow('Khối lượng', '${result.weightG.toStringAsFixed(1)} g'),
                      const Divider(),
                      _buildRow('Carbohydrate', '${result.carbsG.toStringAsFixed(1)} g'),
                      const Divider(),
                      _buildRow(
                        'Độ tin cậy',
                        result.confidence <= 0.5
                            ? '⚠️ Thấp'
                            : '${(result.confidence * 100).toStringAsFixed(0)}%',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Insulin advice
              if (vm.advice != null || vm.insulinSuggestion != null)
                Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.medical_information,
                                color: Colors.blue.shade700),
                            const SizedBox(width: 8),
                            Text(
                              'Tư vấn Insulin',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue.shade700,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                        if (vm.insulinSuggestion != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            vm.insulinSuggestion!,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                        if (vm.advice != null) ...[
                          const SizedBox(height: 8),
                          Text(vm.advice!),
                        ],
                      ],
                    ),
                  ),
                ),

              const SizedBox(height: 16),
              const DisclaimerBanner(),
              const SizedBox(height: 16),

              // Developer Mode toggle + panel
              if (result.debug != null) _DeveloperModePanel(debug: result.debug!),

              const SizedBox(height: 24),

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
                  label: const Text('Phân tích món mới'),
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
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

/// Collapsible "Under the Hood" developer panel showing pipeline internals.
class _DeveloperModePanel extends StatelessWidget {
  final DebugData debug;
  const _DeveloperModePanel({required this.debug});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.grey.shade900,
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          leading: Icon(Icons.developer_mode, color: Colors.greenAccent.shade400),
          title: Text(
            'Under the Hood',
            style: TextStyle(
              color: Colors.greenAccent.shade400,
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
            ),
          ),
          subtitle: Text(
            'Khám phá hệ thống',
            style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
          ),
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 1. Depth Map
                  if (debug.depthPreview != null) ...[
                    _sectionTitle('1. Depth Map (Depth Anything V2)'),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.memory(
                        base64Decode(debug.depthPreview!),
                        width: double.infinity,
                        fit: BoxFit.contain,
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // 2. Food Mask
                  if (debug.foodMaskPreview != null) ...[
                    _sectionTitle('2. Food Segmentation Mask'),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.memory(
                        base64Decode(debug.foodMaskPreview!),
                        width: double.infinity,
                        fit: BoxFit.contain,
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // 3. Reference Objects
                  if (debug.referenceObjects != null &&
                      debug.referenceObjects!.isNotEmpty) ...[
                    _sectionTitle('3. Reference Objects Detected'),
                    const SizedBox(height: 8),
                    ...debug.referenceObjects!.map(
                      (obj) => _codeBlock(
                        '${obj['class']}  conf=${obj['confidence']}  '
                        'bbox=${obj['bbox']}',
                      ),
                    ),
                    if (debug.scalePxPerCm != null)
                      _codeBlock('Scale: ${debug.scalePxPerCm} px/cm'),
                    if (debug.tableLevelCm != null)
                      _codeBlock('Table level: ${debug.tableLevelCm} cm'),
                    const SizedBox(height: 16),
                  ] else ...[
                    _sectionTitle('3. Reference Objects'),
                    const SizedBox(height: 8),
                    _codeBlock('None detected — using fallback scale'),
                    if (debug.scalePxPerCm != null)
                      _codeBlock('Fallback scale: ${debug.scalePxPerCm} px/cm'),
                    const SizedBox(height: 16),
                  ],

                  // 4. Volume Formula
                  if (debug.formula != null) ...[
                    _sectionTitle('4. Volume Formula'),
                    const SizedBox(height: 8),
                    _codeBlock(debug.formula!),
                    const SizedBox(height: 16),
                  ],

                  // 5. RAG Hybrid Search
                  if (debug.retrievedChunks != null &&
                      debug.retrievedChunks!.isNotEmpty) ...[
                    _sectionTitle('5. RAG Hybrid Search (BM25 + Vector)'),
                    const SizedBox(height: 8),
                    ...debug.retrievedChunks!.asMap().entries.map(
                      (entry) {
                        final i = entry.key + 1;
                        final chunk = entry.value;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _codeBlock(
                            '[$i] ${chunk['source']}\n'
                            '    Category: ${chunk['category']}\n'
                            '    Score: ${chunk['score']}\n'
                            '    ${chunk['content_preview']}',
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                  ],

                  // 6. LLM Raw Response
                  if (debug.llmRaw != null) ...[
                    _sectionTitle('6. LLM Raw Response (Gemini)'),
                    const SizedBox(height: 8),
                    _codeBlock(debug.llmRaw!),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Text(
      text,
      style: TextStyle(
        color: Colors.greenAccent.shade400,
        fontWeight: FontWeight.bold,
        fontSize: 14,
        fontFamily: 'monospace',
      ),
    );
  }

  Widget _codeBlock(String text) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.grey.shade700),
      ),
      child: SelectableText(
        text,
        style: const TextStyle(
          color: Colors.white70,
          fontSize: 12,
          fontFamily: 'monospace',
          height: 1.4,
        ),
      ),
    );
  }
}
