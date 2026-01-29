# Phân Tích Chi Tiết Kiến Trúc & Công Nghệ (Architecture Deep Dive)

Tài liệu này giải thích sâu về lý do lựa chọn công nghệ (Tech Stack), cơ chế hoạt động chi tiết của từng thành phần, và phân tích các sơ đồ kiến trúc trong dự án **InSight**.

---

## 1. Phân Tích Tech Stack: Tại sao chọn và nó hoạt động ntn?

Chúng ta không chọn công nghệ vì nó "hot", mà vì nó giải quyết triệt để các bài toán cụ thể của dự án (Performance, Scalability, Accuracy).

### 1.1 Mobile & Edge Layer: Flutter + ONNX Runtime
*   **Tại sao chọn?**
    *   **Flutter:** Cho phép build 1 lần chạy cả iOS/Android với hiệu năng Native (60fps). Hỗ trợ render đồ họa 3D/AR tốt hơn React Native.
    *   **ONNX Runtime:** Đây là "vũ khí bí mật" để chạy AI *ngay trên điện thoại*. Thay vì gửi tất cả ảnh về server (tốn 4G, chậm), ta dùng ONNX để chạy các model nhỏ (như YOLO-Nano) để crop món ăn ngay tại máy người dùng.
*   **Có ích gì?** Giảm tải cho server, tăng tốc độ phản hồi, và quan trọng là trải nghiệm người dùng mượt mà (Real-time feedback).
*   **Cách hoạt động:** Model AI được train bằng Python (PyTorch) -> Export sang định dạng `.onnx` -> Nhúng vào App Flutter -> App dùng CPU/NPU điện thoại để suy luận.

### 1.2 Communication: gRPC (Google Remote Procedure Call)
*   **Tại sao chọn?** REST API truyền dữ liệu dạng văn bản (JSON), rất chậm khi truyền file ảnh lớn. gRPC truyền dữ liệu dạng nhị phân (Binary - Protobuf).
*   **Có ích gì?** **Nhanh hơn 7-10 lần** so với REST. Tiết kiệm băng thông mobile. Định nghĩa kiểu dữ liệu chặt chẽ (Strongly Typed), tránh lỗi "gửi string mà nhận int".
*   **Cách hoạt động:** Mobile đóng gói ảnh thành các byte nhị phân -> Gửi qua HTTP/2 -> Server Java nhận và giải mã cực nhanh.

### 1.3 Backend Core: Java 21 + Spring Boot 3.3 (Virtual Threads)
*   **Tại sao chọn?**
    *   **Java 21:** LTS mới nhất.
    *   **Spring Boot 3.3 + Virtual Threads (Project Loom):** Trước đây, 1 request = 1 luồng hệ điều hành (nặng, tốn RAM). Virtual Threads cho phép tạo **hàng triệu luồng ảo** siêu nhẹ.
*   **Có ích gì?** Server có thể xử lý hàng chục nghìn kết nối đồng thời (high concurrency) mà không bị sập hay tốn quá nhiều RAM. Cực kỳ phù hợp cho hệ thống I/O bound (gọi DB, gọi AI service liên tục) như InSight.
*   **Cách hoạt động:** Khi Server Java chờ phản hồi từ Python AI Service, Virtual Thread sẽ "ngủ đông" và nhường CPU cho request khác, không chiếm dụng tài nguyên thực.

### 1.4 Vision Engine: Python + Depth Anything V2
*   **Tại sao chọn?**
    *   **Python:** Ngôn ngữ số 1 về AI.
    *   **Depth Anything V2 (SOTA 2025):** Các model cũ cần camera kép hoặc LiDAR (chỉ có trên iPhone Pro). Model này có thể đoán độ sâu cực chính xác chỉ từ **1 camera thường** (Monocular Depth Estimation).
*   **Có ích gì?** Giúp ứng dụng chạy được trên mọi điện thoại Android/iOS bình thường, không cần thiết bị đắt tiền.
*   **Cách hoạt động:** Nhận ảnh 2D -> Model suy luận ra bản đồ độ sâu (Depth Map - ảnh trắng đen thể hiện độ xa gần) -> Thuật toán tích phân tính toán thể tích không gian 3D.

### 1.5 The Brain: LangChain4j + Milvus (RAG)
*   **Tại sao chọn?**
    *   **LangChain4j:** Tích hợp AI Logic trực tiếp vào Java (thay vì phải gọi qua Python trung gian rườm rà).
    *   **Milvus:** Vector DB chuyên dụng, tìm kiếm vector nhanh hơn Postgres `pgvector` khi dữ liệu lớn.
*   **Có ích gì?** Tư vấn y khoa chính xác. Thay vì trả lời chung chung, hệ thống tìm đúng đoạn văn bản trong phác đồ điều trị (Bộ Y Tế/ADA) liên quan đến tình trạng bệnh nhân.
*   **Cách hoạt động:** Câu hỏi + Chỉ số đường huyết -> Biến đổi thành Vector -> Tìm trong Milvus các đoạn văn bản tương đồng (Semantic Search) -> Đưa vào LLM để sinh lời khuyên dễ hiểu.

---

## 2. Giải Thích Chi Tiết 3 Sơ Đồ Kiến Trúc

### 2.1 Sơ đồ 1: System Component Diagram (Kiến trúc các Zone)
Đây là bản đồ quy hoạch "Thành phố InSight". Hệ thống chia làm 6 vùng (Zones) biệt lập để dễ quản lý:
1.  **Zone 1 (Edge):** Tiền đồn. App trên tay người dùng. Xử lý sơ bộ.
2.  **Zone 2 (Gateway):** Cổng thành. Java Backend đón nhận mọi yêu cầu, kiểm tra an ninh (Auth), điều phối luồng đi.
3.  **Zone 3 (Core Processing):** Nhà máy xử lý hình ảnh. Nơi Python "xào nấu" ảnh thành số liệu thể tích.
4.  **Zone 4 (The Brain):** Bộ não trung tâm. Nơi Java kết hợp số liệu thể tích + kiến thức y khoa để ra quyết định.
5.  **Zone 5 (Observability):** Tháp canh. Prometheus/Grafana giám sát xem server nào đang chậm, service nào đang lỗi.
6.  **Zone 6 (Data):** Kho chứa. Postgres lưu user, Milvus lưu kiến thức, Redis lưu tạm (cache).

**Ý nghĩa:** Chia nhỏ để trị (Microservices). Nếu "Nhà máy ảnh" (Zone 3) bị lỗi, người dùng vẫn đăng nhập, xem lịch sử (Zone 2, 6) được, không sập toàn bộ app.

### 2.2 Sơ đồ 2: Sequence Flow (Hành trình người dùng)
Mô tả từng bước một (Step-by-step) của một chức năng cốt lõi: **Chụp ảnh tính Carbs**.
1.  **User chụp:** App dùng AI local (ONNX) để crop đúng món ăn.
2.  **Upload:** Ảnh bay qua gRPC tới Java Core.
3.  **Vision hoạt động:** Java Core ném ảnh sang Python Vision. Python chạy Depth Model, tính ra "150ml cơm". Trả lại Java.
4.  **Java tính toán:** Java tra bảng: 150ml cơm = 200g cơm = 56g Carbs.
5.  **Tư vấn:** Java hỏi RAG Agent: "Bệnh nhân đường huyết 180, ăn 56g Carbs thì tiêm bao nhiêu?".
6.  **Trả kết quả:** RAG trả lời. Java đóng gói tất cả gửi về App.
7.  **Hiển thị:** App hiện mô hình 3D AR lên đĩa cơm + Lời khuyên bác sĩ.

**Ý nghĩa:** Cho thấy sự phối hợp nhịp nhàng (Orchestration) giữa các service.

### 2.3 Sơ đồ 3: Data Flow Diagram (Luồng dữ liệu C4 L2)
Mô tả dòng chảy của dữ liệu (Data Pipeline).
*   **Mũi tên đen:** Dữ liệu đi vào. Ảnh từ App -> API -> Vision.
*   **Mũi tên database:** API cất dữ liệu vào Postgres. RAG lấy kiến thức từ Milvus.
*   **Vòng lặp:** API -> Cache (Redis) -> API. Trước khi hỏi DB, API check Redis xem có kết quả cũ không để trả về cho nhanh.

**Ý nghĩa:** Giúp hiểu rõ dữ liệu đang nằm ở đâu, được xử lý thế nào, và lưu trữ tại đâu.

---

## 3. Cách Hoạt Động Tổng Thể Của Dự Án

Dự án hoạt động theo mô hình **Event-Driven Hybrid Cloud**:

1.  **Hybrid (Lai):**
    *   Phần "nhẹ" (Crop ảnh, UI) chạy ở **Edge** (Điện thoại).
    *   Phần "nặng" (3D Depth, LLM) chạy ở **Cloud** (Server).
    *   -> Tối ưu chi phí server và trải nghiệm người dùng.

2.  **Event-Driven (Hướng sự kiện):**
    *   Các service không chờ đợi nhau một cách thụ động (Blocking).
    *   Khi Java nhận ảnh, nó bắn một sự kiện `IMAGE_RECEIVED` vào hàng đợi (Kafka).
    *   Python Vision Service đang rảnh sẽ "nhặt" sự kiện đó về xử lý.
    *   Xử lý xong, Python bắn sự kiện `VOLUME_CALCULATED` ngược lại.
    *   -> Giúp hệ thống không bị tắc nghẽn (Non-blocking) khi có quá nhiều người dùng cùng lúc.

3.  **SOTA Integration:**
    *   Kết hợp **Computer Vision** (Mắt) để nhìn thế giới vật lý và **GenAI/LLM** (Não) để hiểu và tư vấn. Đây là xu hướng **Multimodal AI** (AI đa phương thức) hiện đại nhất.

---

### Tóm lại
InSight không chỉ là một cái App, nó là một **Hệ phân tán (Distributed System)** thu nhỏ.
*   Nó dùng **Toán học** (Tích phân) để giải quyết bài toán lượng.
*   Nó dùng **AI** (Vision + LLM) để giải quyết bài toán chất.
*   Nó dùng **Engineering** (Microservices, gRPC, Virtual Threads) để đảm bảo tốc độ và độ ổn định.
