import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../data/models/patient_context.dart';
import '../../ui/widgets/insight_card.dart';
import '../../viewmodels/meal_viewmodel.dart';

/// Patient Profile — diabetes parameters for personalized advice.
class PatientProfileScreen extends StatefulWidget {
  const PatientProfileScreen({super.key});

  @override
  State<PatientProfileScreen> createState() => _PatientProfileScreenState();
}

class _PatientProfileScreenState extends State<PatientProfileScreen> {
  final _glucoseController = TextEditingController();
  final _icrController = TextEditingController();
  final _cfController = TextEditingController();
  final _targetController = TextEditingController();
  String? _diabetesType;

  static const _diabetesTypes = [
    'Type 1',
    'Type 2',
    'Tiền đái tháo đường',
    'Thai kỳ',
    'Không xác định',
  ];

  @override
  void initState() {
    super.initState();
    final vm = context.read<MealViewModel>();
    final ctx = vm.patientContext;
    _glucoseController.text = ctx.glucoseLevel?.toString() ?? '';
    _icrController.text = ctx.insulinCarbRatio?.toString() ?? '';
    _cfController.text = ctx.correctionFactor?.toString() ?? '';
    _targetController.text = ctx.targetGlucose?.toString() ?? '';
    _diabetesType = ctx.medicationType;
  }

  @override
  void dispose() {
    _glucoseController.dispose();
    _icrController.dispose();
    _cfController.dispose();
    _targetController.dispose();
    super.dispose();
  }

  void _save() {
    final vm = context.read<MealViewModel>();
    vm.updatePatientContext(PatientContext(
      glucoseLevel: double.tryParse(_glucoseController.text),
      insulinCarbRatio: double.tryParse(_icrController.text),
      correctionFactor: double.tryParse(_cfController.text),
      targetGlucose: double.tryParse(_targetController.text),
      medicationType: _diabetesType,
    ));

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: AppColors.success, size: 20),
            const SizedBox(width: 8),
            Text('Đã lưu thông tin', style: GoogleFonts.inter()),
          ],
        ),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.sm),
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hồ sơ bệnh nhân')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              InsightCard(
                gradientColors: const [AppColors.info, AppColors.primary],
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: Colors.white.withAlpha(30),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.person, color: Colors.white, size: 28),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Thông tin cá nhân hóa',
                            style: GoogleFonts.inter(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Giúp AI đưa ra tư vấn chính xác hơn',
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              color: Colors.white.withAlpha(180),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Diabetes Type ───
              _sectionTitle('Loại đái tháo đường'),
              const SizedBox(height: AppSpacing.sm),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _diabetesTypes.map((type) {
                  final selected = _diabetesType == type;
                  return ChoiceChip(
                    label: Text(type),
                    selected: selected,
                    onSelected: (_) {
                      setState(() => _diabetesType = selected ? null : type);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Glucose Level ───
              _sectionTitle('Đường huyết lúc đói (mg/dL)'),
              const SizedBox(height: AppSpacing.sm),
              _buildInput(
                controller: _glucoseController,
                hint: '120',
                icon: Icons.bloodtype,
                suffix: 'mg/dL',
                helperText: 'Bình thường: 70–100 mg/dL',
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── ICR ───
              _sectionTitle('Tỷ lệ Insulin:Carb (ICR)'),
              const SizedBox(height: AppSpacing.sm),
              _buildInput(
                controller: _icrController,
                hint: '10',
                icon: Icons.calculate,
                suffix: 'g/unit',
                helperText: '1 đơn vị insulin cover bao nhiêu g carb',
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Correction Factor ───
              _sectionTitle('Hệ số điều chỉnh (CF)'),
              const SizedBox(height: AppSpacing.sm),
              _buildInput(
                controller: _cfController,
                hint: '50',
                icon: Icons.tune,
                suffix: 'mg/dL/unit',
                helperText: '1 đơn vị insulin giảm bao nhiêu mg/dL',
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Target Glucose ───
              _sectionTitle('Đường huyết mục tiêu'),
              const SizedBox(height: AppSpacing.sm),
              _buildInput(
                controller: _targetController,
                hint: '100',
                icon: Icons.gps_fixed,
                suffix: 'mg/dL',
                helperText: 'Mục tiêu đường huyết sau ăn',
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Disclaimer ───
              Container(
                padding: const EdgeInsets.all(AppSpacing.md),
                decoration: BoxDecoration(
                  color: AppColors.accent.withAlpha(15),
                  borderRadius: BorderRadius.circular(AppRadius.md),
                  border: Border.all(color: AppColors.accent.withAlpha(40)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lock, color: AppColors.accent, size: 18),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: Text(
                        'Dữ liệu chỉ lưu trên thiết bị. Không gửi lên server.',
                        style: GoogleFonts.inter(fontSize: 12, color: AppColors.accent),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // ─── Save Button ───
              SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton.icon(
                  onPressed: _save,
                  icon: const Icon(Icons.save),
                  label: Text('Lưu thông tin',
                      style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
            ],
          ),
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Text(
      text,
      style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
    );
  }

  Widget _buildInput({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    required String suffix,
    String? helperText,
  }) {
    return TextField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: Icon(icon),
        suffixText: suffix,
        helperText: helperText,
        helperStyle: GoogleFonts.inter(fontSize: 12, color: AppColors.textMuted),
      ),
    );
  }
}
