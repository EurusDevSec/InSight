# Vietnamese Demo Samples

## Hướng dẫn cho Hoài

### Danh sách món cần chụp (5-10 mẫu)

| # | Món | Số mẫu | Ghi chú |
|---|-----|--------|---------|
| 1 | Cơm trắng | 1-2 | Chén/bát — dễ chụp nhất |
| 2 | Phở bò | 1-2 | Tô thường |
| 3 | Bánh mì | 1 | Nguyên ổ |
| 4 | Cơm tấm | 1 | Đĩa thường |
| 5 | Bún bò Huế | 1 | Tô thường |

Tùy thời gian: Mì xào, Cháo, Xôi, Bún thịt nướng, Trà sữa

### Checklist chụp ảnh

Cho mỗi mẫu:
1. Đặt món ăn trên bàn có **thìa/đũa** bên cạnh (vật tham chiếu)
2. Chụp **2 góc**:
   - Top-down (nhìn thẳng từ trên)
   - 45 độ (góc nghiêng bình thường)
3. Ánh sáng đều, nền rõ ràng
4. Đặt ảnh vào thư mục đúng format

### Cấu trúc thư mục

```
vn_demo/
├── com_trang/
│   └── com_trang_001/
│       ├── com_trang_001_top.jpg
│       ├── com_trang_001_45.jpg
│       └── com_trang_001.json    ← Copy template & sửa
├── pho_bo/
│   └── pho_bo_001/
│       ├── pho_bo_001_top.jpg
│       ├── pho_bo_001_45.jpg
│       └── pho_bo_001.json
└── ...
```

### Template JSON

Xem file `_template.json` trong thư mục này.
Chỉ cần thay `sample_id`, `images`, và `metadata.notes`.
**KHÔNG CẦN đo nước hay cân** — dùng estimated values từ literature.
