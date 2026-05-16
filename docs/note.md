
---

### 1. MỞ ĐẦU: ĐỊNH VỊ DỰ ÁN (2 phút)

* **Slide:** Giới thiệu InSight — Hệ thống ước lượng GL.
* **Note:** * Tuyên bố: Đây là **Proof of Concept (PoC)** — Bản nghiên cứu ứng dụng, không phải sản phẩm thương mại thay thế bác sĩ.
* Mục tiêu: Chứng minh pipeline thuật toán: Ảnh 2D → Thể tích 3D → Dinh dưỡng → Liều tiêm.
* *Hóa giải trước:* Thừa nhận UX hiện tại (chụp 90 độ) là để phục vụ tính chính xác của toán học nghiên cứu.



### 2. DEMO MÓN RẮN: CƠ CHẾ 3D (3 phút)

* **Hành động:** Demo chụp chén Cơm trắng.
* **Note:**
* Công nghệ: YOLOv8 (Reference) + Depth Anything V2 (Depth Map).
* Thuật toán: Tích phân không gian ($V = \iint depth(x,y) \,dA$) — Chia nhỏ chén cơm thành hàng vạn "cột Lego" để tính.
* *Key:* Show màn hình **Under the Hood** để minh chứng toán học thực thụ, không đoán mò.



### 3. DEMO MÓN NƯỚC: BÀI TOÁN THỰC TẾ (4 phút)

* **Hành động:** Demo Tô Bún bò (Đầy & Vơi).
* **Note:**
* Thuật toán: **Bowl-fill Estimation** — Đo khoảng cách từ mặt nước đến vành bát để tính độ vơi (`fill_ratio`).
* *Hóa giải Q2:* Thừa nhận camera bị "mù" dưới nước. Giải pháp: Dùng **Solid Ratio (35%)** làm chuẩn thống kê an toàn và đề xuất **Thanh trượt UI (Slider)** cho bản thương mại để người dùng tự chỉnh "Nhiều bún/Ít bún".



### 4. KIẾN TRÚC: MICROSERVICES & PANIC MODE (4 phút)

* **Slide:** Sơ đồ Hybrid Edge-Cloud.
* **Note:**
* *Hóa giải Q3:* Tại sao Microservices?
1. **AI nặng:** DAv2 25M tham số phải đẩy lên Server xử lý thay vì làm nóng máy điện thoại.
2. **Panic Mode:** Show tính năng chạy **100% Offline** (< 1s) cho trường hợp khẩn cấp/mất mạng.
3. **Lưu vết y tế:** Kafka dùng làm **Audit Trail** ghi nhận lịch sử tiêm để phục vụ pháp lý.





### 5. RAG AGENT: AN TOÀN Y KHOA (3 phút)

* **Slide:** 3 lớp áo giáp an toàn (Safety Guards).
* **Note:**
* *Hóa giải Q4:* Chống ảo giác LLM:
1. **Tách biệt:** LLM chỉ tư vấn văn bản, còn tính liều Insulin do code Python thuật toán cứng xử lý.
2. **Grounding:** Quét và Reject kết quả nếu LLM sinh số lệch > 20% so với code tính.
3. **Cầu dao tổng:** **Safety Caps** khóa chết liều tiêm không quá 30 Units.





### 6. KẾT LUẬN & TƯƠNG LAI (2 phút)

* **Slide:** Future Work.
* **Note:**
* *Hóa giải Q1:* Thừa nhận việc bắt người dùng chụp 90 độ là phiền.
* Hướng giải quyết: Dùng Accelerometer (đo góc nghiêng) để hiệu chỉnh hình học và dùng DAv2 Metric để bỏ luôn vật tham chiếu.
* Chốt: InSight là công cụ **Giáo dục nhận thức dinh dưỡng**, hỗ trợ bệnh nhân hiểu về GL hàng ngày.



---

**Lời khuyên cuối:** Khi hội đồng hỏi, hãy luôn bắt đầu bằng: *"Dạ thưa thầy/cô, câu hỏi này rất hay, nhóm em cũng đã đặt ra giả thuyết này trong quá trình thiết kế và giải quyết bằng cách..."*. Chúc bạn và nhóm có một buổi bảo vệ rực rỡ!