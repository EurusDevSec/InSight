import 'package:flutter/material.dart';

/// Disclaimer banner — always visible on result screens.
class DisclaimerBanner extends StatelessWidget {
  const DisclaimerBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber.shade200),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber, color: Colors.orange, size: 20),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              '⚠️ Kết quả chỉ mang tính tham khảo. '
              'Không thay thế chỉ định của bác sĩ. '
              'Luôn tham khảo ý kiến chuyên gia y tế trước khi điều chỉnh liều insulin.',
              style: TextStyle(fontSize: 12, color: Colors.brown),
            ),
          ),
        ],
      ),
    );
  }
}
