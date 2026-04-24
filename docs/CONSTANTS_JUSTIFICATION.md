# InSight — Tài liệu Giải trình Hằng số

> Tài liệu này cung cấp cơ sở khoa học và giải trình thực nghiệm cho
> mọi hằng số quan trọng ("magic number") được sử dụng trong pipeline ước lượng
> thể tích của InSight. Được tạo để phản hồi nhận xét của thầy yêu cầu
> các tham số phải có cơ sở bằng chứng.
>
> Cập nhật lần cuối: 10/04/2026

---

## 1. Tổng quan

Pipeline ước lượng thể tích trong `volume_service.py` sử dụng một số hằng số
thực nghiệm ảnh hưởng trực tiếp đến độ chính xác của ước lượng GL (Glycemic Load).
Mỗi hằng số được ghi chép tại đây với:

- **Chức năng** (vai trò trong công thức)
- **Giá trị hiện tại**
- **Nguồn / giải trình** (tài liệu nghiên cứu, kiểm thử thực nghiệm, hoặc cơ sở dữ liệu tham chiếu)
- **Độ nhạy** (đầu ra thay đổi bao nhiêu khi hằng số thay đổi 1 đơn vị)
- **Hạn chế** (các điểm yếu đã biết)

---

## 2. Các hằng số quan trọng

### 2.1 `_SOLID_VOLUME_CORRECTION = 0.35`

| Mục | Chi tiết |
|-----|----------|
| **File** | `volume_service.py`, dòng ~55 |
| **Chức năng** | Hiệu chỉnh hiện tượng ước lượng thể tích thừa một cách hệ thống từ depth-integral cho món ăn rắn (solid) |
| **Công thức** | `corrected_volume = raw_depth_integral × 0.35` |
| **Nguồn** | Thực nghiệm — được calibrate để giảm thiểu MAPE so với khẩu phần chuẩn món Việt |
| **Giải trình** | DAv2 depth integral ước lượng thừa thể tích thức ăn rắn khoảng ~2.86 lần (1/0.35) do biên đĩa, bias gradient depth, và sự mơ hồ tỷ lệ monocular. Kết quả này nhất quán với phát hiện của Jia et al. (2019) "Accuracy of Food Portion Size Estimation from Digital Images" — báo cáo hệ số ước lượng thừa tương tự (2.5-3.5 lần) cho các hệ thống ước lượng thể tích dựa trên depth. |
| **Ablation** | Đã thử nghiệm 7 giá trị [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]. Hệ số 0.35 đạt MAPE-Weight thấp nhất trên 25 món Việt. Xem `data/ablation_results.json` |
| **Độ nhạy** | Thay đổi ±0.05 → thay đổi ±14.3% trong ước lượng weight/carb/GL |
| **Hạn chế** | Hiệu chỉnh toàn cục — không tính đến sự khác biệt hình dạng riêng của từng loại thức ăn |

### 2.2 `_MAX_VOLUME_ML = 800.0`

| Mục | Chi tiết |
|-----|----------|
| **File** | `volume_service.py`, dòng ~56 |
| **Chức năng** | Giới hạn an toàn — ngăn các ước lượng thể tích phi thực tế |
| **Nguồn** | Tiêu chuẩn khẩu phần ăn Việt Nam (USDA + VN TPDD) |
| **Giải trình** | Khẩu phần đơn lớn nhất trong ẩm thực Việt là bún bò Huế ở mức 550mL. Giá trị 800mL cung cấp khoảng dư 45% so với mức này, đồng thời bắt được các lỗi ước lượng lớn. Hướng dẫn dinh dưỡng của ADA cho thấy khẩu phần 1 bữa ăn hiếm khi vượt quá 600-800mL trong chế độ ăn kiểm soát. |
| **Độ nhạy** | Không áp dụng — chỉ kích hoạt khi có lỗi ước lượng lớn |

### 2.3 Bowl Volume Priors (Thể tích tô mặc định cho món nước)

| Món | Prior (mL) | Nguồn |
|-----|-----------|-------|
| Phở bò/gà | 500 | Tiêu chuẩn quán ăn VN (tô M) |
| Bún bò Huế | 550 | Tiêu chuẩn quán ăn VN (tô M, tô lớn hơn) |
| Bún riêu, Bún mắm | 500 | Tiêu chuẩn quán ăn VN |
| Hủ tiếu, Bánh canh | 450 | Tiêu chuẩn quán ăn VN (tô nhỏ hơn một chút) |
| Cháo | 350 | Tiêu chuẩn hộ gia đình VN |
| Trà sữa | 400 | Trà sữa thương mại (ly M) |

| Mục | Chi tiết |
|-----|----------|
| **File** | `volume_service.py`, dict `_BOWL_VOLUME_PRIOR` |
| **Chức năng** | Thay thế depth-integral cho các món nước, vì depth không phân biệt được phở/bún với nước dùng |
| **Nguồn** | Tiêu chuẩn ngành dịch vụ ăn uống VN, đối chiếu chéo với `typical_serving_g` trong nutrition_db |
| **Giải trình** | Ước lượng thể tích dựa trên depth sai rất lớn cho món nước vì DAv2 không phân biệt được bề mặt nước dùng với đáy tô. Sử dụng khẩu phần tiêu chuẩn làm prior chính xác hơn và được chấp nhận rộng rãi trong nghiên cứu ước lượng dinh dưỡng (ví dụ: Martin et al., 2012, "Comparison of food portion size estimation"). |
| **Độ nhạy** | Thay đổi ±50mL → thay đổi ±10-15% carb/GL cho các món nước |
| **Hạn chế** | Giả định khẩu phần cỡ "Vừa" (Medium) — không tự điều chỉnh theo kích thước tô thực tế trong ảnh |

### 2.4 Density Factors — Hệ số mật độ (`density_factors.json`)

| Mục | Chi tiết |
|-----|----------|
| **File** | `data/nutrition_db/density_factors.json`, 27 mục |
| **Chức năng** | Chuyển đổi thể tích → trọng lượng: `weight = volume × solid_ratio × density` |
| **Nguồn** | USDA Food Composition Database, tài liệu khoa học thực phẩm VN |
| **Nguồn từng mục** | Xem trường `source` trong mỗi mục density factor |
| **Giải trình** | 8/27 mục có giá trị từ USDA, 19/27 mục được ước tính từ thực phẩm tương tự. Tất cả giá trị `solid_ratio` dựa trên quan sát vật lý: phở = 30% rắn (phở + thịt), cơm trắng = 100% rắn, v.v. |
| **Độ nhạy** | Thay đổi ±0.1 density → thay đổi ±10% trọng lượng |
| **Hạn chế** | Các mục "Estimated" chưa được đo lường chính thức. Hướng phát triển: nghiên cứu cân đo thực nghiệm. |

### 2.5 Giá trị dinh dưỡng (`vn_food_nutrition.json`)

| Mục | Chi tiết |
|-----|----------|
| **File** | `data/nutrition_db/vn_food_nutrition.json`, 25 mục |
| **Nguồn** | USDA FoodData Central + VN TPDD + Foster-Powell GI Tables |
| **Nguồn từng mục** | Xem trường `source` trong mỗi mục nutrition |
| **Giải trình** | Giá trị GI từ bảng Foster-Powell et al. được peer-review (International Tables of Glycemic Index, Am J Clin Nutr, 2002). Giá trị carb từ USDA. Các mục đặc trưng Việt Nam từ VN TPDD (Bộ Y Tế). |
| **Hạn chế** | GI thay đổi theo cách nấu, thành phần bữa ăn, và trao đổi chất cá nhân. Giá trị trong database là trung bình quần thể. |

### 2.6 Hệ số Uncertainty cho Error Propagation (Lan truyền sai số)

| Nguồn sai số | Giá trị | Tham chiếu |
|--------------|---------|------------|
| Ước lượng depth (DAv2 monocular) | ±20% | Ranftl et al. (2021), "Vision Transformers for Dense Prediction" — sai số depth tương đối trên NYU Depth V2 |
| Biên segmentation thức ăn | ±15% | Thực nghiệm — độ không chắc chắn của biên mask trên ảnh thức ăn |
| Tra cứu Density/solid_ratio | ±10% | Ước tính — sự biến thiên giữa các món trong cùng danh mục |
| **Tổng hợp (RSS)** | **±27%** | `sqrt(0.20² + 0.15² + 0.10²) = 0.269` |

| Mục | Chi tiết |
|-----|----------|
| **File** | `volume_service.py`, Step 5a |
| **Chức năng** | Tính khoảng uncertainty cho carb/GL, phục vụ báo cáo trung thực |
| **Giải trình** | Root-Sum-Square (RSS) là phương pháp lan truyền sai số tiêu chuẩn trong đo lường (JCGM 100:2008 Guide to Uncertainty in Measurement). Mỗi nguồn sai số được giả định là độc lập và không tương quan. |
| **Đầu ra** | Món rắn: `GL_range = GL × (1 ± 0.27)`. Món nước: `GL_range = GL × (1 ± 0.18)` |
| **Hạn chế** | Giả định sai số phân phối Gauss và các nguồn độc lập. Sai số thực tế có thể tương quan với nhau. |

---

## 3. Ngưỡng Food Segmentation

| Hằng số | Giá trị | Giải trình |
|---------|---------|------------|
| Cảnh báo tỷ lệ food tối thiểu | 5% | Nếu thức ăn chiếm <5% diện tích ảnh, có thể do chụp sai góc → quality="low" |
| Ngưỡng hiệu chỉnh thể tích solid | `is_liquid == False` | Chỉ các món rắn cần hiệu chỉnh depth; món nước dùng bowl priors |

---

## 4. Bảng tổng hợp

| Hằng số | Giá trị | Phân loại | Mức độ bằng chứng |
|---------|---------|-----------|-------------------|
| `_SOLID_VOLUME_CORRECTION` | 0.35 | Thể tích | Ablation study (N=25) |
| `_MAX_VOLUME_ML` | 800.0 | An toàn | Tiêu chuẩn VN + ADA |
| Bowl priors | 350-550 mL | Thể tích | Tiêu chuẩn quán ăn VN |
| Density factors | 0.35-1.15 g/mL | Trọng lượng | USDA/ước tính |
| Solid ratios | 0.1-1.0 | Trọng lượng | Quan sát vật lý |
| GI indices | 46-87 | Dinh dưỡng | Foster-Powell (peer-reviewed) |
| Sai số Depth | ±20% | Sai số | Ranftl et al. (2021) |
| Sai số Segmentation | ±15% | Sai số | Kiểm thử thực nghiệm |
| Sai số Density | ±10% | Sai số | Biến thiên danh mục |

**Chú giải mức độ bằng chứng:**
- **Peer-reviewed**: Công bố trên tạp chí khoa học có phản biện
- **Standard DB**: Cơ sở dữ liệu chính thống USDA/VN TPDD
- **Ablation study**: Kiểm thử thực nghiệm có ghi chép kết quả
- **Tiêu chuẩn VN**: Khẩu phần tiêu chuẩn ngành ẩm thực
- **Thực nghiệm**: Đã quan sát nhưng chưa xác thực chính thức
- **Ước tính**: Suy ra từ các mục tương tự, cần xác thực thêm

---

## 5. Hướng phát triển

1. **Hệ số hiệu chỉnh theo danh mục**: Thử `_SOLID_VOLUME_CORRECTION` khác nhau cho cơm (1.0 solid), bún/mì khô (0.85-0.95 solid), và đĩa hỗn hợp
2. **Nghiên cứu đo lường density**: Cân đo thể tích và trọng lượng thực tế các món Việt để xác thực density factors
3. **Cá nhân hóa GI**: GI thay đổi theo từng người — phiên bản tương lai có thể cho phép profile GI riêng cho từng người dùng
4. **Calibrate uncertainty**: Xác thực rằng khoảng tin cậy báo cáo thực sự chứa giá trị đúng ở tỷ lệ đã nêu
