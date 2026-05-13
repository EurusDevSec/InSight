import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/constants.dart';

/// Chat bubble widget — user or bot message.
class ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;
  final List<String>? sources;
  final String time;

  const ChatBubble({
    super.key,
    required this.text,
    required this.isUser,
    this.sources,
    required this.time,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.only(
        left: isUser ? 48 : 0,
        right: isUser ? 0 : 48,
        bottom: AppSpacing.sm,
      ),
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          // Avatar + bubble
          Row(
            mainAxisAlignment:
                isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (!isUser) ...[
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppColors.primary, AppColors.primaryDark],
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.smart_toy, color: Colors.white, size: 18),
                ),
                const SizedBox(width: 8),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.md, vertical: 12),
                  decoration: BoxDecoration(
                    color: isUser
                        ? AppColors.primary
                        : (isDark ? AppColors.cardDark : AppColors.cardLight),
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(AppRadius.lg),
                      topRight: const Radius.circular(AppRadius.lg),
                      bottomLeft: Radius.circular(isUser ? AppRadius.lg : 4),
                      bottomRight: Radius.circular(isUser ? 4 : AppRadius.lg),
                    ),
                    border: isUser
                        ? null
                        : Border.all(
                            color: isDark
                                ? Colors.white.withAlpha(15)
                                : Colors.black.withAlpha(10)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        text,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: isUser ? Colors.white : null,
                          height: 1.5,
                        ),
                      ),
                      // Source citations
                      if (sources != null && sources!.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: sources!
                              .map((s) => Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: AppColors.info.withAlpha(20),
                                      borderRadius:
                                          BorderRadius.circular(AppRadius.pill),
                                    ),
                                    child: Text(
                                      '📄 $s',
                                      style: GoogleFonts.inter(
                                          fontSize: 10, color: AppColors.info),
                                    ),
                                  ))
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
          // Timestamp
          Padding(
            padding: EdgeInsets.only(
              top: 4,
              left: isUser ? 0 : 40,
            ),
            child: Text(
              time,
              style: GoogleFonts.inter(
                  fontSize: 10, color: AppColors.textMuted.withAlpha(120)),
            ),
          ),
        ],
      ),
    );
  }
}
