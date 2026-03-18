import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../viewmodels/panic_viewmodel.dart';
import '../widgets/gl_indicator.dart';
import '../widgets/disclaimer_banner.dart';

/// Panic Mode — 1-tap instant GL estimation from cached data.
class PanicScreen extends StatelessWidget {
  const PanicScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<PanicViewModel>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('⚡ Ước lượng nhanh'),
        backgroundColor: Colors.orange.shade50,
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
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Chọn món đang ăn',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Chạm 1 lần để ước lượng GL ngay',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.5,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
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
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          GlIndicator(
            glycemicLoad: dish['glycemic_load'] as double,
            glLevel: dish['gl_level'] as String,
          ),
          const SizedBox(height: 24),
          Text(
            dish['name'] as String,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _stat('Carb', '${(dish['carbs_g'] as double).toStringAsFixed(0)}g'),
                  _stat('GL', (dish['glycemic_load'] as double).toStringAsFixed(0)),
                  _stat('Mức', (dish['gl_level'] as String).toUpperCase()),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              '⏱ Kết quả dựa trên trung bình thống kê.\n'
              'Để chính xác hơn, hãy dùng chế độ Chụp ảnh phân tích.',
              style: TextStyle(fontSize: 13),
            ),
          ),
          const SizedBox(height: 16),
          const DisclaimerBanner(),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => vm.reset(),
                  child: const Text('Chọn món khác'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton(
                  onPressed: () {
                    vm.reset();
                    context.go('/');
                  },
                  child: const Text('Xong'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _stat(String label, String value) {
    return Column(
      children: [
        Text(value,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(color: Colors.grey)),
      ],
    );
  }
}

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
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                name,
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              Text(
                '~${carbsG.toStringAsFixed(0)}g Carb',
                style: TextStyle(color: Colors.grey[600], fontSize: 13),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
