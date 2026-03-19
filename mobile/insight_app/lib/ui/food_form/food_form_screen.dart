import 'dart:typed_data';

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
  final _customFoodController = TextEditingController();

  @override
  void dispose() {
    _customFoodController.dispose();
    super.dispose();
  }

  static const _dishTypes = [
    // Cơm
    'Cơm tấm',
    'Cơm trắng',
    'Cơm gà',
    'Cơm chiên',
    'Cơm bình dân',
    // Phở / Bún / Mì
    'Phở bò',
    'Phở gà',
    'Bún bò',
    'Bún chả',
    'Bún riêu',
    'Bún mắm',
    'Bún thịt nướng',
    'Hủ tiếu',
    'Mì xào',
    'Mì Quảng',
    'Cao lầu',
    'Bánh canh',
    // Bánh / Khác
    'Bánh mì',
    'Bánh cuốn',
    'Bánh xèo',
    'Gỏi cuốn',
    'Xôi',
    'Cháo',
    'Bột chiên',
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
                // Image preview — uses Image.memory for web+mobile compatibility
                if (vm.selectedImage != null)
                  FutureBuilder<Uint8List>(
                    future: vm.selectedImage!.readAsBytes(),
                    builder: (context, snapshot) {
                      if (!snapshot.hasData) {
                        return const SizedBox(
                          height: 200,
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      return ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.memory(
                          snapshot.data!,
                          height: 200,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      );
                    },
                  ),
                // Top-down photo guidance
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Row(
                    children: [
                      Icon(Icons.camera_alt, size: 16, color: Colors.blue[700]),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Chụp từ trên xuống (top-down) cho kết quả chính xác nhất',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.blue[700],
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Dish type (optional — auto-detected from image if not selected)
                Text('Loại món (tùy chọn)', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                Text(
                  'Bỏ qua để hệ thống tự nhận diện từ ảnh',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
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
                        setState(() {
                          // Toggle: tap again to deselect → auto-detect
                          if (_dishType == type) {
                            _dishType = null;
                            vm.setFoodType(null);
                            vm.setCustomFoodName(null);
                          } else {
                            _dishType = type;
                            vm.setFoodType(type);
                            if (type != 'Khác') {
                              vm.setCustomFoodName(null);
                              _customFoodController.clear();
                            }
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
                // Custom food name input when "Khác" is selected
                if (_dishType == 'Khác') ...[
                  const SizedBox(height: 12),
                  TextField(
                    controller: _customFoodController,
                    decoration: InputDecoration(
                      labelText: 'Tên món ăn',
                      hintText: 'VD: Bún đậu mắm tôm, Bánh tráng trộn...',
                      border: const OutlineInputBorder(),
                      prefixIcon: const Icon(Icons.restaurant),
                      helperText: 'Nhập tên món để AI tư vấn chính xác hơn',
                      helperStyle: TextStyle(color: Colors.grey[600]),
                    ),
                    onChanged: (value) => vm.setCustomFoodName(
                      value.trim().isEmpty ? null : value.trim(),
                    ),
                    textCapitalization: TextCapitalization.sentences,
                  ),
                ],
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
                const SizedBox(height: 24),

                // Developer Mode toggle
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Developer Mode'),
                  subtitle: const Text('Hiển thị depth map, formula, RAG chunks'),
                  secondary: Icon(
                    Icons.developer_mode,
                    color: vm.debugMode ? Colors.greenAccent : Colors.grey,
                  ),
                  value: vm.debugMode,
                  onChanged: (_) => vm.toggleDebugMode(),
                ),

                const SizedBox(height: 16),

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
