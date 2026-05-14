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

/// ChatViewModel — manages AI chat with rich offline knowledge base.
class ChatViewModel extends ChangeNotifier {
  final ApiService _api;

  ChatViewModel(this._api);

  final List<ChatMessage> messages = [];
  bool isTyping = false;
  String? error;

  static const int _maxMessages = 40;

  /// Send a user message and get AI response.
  Future<void> sendMessage(String text, {Map<String, dynamic>? patientContext}) async {
    if (text.trim().isEmpty) return;
    if (messages.where((m) => m.isUser).length >= _maxMessages) {
      error = 'Đã đạt giới hạn $_maxMessages tin nhắn. Vui lòng bắt đầu phiên mới.';
      notifyListeners();
      return;
    }

    messages.add(ChatMessage(text: text.trim(), isUser: true));
    isTyping = true;
    error = null;
    notifyListeners();

    // Simulate thinking delay for natural feel
    await Future.delayed(const Duration(milliseconds: 800));

    try {
      final history = messages
          .take(20)
          .map((m) => {'role': m.isUser ? 'user' : 'assistant', 'content': m.text})
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

      messages.add(ChatMessage(text: botText, isUser: false, sources: sources));
    } catch (_) {
      // Use rich offline knowledge base
      final answer = _knowledgeBase(text);
      messages.add(ChatMessage(text: answer.text, isUser: false, sources: answer.sources));
    } finally {
      isTyping = false;
      notifyListeners();
    }
  }

  void clearChat() {
    messages.clear();
    error = null;
    messages.add(ChatMessage(
      text: 'Xin chào! 👋 Tôi là trợ lý dinh dưỡng InSight.\n\n'
          'Tôi có thể giúp bạn:\n'
          '• Tra cứu GL của các món ăn Việt\n'
          '• Giải thích về insulin, carb, đường huyết\n'
          '• Tư vấn chế độ ăn cho tiểu đường\n'
          '• Hướng dẫn sử dụng app InSight\n\n'
          'Hãy hỏi tôi bất cứ điều gì! 😊',
      isUser: false,
    ));
    notifyListeners();
  }

  // ═══════════════════════════════════════════════════════════════
  // Offline Knowledge Base — Vietnamese Food & Diabetes
  // ═══════════════════════════════════════════════════════════════

  _KBAnswer _knowledgeBase(String query) {
    final q = query.toLowerCase();

    // ── Specific Vietnamese dishes ──
    for (final dish in _vnFoodDB) {
      for (final keyword in dish.keywords) {
        if (q.contains(keyword)) {
          return _KBAnswer(
            text: '🍽️ **${dish.name}** (1 phần)\n\n'
                '• Glycemic Load (GL): **${dish.gl}** — ${dish.glLevel}\n'
                '• Carbohydrate: **${dish.carbs}g**\n'
                '• GI (Glycemic Index): **${dish.gi}**\n'
                '• Khối lượng: ~${dish.weight}g\n\n'
                '${dish.advice}\n\n'
                '_⚠️ Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ._',
            sources: ['USDA FoodData Central', 'Bảng TPDD Việt Nam'],
          );
        }
      }
    }

    // ── Diabetes & sugar questions ──
    if (q.contains('tiểu đường') || q.contains('đái tháo') || q.contains('diabetes')) {
      if (q.contains('kiêng') || q.contains('ăn gì') || q.contains('nên ăn')) {
        return _KBAnswer(
          text: '🥗 **Chế độ ăn cho người tiểu đường**\n\n'
              '✅ **Nên ăn:**\n'
              '• Rau xanh (rau muống, cải, bông cải xanh) — GL rất thấp\n'
              '• Cá, thịt nạc, đậu phụ — protein không tăng đường huyết\n'
              '• Gạo lứt thay cơm trắng — GI thấp hơn 30%\n'
              '• Trái cây ít ngọt: ổi, bưởi, táo\n\n'
              '❌ **Nên hạn chế:**\n'
              '• Cơm trắng nhiều (GL=41, rất cao)\n'
              '• Nước ngọt, trà sữa, bánh ngọt\n'
              '• Trái cây ngọt: xoài, sầu riêng, nhãn\n'
              '• Đồ chiên rán nhiều dầu\n\n'
              '💡 **Mẹo**: Ăn rau trước, protein giữa, tinh bột cuối → giảm spike đường huyết.\n\n'
              '_⚠️ Luôn tham khảo ý kiến bác sĩ._',
          sources: ['ADA Standards of Care 2024'],
        );
      }

      if (q.contains('đường') || q.contains('kiêng đường') || q.contains('tại sao')) {
        return _KBAnswer(
          text: '🔬 **Tại sao tiểu đường phải kiêng đường?**\n\n'
              'Người tiểu đường có vấn đề với **insulin** — hormone giúp đưa glucose từ máu vào tế bào:\n\n'
              '• **Type 1**: Cơ thể KHÔNG sản xuất insulin\n'
              '• **Type 2**: Cơ thể KHÁNG insulin (insulin không hiệu quả)\n\n'
              'Khi ăn đường/tinh bột → glucose máu tăng nhanh → cơ thể không xử lý kịp → **đường huyết cao kéo dài** → tổn thương:\n'
              '• Mạch máu nhỏ (mắt, thận)\n'
              '• Thần kinh ngoại biên\n'
              '• Tim mạch\n\n'
              '💡 **Lưu ý**: Không phải kiêng HOÀN TOÀN đường, mà là **kiểm soát lượng carb** mỗi bữa. '
              'Dùng Glycemic Load (GL) để đánh giá tác động thực tế.\n\n'
              '_⚠️ Kết quả chỉ mang tính tham khảo._',
          sources: ['ADA Standards of Care 2024', 'WHO Diabetes Guidelines'],
        );
      }

      return _KBAnswer(
        text: '📋 **Tiểu đường (Diabetes Mellitus)**\n\n'
            '**Phân loại:**\n'
            '• **Type 1** (~5-10%): Tự miễn, cần insulin suốt đời\n'
            '• **Type 2** (~90-95%): Kháng insulin, quản lý bằng thuốc + chế độ ăn\n'
            '• **Thai kỳ**: Xuất hiện khi mang thai\n\n'
            '**Chỉ số cần theo dõi:**\n'
            '• HbA1c < 7% (mục tiêu)\n'
            '• Glucose lúc đói: 70-130 mg/dL\n'
            '• Glucose sau ăn 2h: < 180 mg/dL\n\n'
            '**InSight giúp gì?**\n'
            'Ước lượng GL từ ảnh thức ăn → giúp bạn nhận thức lượng carb nạp vào.\n\n'
            '_⚠️ Luôn tham khảo ý kiến bác sĩ._',
        sources: ['ADA Standards of Care 2024'],
      );
    }

    // ── GL explanation ──
    if (q.contains('gl') || q.contains('glycemic load') || q.contains('glycemic')) {
      return _KBAnswer(
        text: '📊 **Glycemic Load (GL) là gì?**\n\n'
            'GL đo lường **tác động thực tế** của thực phẩm lên đường huyết, '
            'kết hợp cả chất lượng (GI) và số lượng carb:\n\n'
            '**Công thức:** GL = (GI × Carb grams) ÷ 100\n\n'
            '**Phân loại:**\n'
            '• 🟢 GL < 10: **Thấp** — ít ảnh hưởng đường huyết\n'
            '• 🟡 GL 10-20: **Trung bình** — cần chú ý\n'
            '• 🔴 GL > 20: **Cao** — tăng đường huyết đáng kể\n\n'
            '**Ví dụ:**\n'
            '• Rau xào: GL ≈ 3 (thấp) ✅\n'
            '• Phở bò: GL ≈ 21 (cao) ⚠️\n'
            '• Cơm trắng: GL ≈ 41 (rất cao) 🔴\n\n'
            '💡 GL chính xác hơn GI vì tính cả **lượng** carb thực tế ăn vào.\n\n'
            '_⚠️ Kết quả chỉ mang tính tham khảo._',
        sources: ['Brand-Miller et al., AJCN', 'USDA FoodData Central'],
      );
    }

    // ── Insulin ──
    if (q.contains('insulin') || q.contains('tiêm')) {
      return _KBAnswer(
        text: '💉 **Cách tính liều insulin cho bữa ăn**\n\n'
            '**1. Liều bữa ăn (Meal Bolus):**\n'
            'Meal dose = Carbs (g) ÷ ICR\n'
            '• ICR = Insulin-to-Carb Ratio (VD: 1 unit/10g carb)\n\n'
            '**2. Liều hiệu chỉnh (Correction):**\n'
            'Correction = (Glucose hiện tại - Glucose mục tiêu) ÷ CF\n'
            '• CF = Correction Factor (VD: 50 mg/dL/unit)\n\n'
            '**3. Tổng = Meal + Correction**\n\n'
            '**Ví dụ:** Ăn phở (50g carb), ICR=10, glucose=200, target=120, CF=50\n'
            '• Meal = 50/10 = 5.0 units\n'
            '• Correction = (200-120)/50 = 1.6 units\n'
            '• **Tổng = 6.6 units**\n\n'
            '⚠️ **CẢNH BÁO**: Liều insulin PHẢI được bác sĩ chỉ định. Ứng dụng chỉ ước lượng tham khảo.\n\n'
            '_Kết quả chỉ mang tính tham khảo._',
        sources: ['ADA Insulin Dosing Guidelines'],
      );
    }

    // ── Carb ──
    if (q.contains('carb') || q.contains('tinh bột') || q.contains('carbohydrate')) {
      return _KBAnswer(
        text: '🍚 **Carbohydrate và đường huyết**\n\n'
            'Carb là chất dinh dưỡng ảnh hưởng **trực tiếp nhất** đến đường huyết.\n\n'
            '**Lượng carb các món Việt phổ biến:**\n'
            '• Cơm trắng (1 chén): ~45g\n'
            '• Phở bò (1 tô): ~50g\n'
            '• Bún bò Huế: ~50g\n'
            '• Bánh mì (1 ổ): ~76g\n'
            '• Cơm tấm: ~68g\n'
            '• Rau xào: ~8g\n\n'
            '**Khuyến cáo ADA:**\n'
            '• 45-60g carb / bữa chính\n'
            '• 15-20g carb / bữa phụ\n'
            '• Carb counting quan trọng hơn GI để tính insulin\n\n'
            '_⚠️ Kết quả chỉ mang tính tham khảo._',
        sources: ['ADA Standards of Care 2024', 'USDA FoodData Central'],
      );
    }

    // ── Đường huyết ──
    if (q.contains('đường huyết') || q.contains('glucose') || q.contains('hạ đường') || q.contains('tăng đường')) {
      return _KBAnswer(
        text: '🩸 **Chỉ số đường huyết**\n\n'
            '**Bình thường:**\n'
            '• Lúc đói: 70-100 mg/dL\n'
            '• Sau ăn 2h: < 140 mg/dL\n\n'
            '**Mục tiêu tiểu đường:**\n'
            '• Lúc đói: 70-130 mg/dL\n'
            '• Sau ăn 2h: < 180 mg/dL\n\n'
            '**⚠️ Nguy hiểm:**\n'
            '• < 54 mg/dL: Hạ đường huyết NẶNG → ăn 15g đường nhanh, gọi cấp cứu\n'
            '• 54-69: Hạ đường huyết → ăn 15g đường, đo lại sau 15 phút\n'
            '• > 250: Tăng cao → uống nước, kiểm tra ketone\n'
            '• > 300: Nguy hiểm → liên hệ bác sĩ ngay\n\n'
            '_⚠️ Luôn tham khảo ý kiến bác sĩ._',
        sources: ['ADA Standards of Care 2024'],
      );
    }

    // ── App usage ──
    if (q.contains('app') || q.contains('insight') || q.contains('sử dụng') || q.contains('cách dùng')) {
      return _KBAnswer(
        text: '📱 **Hướng dẫn sử dụng InSight**\n\n'
            '**1. Chụp ảnh phân tích:**\n'
            '• Chụp từ trên xuống (top-down) → kết quả tốt nhất\n'
            '• Đặt thìa/đũa cạnh món ăn làm vật tham chiếu\n'
            '• Chờ 3-5 giây để nhận kết quả GL + tư vấn\n\n'
            '**2. Ước lượng nhanh (Panic Mode):**\n'
            '• Chọn món từ danh sách có sẵn\n'
            '• Kết quả tức thì (< 1 giây)\n'
            '• Dùng khi không có mạng\n\n'
            '**3. Xem lịch sử & biểu đồ:**\n'
            '• Tab Lịch sử: xem chi tiết từng bữa\n'
            '• Tab Phân tích: biểu đồ GL, carb theo ngày\n\n'
            '**4. Hồ sơ sức khỏe:**\n'
            '• Nhập ICR, CF, mục tiêu glucose\n'
            '• App sẽ tính liều insulin gợi ý',
        sources: null,
      );
    }

    // ── GL thấp ──
    if (q.contains('thấp') || q.contains('tốt') || q.contains('an toàn')) {
      return _KBAnswer(
        text: '🥬 **Món ăn Việt có GL thấp (an toàn cho tiểu đường)**\n\n'
            '✅ **GL thấp (< 10):**\n'
            '• Rau xào: GL ≈ 3\n'
            '• Canh rau: GL ≈ 2-4\n'
            '• Thịt/cá nướng: GL ≈ 0-2\n'
            '• Đậu phụ chiên: GL ≈ 1\n'
            '• Gỏi cuốn (2 cuốn): GL ≈ 8\n\n'
            '🟡 **GL trung bình (10-20):**\n'
            '• Bún: GL ≈ 15-18\n'
            '• Miến: GL ≈ 12\n'
            '• Trái cây (1 phần): GL ≈ 8-15\n\n'
            '🔴 **GL cao (> 20) — hạn chế:**\n'
            '• Cơm trắng: GL ≈ 41\n'
            '• Cơm tấm: GL ≈ 47\n'
            '• Bánh mì: GL ≈ 61\n'
            '• Phở: GL ≈ 21\n\n'
            '_⚠️ Kết quả chỉ mang tính tham khảo._',
        sources: ['USDA FoodData Central', 'Bảng TPDD Việt Nam'],
      );
    }

    // ── Default fallback ──
    return _KBAnswer(
      text: 'Cảm ơn câu hỏi của bạn! 😊\n\n'
          'Tôi có thể tư vấn về:\n\n'
          '🍽️ **Món ăn cụ thể**: "GL của phở bò?", "cơm trắng bao nhiêu carb?"\n'
          '📊 **Kiến thức**: "GL là gì?", "cách tính insulin?"\n'
          '🩺 **Tiểu đường**: "tại sao phải kiêng đường?", "nên ăn gì?"\n'
          '📱 **Sử dụng app**: "hướng dẫn sử dụng InSight"\n'
          '🥬 **Gợi ý**: "món nào GL thấp?"\n\n'
          'Hãy thử hỏi cụ thể hơn nhé!\n\n'
          '_⚠️ Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ._',
      sources: null,
    );
  }
}

class _KBAnswer {
  final String text;
  final List<String>? sources;
  _KBAnswer({required this.text, this.sources});
}

/// Vietnamese food nutrition database for offline chat.
class _VNFood {
  final String name;
  final List<String> keywords;
  final double gl;
  final String glLevel;
  final double carbs;
  final int gi;
  final int weight;
  final String advice;
  const _VNFood({
    required this.name, required this.keywords, required this.gl,
    required this.glLevel, required this.carbs, required this.gi,
    required this.weight, required this.advice,
  });
}

const _vnFoodDB = [
  _VNFood(name: 'Cơm trắng (1 chén)', keywords: ['cơm trắng', 'cơm', 'com trang', 'com'],
      gl: 41.2, glLevel: '🔴 Cao', carbs: 56.4, gi: 73, weight: 200,
      advice: '💡 GL rất cao — nên giảm lượng cơm, thay bằng gạo lứt (GI thấp hơn 30%). Ăn kèm nhiều rau để giảm tốc độ hấp thu.'),
  _VNFood(name: 'Cơm tấm (1 đĩa)', keywords: ['cơm tấm', 'com tam'],
      gl: 47.3, glLevel: '🔴 Cao', carbs: 67.5, gi: 70, weight: 250,
      advice: '💡 GL rất cao — nên ăn nửa đĩa và thêm rau. Thịt sườn nướng không ảnh hưởng đường huyết nhiều.'),
  _VNFood(name: 'Phở bò (1 tô)', keywords: ['phở', 'pho', 'phở bò', 'pho bo'],
      gl: 20.7, glLevel: '🔴 Cao', carbs: 45.0, gi: 46, weight: 450,
      advice: '💡 GL vừa ở mức cao. Nước dùng không có carb, nhưng bánh phở thì có. Ăn ít bánh phở, thêm rau giá.'),
  _VNFood(name: 'Bún bò Huế (1 tô)', keywords: ['bún bò', 'bun bo', 'huế', 'hue'],
      gl: 29.0, glLevel: '🔴 Cao', carbs: 50.0, gi: 58, weight: 500,
      advice: '💡 GL cao — bún có GI trung bình. Nên ăn ít bún hơn, tập trung vào thịt và rau.'),
  _VNFood(name: 'Bánh mì (1 ổ)', keywords: ['bánh mì', 'banh mi'],
      gl: 60.7, glLevel: '🔴 Rất cao', carbs: 75.9, gi: 80, weight: 150,
      advice: '⚠️ GL RẤT CAO — bánh mì trắng có GI=80. Nên ăn nửa ổ hoặc chuyển sang bánh mì nguyên cám.'),
  _VNFood(name: 'Rau xào (1 đĩa)', keywords: ['rau', 'rau xào', 'rau muống', 'cải'],
      gl: 3.0, glLevel: '🟢 Thấp', carbs: 8.0, gi: 37, weight: 200,
      advice: '✅ GL rất thấp — rau xào là lựa chọn tuyệt vời cho người tiểu đường!'),
  _VNFood(name: 'Trái cây (1 phần)', keywords: ['trái cây', 'hoa quả', 'fruit'],
      gl: 8.0, glLevel: '🟢 Thấp', carbs: 15.0, gi: 53, weight: 150,
      advice: '✅ GL thấp — nên chọn trái cây ít ngọt: ổi, bưởi, táo. Tránh xoài, sầu riêng, nhãn.'),
  _VNFood(name: 'Dưa hấu', keywords: ['dưa hấu', 'dua hau', 'watermelon'],
      gl: 7.2, glLevel: '🟢 Thấp', carbs: 11.5, gi: 72, weight: 200,
      advice: '💡 Tuy GI cao (72) nhưng GL thấp vì dưa hấu chứa ÍT carb. Ăn vừa phải (1-2 lát) là an toàn.'),
  _VNFood(name: 'Bún chả (1 phần)', keywords: ['bún chả', 'bun cha'],
      gl: 18.5, glLevel: '🟡 Trung bình', carbs: 40.0, gi: 46, weight: 350,
      advice: '💡 GL trung bình — thịt nướng không ảnh hưởng đường huyết. Nên ăn ít bún hơn.'),
  _VNFood(name: 'Bánh cuốn', keywords: ['bánh cuốn', 'banh cuon'],
      gl: 14.0, glLevel: '🟡 Trung bình', carbs: 28.0, gi: 50, weight: 200,
      advice: '💡 GL trung bình — lựa chọn tương đối an toàn. Ăn kèm rau sống để giảm GL.'),
];
