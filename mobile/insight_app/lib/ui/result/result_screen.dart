import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

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
              const SizedBox(height: 24),

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
                        '${(result.confidence * 100).toStringAsFixed(0)}%',
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

              // Warnings
              if (result.warnings.isNotEmpty) ...[
                const SizedBox(height: 16),
                ...result.warnings.map(
                  (w) => Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.orange.shade200),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning_amber, color: Colors.orange, size: 20),
                        const SizedBox(width: 8),
                        Expanded(child: Text(w)),
                      ],
                    ),
                  ),
                ),
              ],

              const SizedBox(height: 16),
              const DisclaimerBanner(),
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
