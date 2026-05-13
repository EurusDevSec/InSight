# Phân Tích Chi Tiết Kiến Trúc & Công Nghệ (Architecture Deep Dive)

Tài liệu này giải thích sâu về lý do lựa chọn công nghệ (Tech Stack), cơ chế hoạt động chi tiết của từng thành phần, và phân tích các sơ đồ kiến trúc trong dự án **InSight**.

---

## 1. Phân Tích Tech Stack: Tại sao chọn và nó hoạt động ntn?

Chúng ta không chọn công nghệ vì nó "hot", mà vì nó giải quyết triệt để các bài toán cụ thể của dự án (Performance, Scalability, Accuracy).

### 1.1 Mobile & Edge Layer: Flutter + ONNX Runtime

- **Tại sao chọn?**
  - **Flutter:** Cho phép build 1 lần chạy cả iOS/Android với hiệu năng Native (60fps). Hỗ trợ render đồ họa 3D/AR tốt hơn React Native.
  - **ONNX Runtime:** Đây là "vũ khí bí mật" để chạy AI _ngay trên điện thoại_. Thay vì gửi tất cả ảnh về server (tốn 4G, chậm), ta dùng ONNX để chạy các model nhỏ (như YOLO-Nano) để crop món ăn ngay tại máy người dùng.
- **Có ích gì?** Giảm tải cho server, tăng tốc độ phản hồi, và quan trọng là trải nghiệm người dùng mượt mà (Real-time feedback).
- **Cách hoạt động:** Model AI được train bằng Python (PyTorch) -> Export sang định dạng `.onnx` -> Nhúng vào App Flutter -> App dùng CPU/NPU điện thoại để suy luận.

### 1.2 Communication: REST/HTTP

- **Thực tế triển khai:** Hệ thống sử dụng **REST/HTTP** (không dùng gRPC) cho tất cả giao tiếp giữa services.
- **Tại sao REST thay vì gRPC?** Flutter HTTP client đơn giản hơn gRPC dart lib, debug dễ hơn với Postman/curl. Latency ≤5s vẫn đạt.
- **Cách hoạt động:** Mobile gửi ảnh multipart POST → Gateway (Spring Boot `RestTemplate`) forward tới Vision/RAG FastAPI → JSON response trả về.

### 1.3 Backend Core: Java 17 + Spring Boot 3.2.3 (API Gateway)

- **Tại sao chọn?**
  - **Java 17:** LTS ổn định.
  - **Spring Boot 3.2.3:** Dùng cho API Gateway — tiếp nhận request từ mobile, điều phối Vision + RAG.
- **Có ích gì?** `PipelineService` orchestrate: gọi Vision → gọi RAG → combine + disclaimer → trả về Flutter.
- **Lưu ý:** RAG service và Vision service đều dùng Python FastAPI — chỉ API Gateway là Java. Không có Logic Service riêng.

### 1.4 Vision Engine: Python + Depth Anything V2

- **Tại sao chọn?**
  - **Python:** Ngôn ngữ số 1 về AI.
  - **Depth Anything V2 (SOTA 2025):** Các model cũ cần camera kép hoặc LiDAR (chỉ có trên iPhone Pro). Model này có thể đoán độ sâu cực chính xác chỉ từ **1 camera thường** (Monocular Depth Estimation).
- **Có ích gì?** Giúp ứng dụng chạy được trên mọi điện thoại Android/iOS bình thường, không cần thiết bị đắt tiền.
- **Cách hoạt động:** Nhận ảnh 2D -> Model suy luận ra bản đồ độ sâu (Depth Map - ảnh trắng đen thể hiện độ xa gần) -> Thuật toán tích phân tính toán thể tích không gian 3D.

### 1.5 The Brain: Python RAG + Gemini API + Milvus

- **Tại sao chọn?**
  - **Python FastAPI + OpenAI SDK:** RAG service viết bằng Python (cùng stack với Vision), dùng OpenAI-compatible SDK gọi Gemini API.
  - **Google Gemini API (Free Tier):** LLM miễn phí, chất lượng tốt, hỗ trợ OpenAI-compatible endpoint.
  - **Milvus:** Vector DB chuyên dụng, tìm kiếm vector nhanh hơn Postgres `pgvector` khi dữ liệu lớn.
- **Có ích gì?** Tư vấn y khoa chính xác. Thay vì trả lời chung chung, hệ thống tìm đúng đoạn văn bản trong phác đồ điều trị (Bộ Y Tế/ADA) liên quan đến tình trạng bệnh nhân.
- **Cách hoạt động:** Câu hỏi + Chỉ số đường huyết -> Biến đổi thành Vector -> Tìm trong Milvus các đoạn văn bản tương đồng (Semantic Search) -> Đưa vào Gemini LLM để sinh lời khuyên dễ hiểu.

---

## 2. Giải Thích Chi Tiết 3 Sơ Đồ Kiến Trúc

### 2.1 Sơ đồ 1: System Component Diagram (Kiến trúc các Zone)

Đây là bản đồ quy hoạch "Thành phố InSight". Hệ thống chia làm 6 vùng (Zones) biệt lập để dễ quản lý:

1.  **Zone 1 (Mobile):** Flutter app — chụp ảnh, chọn món, hiển thị kết quả + Panic Mode.
2.  **Zone 2 (Gateway):** Spring Boot — orchestrate Vision + RAG, Redis cache, Kafka audit.
3.  **Zone 3 (Vision):** Python FastAPI — Depth map → Calibrate → Segment → Volume → GL.
4.  **Zone 4 (RAG):** Python FastAPI — Retrieve y khoa từ Milvus → Gemini LLM → Insulin advice.
5.  **Zone 5 (Data):** JSON files (nutrition), Milvus (medical KB), Redis (cache), Kafka (audit).

**Ý nghĩa:** Chia nhỏ để trị (Microservices). Nếu RAG bị lỗi → Gateway trả Vision-only (Graceful Degradation). Monitoring chưa triển khai (chưa dùng Prometheus/Grafana).

### 2.2 Sơ đồ 2: Sequence Flow (Hành trình người dùng)

Mô tả từng bước một (Step-by-step) của một chức năng cốt lõi: **Chụp ảnh tính Carbs**.

1.  **User chụp:** App chụp ảnh + chọn loại món từ danh sách 25 món VN.
2.  **Upload:** Ảnh multipart POST qua REST tới Gateway.
3.  **Vision xử lý:** Gateway forward sang Python Vision. Pipeline: Depth → Reference → Calibrate → Segment → Volume → GL. Trả lại Gateway.
4.  **RAG tư vấn:** Gateway hỏi RAG: "GL=13.7, đường huyết 180, ăn 30g Carbs thì tiêm bao nhiêu?". RAG tra Milvus + Gemini → insulin advice.
5.  **Trả kết quả:** Gateway combine Vision + RAG + disclaimer → JSON response.
6.  **Hiển thị:** App hiện GL lớn, uncertainty range, insulin advice + disclaimer banner.

**Ý nghĩa:** Cho thấy sự phối hợp nhịp nhàng (Orchestration) giữa các service.

### 2.3 Sơ đồ 3: Data Flow Diagram (Luồng dữ liệu C4 L2)

Mô tả dòng chảy của dữ liệu (Data Pipeline).

- **Mũi tên đen:** Dữ liệu đi vào. Ảnh từ App -> API -> Vision.
- **Mũi tên database:** API cất dữ liệu vào Postgres. RAG lấy kiến thức từ Milvus.
- **Vòng lặp:** API -> Cache (Redis) -> API. Trước khi hỏi DB, API check Redis xem có kết quả cũ không để trả về cho nhanh.

**Ý nghĩa:** Giúp hiểu rõ dữ liệu đang nằm ở đâu, được xử lý thế nào, và lưu trữ tại đâu.

---

## 3. Cách Hoạt Động Tổng Thể Của Dự Án

Dự án hoạt động theo mô hình **Hybrid Cloud + REST Orchestration**:

1.  **Hybrid (Lai):**
    - Phần "nhẹ" (UI, Panic Mode cache) chạy ở **Edge** (Điện thoại).
    - Phần "nặng" (Depth estimation, LLM) chạy ở **Cloud** (Server).
    - -> Tối ưu chi phí server và trải nghiệm người dùng.

2.  **REST Orchestration (Điều phối đồng bộ):**
    - Gateway nhận request → gọi Vision (HTTP) → gọi RAG (HTTP) → combine response.
    - Kafka chỉ dùng cho **audit events** (fire-and-forget, non-blocking), KHÔNG dùng cho giao tiếp giữa services.
    - Redis cache giảm tải: cùng input → trả cache thay vì tính lại.

3.  **SOTA Integration:**
    - Kết hợp **Computer Vision** (Mắt) để nhìn thế giới vật lý và **GenAI/LLM** (Não) để hiểu và tư vấn. Đây là xu hướng **Multimodal AI** (AI đa phương thức) hiện đại nhất.

---

### Tóm lại

InSight không chỉ là một cái App, nó là một **Hệ phân tán (Distributed System)** thu nhỏ.

- Nó dùng **Toán học** (Tích phân) để giải quyết bài toán lượng.
- Nó dùng **AI** (Vision + LLM) để giải quyết bài toán chất.
- Nó dùng **Engineering** (Microservices, REST orchestration, Graceful Degradation) để đảm bảo tốc độ và độ ổn định.
