import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../viewmodels/meal_viewmodel.dart';

/// Quick food form — 1-tap selections for food type, size, and toppings.
class FoodFormScreen extends StatefulWidget {
  const FoodFormScreen({super.key});

  @override
  State<FoodFormScreen> createState() => _FoodFormScreenState();
}

class _FoodFormScreenState extends State<FoodFormScreen> {
  final _formKey = GlobalKey<FormState>();
  String? _dishType;
  String? _size;
  final List<String> _toppings = [];

  static const _dishTypes = [
    'Cơm',
    'Phở',
    'Bún',
    'Cháo',
    'Bánh mì',
    'Xôi',
    'Miến',
    'Mì',
    'Khác',
  ];

  static const _sizes = ['Nhỏ', 'Vừa', 'Lớn'];

  static const _toppingOptions = [
    'Thêm rau',
    'Thêm thịt',
    'Nước sốt',
    'Trứng',
    'Đồ chua',
    'Tương ớt',
  ];

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<MealViewModel>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Thông tin món ăn'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/camera'),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Image preview
                if (vm.selectedImage != null)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.file(
                      vm.selectedImage!,
                      height: 200,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),
                  ),
                const SizedBox(height: 24),

                // Dish type
                Text('Loại món', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _dishTypes.map((type) {
                    final selected = _dishType == type;
                    return ChoiceChip(
                      label: Text(type),
                      selected: selected,
                      onSelected: (_) {
                        setState(() => _dishType = type);
                        vm.setFoodType(type);
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),

                // Size
                Text('Khẩu phần', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: _sizes.map((size) {
                    final selected = _size == size;
                    return ChoiceChip(
                      label: Text(size),
                      selected: selected,
                      onSelected: (_) {
                        setState(() => _size = size);
                        vm.setSize(size);
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),

                // Toppings
                Text('Thêm (tùy chọn)',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _toppingOptions.map((t) {
                    final selected = _toppings.contains(t);
                    return FilterChip(
                      label: Text(t),
                      selected: selected,
                      onSelected: (val) {
                        setState(() {
                          val ? _toppings.add(t) : _toppings.remove(t);
                        });
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 32),

                // Analyze button
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: FilledButton.icon(
                    onPressed: vm.isLoading
                        ? null
                        : () async {
                            await vm.analyze();
                            if (context.mounted && vm.result != null) {
                              context.go('/result');
                            }
                          },
                    icon: vm.isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.analytics),
                    label: Text(
                      vm.isLoading ? 'Đang phân tích...' : 'Phân tích GL',
                      style: const TextStyle(fontSize: 18),
                    ),
                  ),
                ),

                // Error display
                if (vm.error != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.red),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            vm.error!,
                            style: const TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
