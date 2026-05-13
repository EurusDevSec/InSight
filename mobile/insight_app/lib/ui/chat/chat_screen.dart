import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../config/constants.dart';
import '../../viewmodels/chat_viewmodel.dart';
import '../../viewmodels/meal_viewmodel.dart';
import 'chat_bubble.dart';

/// Chat screen — AI assistant for diabetes nutrition advice.
class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    // Initialize welcome message if empty
    final chatVm = context.read<ChatViewModel>();
    if (chatVm.messages.isEmpty) {
      chatVm.clearChat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    final chatVm = context.read<ChatViewModel>();
    final mealVm = context.read<MealViewModel>();

    chatVm.sendMessage(
      text,
      patientContext: {
        'glucose_level': mealVm.patientContext.glucoseLevel,
        'diabetes_type': mealVm.patientContext.medicationType,
        'insulin_carb_ratio': mealVm.patientContext.insulinCarbRatio,
        'correction_factor': mealVm.patientContext.correctionFactor,
        'target_glucose': mealVm.patientContext.targetGlucose,
      },
    );

    _controller.clear();
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatVm = context.watch<ChatViewModel>();

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
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
            const SizedBox(width: 10),
            Text('InSight AI',
                style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Cuộc trò chuyện mới',
            onPressed: () => chatVm.clearChat(),
          ),
        ],
      ),
      body: Column(
        children: [
          // ─── Messages ───
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(AppSpacing.md),
              itemCount: chatVm.messages.length + (chatVm.isTyping ? 1 : 0),
              itemBuilder: (context, i) {
                // Typing indicator
                if (i == chatVm.messages.length && chatVm.isTyping) {
                  return _TypingIndicator();
                }

                final msg = chatVm.messages[i];
                final time =
                    '${msg.timestamp.hour.toString().padLeft(2, '0')}:${msg.timestamp.minute.toString().padLeft(2, '0')}';

                return ChatBubble(
                  text: msg.text,
                  isUser: msg.isUser,
                  sources: msg.sources,
                  time: time,
                );
              },
            ),
          ),

          // ─── Error Banner ───
          if (chatVm.error != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.md, vertical: 8),
              color: AppColors.emergency.withAlpha(20),
              child: Text(
                chatVm.error!,
                style: GoogleFonts.inter(
                    fontSize: 12, color: AppColors.emergency),
                textAlign: TextAlign.center,
              ),
            ),

          // ─── Disclaimer ───
          Container(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 6),
            child: Text(
              'AI có thể sai. Luôn tham khảo ý kiến bác sĩ.',
              style: GoogleFonts.inter(
                  fontSize: 10, color: AppColors.textMuted.withAlpha(120)),
              textAlign: TextAlign.center,
            ),
          ),

          // ─── Quick Suggestions ───
          if (chatVm.messages.length <= 1)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
              child: Wrap(
                spacing: 8,
                runSpacing: 6,
                children: [
                  _SuggestionChip(
                    text: 'Phở bò GL bao nhiêu?',
                    onTap: () {
                      _controller.text = 'Phở bò có GL bao nhiêu?';
                      _sendMessage();
                    },
                  ),
                  _SuggestionChip(
                    text: 'Cách tính insulin',
                    onTap: () {
                      _controller.text = 'Cách tính liều insulin cho bữa ăn?';
                      _sendMessage();
                    },
                  ),
                  _SuggestionChip(
                    text: 'Món nào GL thấp?',
                    onTap: () {
                      _controller.text = 'Món ăn Việt nào có GL thấp?';
                      _sendMessage();
                    },
                  ),
                ],
              ),
            ),

          // ─── Input Bar ───
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).brightness == Brightness.dark
                      ? Colors.white.withAlpha(12)
                      : Colors.black.withAlpha(8),
                ),
              ),
            ),
            child: SafeArea(
              top: false,
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                      decoration: InputDecoration(
                        hintText: 'Nhập câu hỏi...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(AppRadius.pill),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor:
                            Theme.of(context).brightness == Brightness.dark
                                ? AppColors.cardDark
                                : AppColors.cardLight,
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [AppColors.primary, AppColors.primaryDark],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      onPressed: chatVm.isTyping ? null : _sendMessage,
                      icon: Icon(
                        chatVm.isTyping ? Icons.hourglass_top : Icons.send,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Typing indicator (3 dots animation).
class _TypingIndicator extends StatefulWidget {
  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Row(
        children: [
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
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).brightness == Brightness.dark
                  ? AppColors.cardDark
                  : AppColors.cardLight,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(AppRadius.lg),
                topRight: Radius.circular(AppRadius.lg),
                bottomRight: Radius.circular(AppRadius.lg),
                bottomLeft: Radius.circular(4),
              ),
            ),
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, _) {
                final dots = '.' * ((_controller.value * 3).floor() % 3 + 1);
                return Text(
                  'Đang suy nghĩ$dots',
                  style: GoogleFonts.inter(
                      fontSize: 13, color: AppColors.textMuted),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _SuggestionChip extends StatelessWidget {
  final String text;
  final VoidCallback onTap;
  const _SuggestionChip({required this.text, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      label: Text(text, style: GoogleFonts.inter(fontSize: 12)),
      onPressed: onTap,
      backgroundColor: AppColors.primary.withAlpha(15),
      side: BorderSide(color: AppColors.primary.withAlpha(40)),
    );
  }
}
