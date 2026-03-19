Để đồ án của bạn trở thành một giải pháp quản lý bệnh lý hoàn chỉnh (không chỉ là một công cụ AI rời rạc), đây là hệ thống 7 màn hình chính cùng các tính năng chi tiết:

1. Màn hình Dashboard (Trung tâm Điều khiển)

- Biểu đồ đường huyết (Interactive Graph): Hiển thị biến thiên chỉ số trong ngày. Các điểm chạm trên biểu đồ sẽ hiện ảnh món ăn tương ứng đã chụp.
- Thẻ chỉ số nhanh:
- Đường huyết hiện tại (nhập tay hoặc sync từ CGM).
  - Dự đoán A1C (Lab-accurate) dựa trên dữ liệu 3 tháng.
  - Huyết áp & Cân nặng.
- Trend Detection: Thông báo AI: "Đường huyết của bạn thường cao sau 8h sáng, hãy chú ý bữa điểm tâm."

2. Màn hình AI Camera (Linh hồn của Đồ án)

- Giao diện Quét 3D: Hiển thị lưới Depthmap thời gian thực để người dùng căn chỉnh góc chụp (đảm bảo độ chính xác thể tích).
- Multi-object Detection: Nhận diện cùng lúc nhiều món trên mâm (ví dụ: bát cơm, đĩa cá, bát canh).
- Xác nhận kết quả: Sau khi quét, hiện bảng tóm tắt: "Cơm: 150g | Cá: 100g -> Tổng GL: 25". Cho phép người dùng điều chỉnh nhanh bằng thanh trượt (Slider) nếu AI nhận diện sai.

3. Màn hình Trợ lý RAG (AI Consultant & Insulin)

- Tính liều Insulin: Nút "Suggest Dosage" dựa trên: GL món ăn + Đường huyết hiện tại + Độ nhạy Insulin của người dùng.
- Chatbot tư vấn (RAG): Ô chat để người dùng hỏi: "Tôi bị chóng mặt sau khi tiêm, nên làm gì?". AI truy xuất lịch sử tiêm và kiến thức y khoa để đưa ra lời khuyên an toàn.
- Cảnh báo an toàn: Nếu liều Insulin tính ra quá cao so với lịch sử, app sẽ yêu cầu xác nhận lại lần nữa.

4. Màn hình Nhật ký Chi tiết (Smart Logbook)

- Dòng thời gian (Timeline): Lưu mọi sự kiện: Ăn uống (có ảnh), Tiêm thuốc (Meds), Tập thể dục (Activities).
- Bộ lọc thông minh (Smart Filters): Lọc theo loại bữa ăn, khoảng thời gian hoặc các sự kiện "Hạ đường huyết".
- Hồ sơ gia đình (Multi-profiles): Nút chuyển đổi nhanh để theo dõi chỉ số cho người thân (bố, mẹ).

5. Màn hình Báo cáo & Chia sẻ (Doctor Connect)

- Export Center: Xuất dữ liệu ra file PDF/Excel/CSV với định dạng chuyên nghiệp để trình bác sĩ.
- Báo cáo xu hướng: Phân tích tỉ lệ thời gian đường huyết nằm trong vùng an toàn (Time in Range).
- Gửi nhanh: Nút chia sẻ trực tiếp qua Zalo/Email cho bác sĩ hoặc người giám hộ.

6. Màn hình Nhắc nhở & Mục tiêu (Habit Tracker)

- Nhắc nhở thông minh: Nhắc đo đường huyết 2 giờ sau khi chụp ảnh bữa ăn; nhắc lịch uống thuốc định kỳ.
- Mục tiêu ngày: Theo dõi tổng lượng Carbs nạp vào so với hạn mức cho phép.

7. Màn hình Cài đặt & Bảo mật (System & Privacy)

- Data Security: Tùy chọn lưu trữ dữ liệu trên thiết bị hoặc Cloud mã hóa.
- Cấu hình cá nhân: Nhập các thông số y tế (Cân nặng, loại tiểu đường, hệ số nhạy insulin) để RAG học và tư vấn chính xác hơn.
- Kết nối thiết bị: Sync với Apple Health, Google Fit, hoặc máy đo CGM.

---

Lời khuyên cho Đồ án:
Hãy chuẩn bị một User Flow (Luồng người dùng) mẫu:

1.  Người dùng cảm thấy đói -> Mở App.
2.  Chụp ảnh đĩa cơm sườn (Màn hình 2) -> AI tính Thể tích & GL.
3.  App tự động hỏi: "Đường huyết hiện tại của bạn là bao nhiêu?" -> Người dùng nhập hoặc Sync.
4.  Màn hình RAG hiện ra gợi ý: "Tiêm 4 đơn vị Insulin" và tư vấn "Nên ăn rau trước khi ăn cơm".
5.  2 giờ sau: App Nhắc nhở đo lại đường huyết để kiểm tra phản ứng cơ thể.

Bạn đã bắt đầu thiết kế UI (Giao diện) cho màn hình nào trong số này chưa?
