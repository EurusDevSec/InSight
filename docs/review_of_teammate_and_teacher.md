3 Trụ cột Kỹ thuật Cốt lõi
1.	Thị giác máy tính 3D (Thị giác)
Nhiệm vụ chính là chuyển đổi hình ảnh 2D từ smartphone thành thể tích thực (cm3) của món ăn.
•	Phát hiện & Phân đoạn: Sử dụng YOLOv8 hoặc Mask R-CNN để nhận diện từng loại thực phẩm trên đĩa.
•	Ước lượng Thể tích: Đây là phần khó nhất. Bạn cần sử dụng các kỹ thuật như Stereo Vision (2 ảnh từ góc khác nhau) hoặc Reference Object (dùng đồng xu/thẻ làm vật đối chứng) để tính toán kích thước thực.
•	Công nghệ gợi ý: MediaPipe, OpenCV, hoặc Point Cloud processing.
2.	Tính toán Glycemic Load (Bộ não)
Sau khi có thể tích, hệ thống cần chuyển đổi sang khối lượng (gram) và tính toán chỉ số GL.. Trong đó Carbohydrate tính dựa trên khối lượng thực phẩm.
•	Cơ sở dữ liệu: Bạn cần tích hợp các API như USDA FoodData Central hoặc Nutritionix để lấy chỉ số GI và mật độ dinh dưỡng.
•	Thách thức: Xử lý các món ăn hỗn hợp (ví dụ: Phở, Cơm tấm) nơi các thành phần bị trộn lẫn.
3.	Personalized RAG Agent (Trợ lý)
Đây là lớp thông minh giúp cá nhân hóa lời khuyên dựa trên dữ liệu lịch sử của bệnh nhân.
•	Retrieval (Truy xuất): Lấy dữ liệu từ hướng dẫn điều trị tiểu đường (ADA guidelines) và hồ sơ sức khỏe cá nhân.
•	Augmented (Làm giàu): Kết hợp kết quả GL vừa tính được với mức đường huyết hiện tại (từ CGM) để đánh giá rủi ro.
•	Generation (Tạo câu trả lời): Agent sẽ đưa ra lời khuyên: "Món này có GL cao, bạn nên giảm 1/2 lượng cơm hoặc đi bộ 15 phút sau ăn".
	Góp ý của thầy: Các vấn đề cốt lõi này thực chất vẫn chưa giải quyết được bài toán nào cho người bị tiểu đường, E giải quyết được vấn để thể tích cũng chả có giải quyết được j trong khi một ly nước e không thể bt được lượng đường trong lý là bao nhiêu, và mô hình RAG nhóm e sử dụng với mục đích j để hỗ trợ cho người bệnh tiểu đường đó là vấn đề nhóm e phải làm rõ. Đây là một đề tài khá hay và nó có hướng mở nên dễ phát triển, e làm sao đấy để giải quyết được cho người bênh tiểu đường, Ví dụ như để làm rõ thêm chỉ số GL thì e có thể cho họ thêm 1 cái form để cung cấp thông tin thêm để làm rõ về cái món ăn đấy, từ đấy có thể dễ dàng suy đoán ra được,…. 
