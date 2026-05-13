import 'package:flutter/foundation.dart';
import '../data/services/api_service.dart';

/// Chat message model.
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final List<String>? sources;

  ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
    this.sources,
  }) : timestamp = timestamp ?? DateTime.now();
}

/// ChatViewModel — manages AI chat conversation state.
class ChatViewModel extends ChangeNotifier {
  final ApiService _api;

  ChatViewModel(this._api);

  final List<ChatMessage> messages = [];
  bool isTyping = false;
  String? error;

  static const int _maxMessages = 40; // rate limit per session

  /// Send a user message and get AI response.
  Future<void> sendMessage(String text, {Map<String, dynamic>? patientContext}) async {
    if (text.trim().isEmpty) return;
    if (messages.where((m) => m.isUser).length >= _maxMessages) {
      error = 'Đã đạt giới hạn $_maxMessages tin nhắn. Vui lòng bắt đầu phiên mới.';
      notifyListeners();
      return;
    }

    // Add user message
    messages.add(ChatMessage(text: text.trim(), isUser: true));
    isTyping = true;
    error = null;
    notifyListeners();

    try {
      // Build history for context
      final history = messages
          .take(20) // last 20 messages for context window
          .map((m) => {
                'role': m.isUser ? 'user' : 'assistant',
                'content': m.text,
              })
          .toList();

      final response = await _api.chat(
        message: text.trim(),
        history: history,
        patientContext: patientContext,
      );

      final botText = response['advice'] as String? ??
          response['response'] as String? ??
          'Xin lỗi, tôi không thể trả lời lúc này.';

      final sources = (response['sources'] as List<dynamic>?)
          ?.map((s) => s['source']?.toString() ?? '')
          .where((s) => s.isNotEmpty)
          .toList();

      messages.add(ChatMessage(
        text: botText,
        isUser: false,
        sources: sources,
      ));
    } catch (e) {
      // Fallback: offline response
      messages.add(ChatMessage(
        text: _getOfflineResponse(text),
        isUser: false,
      ));
    } finally {
      isTyping = false;
      notifyListeners();
    }
  }

  /// Clear conversation.
  void clearChat() {
    messages.clear();
    error = null;
    // Add welcome message
    messages.add(ChatMessage(
      text: 'Xin chào! 👋 Tôi là trợ lý dinh dưỡng InSight.\n\n'
          'Tôi có thể giúp bạn:\n'
          '• Tư vấn về GL của các món ăn\n'
          '• Giải thích về insulin và carb\n'
          '• Hướng dẫn quản lý đường huyết\n\n'
          'Hãy hỏi tôi bất cứ điều gì! 😊',
      isUser: false,
    ));
    notifyListeners();
  }

  /// Basic offline responses when API unavailable.
  String _getOfflineResponse(String query) {
    final q = query.toLowerCase();

    if (q.contains('gl') || q.contains('glycemic')) {
      return 'Glycemic Load (GL) đo lường tác động thực tế của thực phẩm lên đường huyết.\n\n'
          '• GL < 10: Thấp ✅\n'
          '• GL 10-20: Trung bình ⚠️\n'
          '• GL > 20: Cao 🔴\n\n'
          '⚠️ Đây là thông tin offline. Kết nối mạng để nhận tư vấn chi tiết hơn.\n\n'
          '_Kết quả chỉ mang tính tham khảo._';
    }

    if (q.contains('insulin')) {
      return 'Liều insulin thường được tính:\n\n'
          '• **Meal dose** = Carbs (g) ÷ ICR\n'
          '• **Correction** = (Glucose - Target) ÷ CF\n'
          '• **Total** = Meal + Correction\n\n'
          '⚠️ Luôn tuân theo chỉ định bác sĩ.\n\n'
          '_Kết quả chỉ mang tính tham khảo._';
    }

    if (q.contains('carb') || q.contains('tinh bột')) {
      return 'Carbohydrate (carb) là chất dinh dưỡng ảnh hưởng trực tiếp đến đường huyết.\n\n'
          'Thực phẩm giàu carb phổ biến:\n'
          '• Cơm trắng: ~45g/chén\n'
          '• Phở: ~50g/tô\n'
          '• Bánh mì: ~40g/ổ\n\n'
          '_Kết quả chỉ mang tính tham khảo._';
    }

    return 'Tôi hiểu câu hỏi của bạn, nhưng hiện không kết nối được server.\n\n'
        'Vui lòng thử lại khi có mạng, hoặc hỏi về:\n'
        '• GL (Glycemic Load)\n'
        '• Insulin\n'
        '• Carbohydrate\n\n'
        '_Kết quả chỉ mang tính tham khảo._';
  }
}
