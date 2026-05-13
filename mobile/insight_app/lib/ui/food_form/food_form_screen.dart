import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../ui/widgets/food_emoji_icon.dart';
import '../../viewmodels/meal_viewmodel.dart';

/// Quick food form — categorized tabs + glucose input.
class FoodFormScreen extends StatefulWidget {
  const FoodFormScreen({super.key});

  @override
  State<FoodFormScreen> createState() => _FoodFormScreenState();
}

class _FoodFormScreenState extends State<FoodFormScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  String? _dishType;
  String? _size;
  final List<String> _toppings = [];
  final _customFoodController = TextEditingController();
  final _glucoseController = TextEditingController();
  late TabController _tabController;

  static const _categories = {
    'Cơm': ['Cơm tấm', 'Cơm trắng', 'Cơm gà', 'Cơm chiên', 'Cơm bình dân'],
    'Phở/Bún/Mì': [
      'Phở bò', 'Phở gà', 'Bún bò', 'Bún chả', 'Bún riêu',
      'Bún mắm', 'Bún thịt nướng', 'Hủ tiếu', 'Mì xào',
      'Mì Quảng', 'Cao lầu', 'Bánh canh',
    ],
    'Khác': [
      'Bánh mì', 'Bánh cuốn', 'Bánh xèo', 'Gỏi cuốn',
      'Xôi', 'Cháo', 'Bột chiên', 'Khác',
    ],
  };

  static const _sizes = ['Nhỏ', 'Vừa', 'Lớn'];
  static const _toppingOptions = [
    'Thêm rau', 'Thêm thịt', 'Nước sốt', 'Trứng', 'Đồ chua', 'Tương ớt',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _categories.length, vsync: this);
  }

  @override
  void dispose() {
    _customFoodController.dispose();
    _glucoseController.dispose();
    _tabController.dispose();
    super.dispose();
  }

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
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ─── Progress indicator ───
                _buildProgress(),
                const SizedBox(height: AppSpacing.md),

                // ─── Image preview ───
                if (vm.selectedImage != null)
                  FutureBuilder<Uint8List>(
                    future: vm.selectedImage!.readAsBytes(),
                    builder: (context, snapshot) {
                      if (!snapshot.hasData) {
                        return Container(
                          height: 180,
                          decoration: BoxDecoration(
                            color: AppColors.cardDark,
                            borderRadius: BorderRadius.circular(AppRadius.md),
                          ),
                          child: const Center(child: CircularProgressIndicator()),
                        );
                      }
                      return ClipRRect(
                        borderRadius: BorderRadius.circular(AppRadius.md),
                        child: Image.memory(
                          snapshot.data!,
                          height: 180,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      );
                    },
                  ),
                const SizedBox(height: AppSpacing.md),

                // ─── Dish type with tabs ───
                Text(
                  'Loại món (tùy chọn)',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Bỏ qua để hệ thống tự nhận diện từ ảnh',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // Tab bar
                Container(
                  decoration: BoxDecoration(
                    color: AppColors.cardDarkElevated,
                    borderRadius: BorderRadius.circular(AppRadius.sm),
                  ),
                  child: TabBar(
                    controller: _tabController,
                    labelColor: AppColors.primary,
                    unselectedLabelColor: AppColors.textMuted,
                    indicatorColor: AppColors.primary,
                    indicatorSize: TabBarIndicatorSize.tab,
                    dividerColor: Colors.transparent,
                    labelStyle: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                    tabs: _categories.keys
                        .map((cat) => Tab(text: cat))
                        .toList(),
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // Tab content
                SizedBox(
                  height: 130,
                  child: TabBarView(
                    controller: _tabController,
                    children: _categories.values.map((dishes) {
                      return SingleChildScrollView(
                        child: Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: dishes.map((type) {
                            final selected = _dishType == type;
                            return ChoiceChip(
                              avatar: FoodEmojiIcon(foodName: type, size: 16),
                              label: Text(type),
                              selected: selected,
                              onSelected: (_) {
                                setState(() {
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
                      );
                    }).toList(),
                  ),
                ),

                // Custom food name
                if (_dishType == 'Khác') ...[
                  const SizedBox(height: AppSpacing.md),
                  TextField(
                    controller: _customFoodController,
                    decoration: InputDecoration(
                      labelText: 'Tên món ăn',
                      hintText: 'VD: Bún đậu mắm tôm...',
                      prefixIcon: const Icon(Icons.restaurant),
                    ),
                    onChanged: (value) => vm.setCustomFoodName(
                      value.trim().isEmpty ? null : value.trim(),
                    ),
                    textCapitalization: TextCapitalization.sentences,
                  ),
                ],
                const SizedBox(height: AppSpacing.lg),

                // ─── Size ───
                Text('Khẩu phần',
                    style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: AppSpacing.sm),
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
                const SizedBox(height: AppSpacing.lg),

                // ─── Toppings ───
                Text('Thêm (tùy chọn)',
                    style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: AppSpacing.sm),
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
                const SizedBox(height: AppSpacing.lg),

                // ─── Glucose input ───
                Text('Đường huyết hiện tại (tùy chọn)',
                    style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: AppSpacing.sm),
                TextField(
                  controller: _glucoseController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'mg/dL',
                    hintText: 'VD: 120',
                    prefixIcon: const Icon(Icons.bloodtype),
                    suffixText: 'mg/dL',
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),

                // ─── Developer Mode ───
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text('Developer Mode', style: GoogleFonts.inter()),
                  subtitle: Text(
                    'Hiển thị depth map, formula, RAG chunks',
                    style: GoogleFonts.inter(fontSize: 12, color: AppColors.textMuted),
                  ),
                  secondary: Icon(
                    Icons.developer_mode,
                    color: vm.debugMode ? Colors.greenAccent : AppColors.textMuted,
                  ),
                  value: vm.debugMode,
                  onChanged: (_) => vm.toggleDebugMode(),
                ),
                const SizedBox(height: AppSpacing.md),

                // ─── Analyze button ───
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
                      style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                  ),
                ),

                // Error display
                if (vm.error != null) ...[
                  const SizedBox(height: AppSpacing.md),
                  Container(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    decoration: BoxDecoration(
                      color: AppColors.emergency.withAlpha(20),
                      borderRadius: BorderRadius.circular(AppRadius.md),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: AppColors.emergency),
                        const SizedBox(width: AppSpacing.sm),
                        Expanded(
                          child: Text(
                            vm.error!,
                            style: GoogleFonts.inter(color: AppColors.emergency, fontSize: 13),
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

  Widget _buildProgress() {
    return Row(
      children: [
        _progressDot(1, 'Chụp', true),
        Expanded(child: Container(height: 2, color: AppColors.primary)),
        _progressDot(2, 'Chọn', true),
        Expanded(
          child: Container(height: 2, color: AppColors.textMuted.withAlpha(40)),
        ),
        _progressDot(3, 'Kết quả', false),
      ],
    );
  }

  Widget _progressDot(int step, String label, bool active) {
    return Column(
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            color: active ? AppColors.primary : AppColors.textMuted.withAlpha(40),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            '$step',
            style: GoogleFonts.inter(
              color: active ? Colors.white : AppColors.textMuted,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            color: active ? AppColors.primary : AppColors.textMuted,
          ),
        ),
      ],
    );
  }
}
