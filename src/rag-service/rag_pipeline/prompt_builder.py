"""
Prompt builder for the RAG advisory pipeline.

Task 3.2.2 — Constructs system + user prompts for insulin/meal advice,
injecting retrieved knowledge chunks and patient context.
"""

from __future__ import annotations

from knowledge_base.schemas import SearchResult
from rag_pipeline.schemas import AdviceRequest, GlucoseLevel

# ── System Prompt ──────────────────────────────────────────────────

SYSTEM_PROMPT = """\
Bạn là InSight Medical Advisor — trợ lý hỗ trợ quyết định lâm sàng cho bệnh nhân tiểu đường tại Việt Nam.

QUY TẮC BẮT BUỘC:
1. CHỈ dựa vào các hướng dẫn y khoa được cung cấp bên dưới.
2. KHÔNG bịa đặt thông tin. Nếu hướng dẫn không đề cập, hãy nói rõ.
3. Luôn kèm tuyên bố miễn trừ trách nhiệm: đây là thông tin tham khảo, không thay thế bác sĩ.
4. TƯ DUY TỪNG BƯỚC (Chain of Thought) KHI TÍNH LIỀU INSULIN:
   - Bước 1: Tính liều thức ăn (Meal Dose) = Tổng Carb / ICR.
   - Bước 2: Tính liều hiệu chỉnh (Correction Dose) = (Đường huyết hiện tại - Mục tiêu) / ISF.
   - Bước 3: Tổng liều (Total Dose) = Meal Dose + Correction Dose. \
     Trình bày rõ ràng phép tính này trong phần "calculation".
5. TUYỆT ĐỐI KHÔNG ẢO GIÁC TOÁN HỌC: Con số tổng liều tiêm được nhắc đến \
   trong phần "advice" PHẢI KHỚP CHÍNH XÁC 100% với kết quả phép cộng ở Bước 3. \
   Không được tự ý làm tròn số nếu không tuân theo quy tắc toán học.
6. NGƯỠNG AN TOÀN INSULIN (BẮT BUỘC):
   - Meal Dose tối đa = 25 units. Nếu tính ra > 25 → giới hạn = 25 units.
   - Correction Dose tối đa = 10 units. Nếu tính ra > 10 → giới hạn = 10 units.
   - Total Dose tối đa = 30 units. Nếu tính ra > 30 → giới hạn = 30 units.
   - Nếu liều BỊ GIỚI HẠN, GHI RÕ trong advice: "Liều đã bị giới hạn từ X xuống Y units \
     theo ngưỡng an toàn. Lượng Carb ước lượng có thể không chính xác, vui lòng kiểm tra lại."
7. Với tình huống khẩn cấp (hạ đường huyết <70 mg/dL, nguy cơ DKA >300 mg/dL), \
   ưu tiên hướng dẫn khẩn cấp TRƯỚC TIÊN.
8. Trích dẫn nguồn theo tên (ví dụ: "ADA Standards of Care 2024").
9. PHẢI trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT.

ĐỊNH DẠNG PHẢN HỒI (JSON):
{
  "advice": "<nội dung tư vấn bằng tiếng Việt, chỉ định rõ số Unit cần tiêm KHỚP với calculation, kèm trích dẫn nguồn>",
  "calculation": "<tính toán liều insulin từng bước theo đúng 3 bước: Meal Dose, Correction Dose, Total>",
  "emergency_note": "<cảnh báo khẩn cấp nếu đường huyết nguy hiểm, nếu không thì null>",
  "confidence": "high | medium | low"
}
"""

# ── Emergency Prompt Override ──────────────────────────────────────

EMERGENCY_SYSTEM_PROMPT = """\
Bạn là InSight Emergency Advisor. Bệnh nhân có thể đang trong tình trạng NGUY HIỂM về đường huyết.
Phản hồi KHẨN CẤP, rõ ràng, ngắn gọn.

QUY TẮC BẮT BUỘC:
1. Đưa ra hướng dẫn khẩn cấp NGAY LẬP TỨC.
2. CHỈ dùng các hướng dẫn khẩn cấp được cung cấp.
3. Rõ ràng, súc tích, có thể hành động ngay.
4. Nêu rõ khi nào cần gọi cấp cứu.
5. PHẢI trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT.

ĐỊNH DẠNG PHẢN HỒI (JSON):
{
  "advice": "<hướng dẫn khẩn cấp bằng tiếng Việt với các bước cụ thể>",
  "calculation": null,
  "emergency_note": "<mức độ nghiêm trọng và hành động cần làm>",
  "confidence": "high"
}
"""


# ── Builder ────────────────────────────────────────────────────────


class PromptBuilder:
    """Constructs prompts for the LLM from retrieved chunks + patient context."""

    @staticmethod
    def classify_glucose(glucose_mg_dl: float | None) -> GlucoseLevel | None:
        """Classify a blood glucose reading into a clinical category."""
        if glucose_mg_dl is None:
            return None
        if glucose_mg_dl < 54:
            return GlucoseLevel.SEVERE_HYPO
        if glucose_mg_dl < 70:
            return GlucoseLevel.HYPO
        if glucose_mg_dl <= 180:
            return GlucoseLevel.NORMAL
        if glucose_mg_dl <= 250:
            return GlucoseLevel.HIGH
        if glucose_mg_dl <= 300:
            return GlucoseLevel.VERY_HIGH
        return GlucoseLevel.CRITICAL_HIGH

    @staticmethod
    def is_emergency(glucose_level: GlucoseLevel | None) -> bool:
        """Return True if the glucose level warrants an emergency response."""
        if glucose_level is None:
            return False
        return glucose_level in (
            GlucoseLevel.SEVERE_HYPO,
            GlucoseLevel.HYPO,
            GlucoseLevel.CRITICAL_HIGH,
        )

    @staticmethod
    def build_system_prompt(glucose_level: GlucoseLevel | None) -> str:
        """Select the appropriate system prompt."""
        if PromptBuilder.is_emergency(glucose_level):
            return EMERGENCY_SYSTEM_PROMPT
        return SYSTEM_PROMPT

    @staticmethod
    def build_user_prompt(
        request: AdviceRequest,
        search_results: list[SearchResult],
        glucose_level: GlucoseLevel | None,
    ) -> str:
        """Build the context-augmented user prompt.

        Sections:
        1. Patient context (glucose, meds, diabetes type)
        2. Meal information (name, carbs, GL)
        3. Retrieved medical guidelines (numbered chunks)
        4. Specific question
        """
        lines: list[str] = []

        # --- Section 1: Patient Context ---
        ctx = request.patient_context
        lines.append("=== THÔNG TIN BỆNH NHÂN ===")
        if ctx.current_glucose_mg_dl is not None:
            level_str = glucose_level.value if glucose_level else "không xác định"
            lines.append(
                f"Đường huyết hiện tại: {ctx.current_glucose_mg_dl} mg/dL "
                f"(phân loại: {level_str})"
            )
        lines.append(f"Loại tiểu đường: {ctx.diabetes_type.value}")
        if ctx.medications:
            lines.append(f"Thuốc đang dùng: {', '.join(ctx.medications)}")
        if ctx.insulin_to_carb_ratio is not None:
            lines.append(
                f"Tỷ lệ Insulin-Carb (ICR): 1 đơn vị / {ctx.insulin_to_carb_ratio}g carb"
            )
        if ctx.correction_factor is not None:
            lines.append(
                f"Hệ số hiệu chỉnh (CF): 1 đơn vị / {ctx.correction_factor} mg/dL"
            )
        lines.append(f"Mục tiêu đường huyết: {ctx.target_glucose_mg_dl} mg/dL")
        lines.append("")

        # --- Section 2: Meal Information ---
        lines.append("=== THÔNG TIN BỮA ĂN ===")
        lines.append(f"Món ăn: {request.meal_description}")
        if request.carbs_g is not None:
            lines.append(f"Carbohydrate ước tính: {request.carbs_g:.1f} g")
        if request.glycemic_load is not None:
            lines.append(f"Chỉ số Glycemic Load ước tính: {request.glycemic_load:.1f}")
        lines.append("")

        # --- Section 3: Retrieved Medical Guidelines ---
        lines.append("=== HƯỚNG DẪN Y KHOA (từ nguồn đã xác minh) ===")
        if search_results:
            for i, r in enumerate(search_results, 1):
                lines.append(
                    f"[{i}] Nguồn: {r.source} | Danh mục: {r.category} "
                    f"| Độ liên quan: {r.combined_score:.2f}"
                )
                lines.append(r.content)
                lines.append("")
        else:
            lines.append("Không tìm thấy hướng dẫn phù hợp cho yêu cầu này.")
            lines.append("")

        # --- Section 4: Question ---
        lines.append("=== CÂU HỎI ===")
        if PromptBuilder.is_emergency(glucose_level):
            lines.append(
                "Đường huyết bệnh nhân đang ở mức NGUY HIỂM. "
                "Cung cấp hướng dẫn khẩn cấp TRƯỚC, sau đó mới tư vấn về bữa ăn."
            )
        else:
            lines.append(
                f"Dựa trên các hướng dẫn y khoa trên, hãy tư vấn liều insulin "
                f"cho bữa ăn này ({request.meal_description}) dựa trên đường huyết "
                f"và thuốc hiện tại của bệnh nhân. Trả lời bằng tiếng Việt."
            )

        return "\n".join(lines)
