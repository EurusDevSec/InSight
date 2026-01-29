# Đánh Giá Tính Thực Tiễn Của InSight: Góc Nhìn "Devil's Advocate" (Người Dùng Khó Tính)

> **Persona:** Tôi là Nam, 35 tuổi, tiểu đường Type 1 được 10 năm. Tôi phải tiêm Insulin trước mỗi bữa ăn. Tôi rất rành công nghệ, nhưng tôi cực kỳ ghét sự phiền phức vì tôi phải làm việc này 3-4 lần/ngày, suốt đời.

---

## 1. Những Lời Khen (Để Sang Một Bên)
Dĩ nhiên, ý tưởng này nghe rất "ngầu". Việc bỏ cái cân tiểu ly ở nhà mà vẫn biết đĩa cơm bao nhiêu gram là giấc mơ của mọi bệnh nhân. AI tư vấn cũng hay đấy. **NHƯNG...** hãy nói về thực tế.

---

## 2. Những "Gáo Nước Lạnh" (The Practicality Gaps)

### Vấn đề 1: "Cái Thẻ Ngân Hàng" (The Reference Object Friction) 🔴
*   **Thực tế:** Bạn yêu cầu tôi mỗi lần chụp ảnh món ăn phải đặt một vật tham chiếu (đồng xu, thẻ ATM, bật lửa) bên cạnh để tính tỷ lệ pixel/cm?
*   **Phản biện:**
    *   **Mất vệ sinh:** Tôi đang ở quán Phở, bàn hơi bẩn. Bạn bảo tôi đặt thẻ ATM (thứ bẩn kinh khủng) lên bàn cạnh bát phở? Hay nhúng cái thìa chuẩn vào?
    *   **Kỳ quặc (Social Stigma):** Tôi đi ăn với đối tác/bạn gái. Tôi lôi thẻ ra, loay hoay căn góc chụp ảnh. Trông tôi như người ngoài hành tinh. Tôi chỉ muốn ăn bình thường thôi.
    *   **Hệ quả:** Sau 3 ngày, tôi sẽ chán và quay lại ước lượng bằng mắt.

### Vấn đề 2: "Bề Nổi Của Tảng Băng" (The Hidden Volume Problem) 🔴
*   **Thực tế:** Món ăn Việt Nam không phải là cái bánh mì sandwich phẳng lì. Nó là bún, phở, cơm thập cẩm.
*   **Phản biện:**
    *   **Bát Phở:** Camera thấy mặt nước lèo. Làm sao nó biết bên dưới là bao nhiêu bánh phở, bao nhiêu thịt? Nó chỉ tính được thể tích của... cái bát nước. Nhưng nước lèo thì ít Carb, bánh phở ở dưới mới nhiều Carb.
    *   **Cơm tấm sườn bì chả:** Miếng sườn che mất một phần cơm. AI tính thể tích miếng sườn hay cơm bên dưới?
    *   **Hệ quả:** Sai số cực lớn với món nước/món trộn. Mà sai 20g Carb là tôi tiêm sai 2 đơn vị Insulin -> Hạ đường huyết -> Nguy hiểm tính mạng.

### Vấn đề 3: Thời Gian & Sự Kiên Nhẫn (Latency vs. Hunger) 🟠
*   **Thực tế:** Khi tôi đói, đường huyết tụt, tay tôi run.
*   **Phản biện:**
    *   Tôi cần kết quả trong 5 giây. Nếu app mất 3s upload + 5s AI Python chạy + 2s LLM "suy nghĩ" + 2s tải về = **12 giây**.
    *   Too long. Lúc đói, 12 giây là vô tận. Tôi sẽ vứt điện thoại và ăn đại.

### Vấn đề 4: Tôi Không Cần Bài Giảng Y Khoa (Over-caring AI) 🟡
*   **Thực tế:** RAG Agent đọc hướng dẫn của ADA (Hiệp hội tiểu đường Mỹ).
*   **Phản biện:**
    *   Tôi bị bệnh 10 năm rồi. Tôi biết ăn bánh ngọt là xấu. Khi tôi định ăn một cái bánh, tôi cần biết tiêm bao nhiêu thuốc để "bù" vào, chứ không cần AI hiện lên một đoạn văn dài 500 từ khuyên răn về lối sống lành mạnh. Nó rất phiền (annoying).

---

## 3. Chấm Điểm Thực Tiễn (Trước Khi Cải Tiến)

*   **Độ Hào Nhoáng (Innovation):** 9/10 (Công nghệ rất xịn).
*   **Độ Chính Xác (Accuracy):** 6/10 (Rủi ro cao với món nước/món khuất).
*   **Trải Nghiệm (UX/Convenience):** 4/10 (Vướng vụ vật tham chiếu và độ trễ).
*   **-> Khả năng tôi dùng lâu dài:** **Thấp.**

---

## 4. Giải Pháp Cải Tiến (Để Biến Nó Thành SOTA Thực Dụng)

Để tôi thực sự dùng app này hàng ngày, bạn cần giải quyết các vấn đề trên như sau:

### 4.1 Loại bỏ "Vật Tham Chiếu" Cứng Nhắc
*   **Giải pháp:** Dùng **Standard Cutlery (Dụng cụ ăn uống tiêu chuẩn)**.
*   Tại sao: Ở Việt Nam, bát ăn cơm (bát chiết yêu), thìa phở, đũa... có kích thước khá chuẩn.
*   **Huấn luyện AI:** Dạy model nhận diện cái bát/cái thìa trong hình để tự làm vật tham chiếu.
*   **UX:** "App đã phát hiện cái bát tiêu chuẩn. Thể tích tính theo bát này." -> *Người dùng không cần lôi thẻ ATM ra nữa.*

### 4.2 Xử lý "Món Ẩn" (Hidden Food) - Mô hình Hybrid
*   **Giải pháp:** **CV + User Input (Click to confirm)**.
*   Cách làm:
    1. AI quét 3D -> Tính ra thể tích tổng cái bát là 500ml.
    2. AI hỏi nhanh (1 chạm): "Đây là Phở hay Bún?" -> Người dùng chọn "Phở".
    3. Backend dùng công thức thống kê (Density Factor): 1 bát phở 500ml thường chứa 150g bánh phở (phần đặc) và 350ml nước.
    4. -> Tính ra Carb dựa trên 150g bánh phở đó.
*   *Chấp nhận sai số nhỏ để đổi lấy khả năng dùng được.*

### 4.3 Chế độ "Panic Mode" (Cho lúc hạ đường huyết)
*   **Giải pháp:** Nút bấm **"Ước lượng nhanh (No AI)"**.
*   Cách làm: Bỏ qua bước đo đạc 3D. Cho hiện ra thư viện ảnh các món phổ biến (Cơm, Phở, Bánh mì). Người dùng chọn ảnh giống nhất -> App trả về Carb trung bình ngay lập tức (<1s).
*   *Lý do:* Lúc cấp cứu, nhanh quan trọng hơn chính xác tuyệt đối.

### 4.4 AI Kiệm Lời & Cá Nhân Hóa (Context-Aware Output)
*   **Giải pháp:** Trả lời theo kiểu **"Actionable Insight"**.
*   Thay vì: "Theo hiệp hội ADA, bạn nên giảm tinh bột..." (Văn mẫu).
*   Hãy nói: "Bát này khoảng 60g Carb. Với mức đường 180 hiện tại, **bạn nên tiêm thêm 1 Unit so với bình thường** (nếu bác sĩ cho phép)."
*   *Ngắn gọn, súc tích, đi thẳng vào vấn đề.*

---

### Tóm lại
Dự án của bạn rất tiềm năng về mặt kỹ thuật. Nhưng để thắng về mặt **Product**, bạn phải hy sinh một chút sự "hoàn hảo kỹ thuật" (như bắt đặt thẻ đo cho chuẩn từng mm) để đổi lấy sự "tiện dụng" (dùng cái thìa, cái bát làm chuẩn).

**Người dùng tiểu đường không cần một cái phòng thí nghiệm trong túi quần. Họ cần một người trợ lý nhanh nhạy và hiểu chuyện.**
