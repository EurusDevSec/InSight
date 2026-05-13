import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/constants.dart';

/// Disclaimer banner — always visible on result screens.
class DisclaimerBanner extends StatelessWidget {
  const DisclaimerBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.accent.withAlpha(15),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: AppColors.accent.withAlpha(40)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.warning_amber, color: AppColors.accent, size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              '⚠️ Kết quả chỉ mang tính tham khảo. '
              'Không thay thế chỉ định của bác sĩ. '
              'Luôn tham khảo ý kiến chuyên gia y tế trước khi điều chỉnh liều insulin.',
              style: GoogleFonts.inter(fontSize: 12, color: AppColors.accent),
            ),
          ),
        ],
      ),
    );
  }
}
