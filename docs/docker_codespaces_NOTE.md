# 🚀 Docker Cloud Workflow (GitHub Codespaces)

Ghi nhớ nhanh để bảo vệ RAM máy tính và 180 giờ miễn phí (Student Pack).

---

## 🛠 1. Quy trình làm việc hàng ngày

1. **Mở VS Code Local** -> Nhấn biểu tượng góc trái dưới -> **Connect to Codespace**.
2. **Tắt Docker Desktop** trên Windows ngay khi đã kết nối Cloud thành công.
3. **Chạy Docker:**
   - `docker-compose up -d` (Chạy ngầm).
   - Kiểm tra tại tab **Ports** bên cạnh Terminal để lấy Link Web.
4. **Dọn rác Cloud:** `docker system prune -f` (Để không bị đầy 20GB Storage).

---

## 🛑 2. Việc PHẢI LÀM khi nghỉ Code (Rất quan trọng)

1. **Lưu code:** `git add .` -> `git commit` -> `git push`.
2. **Dừng Server:** Nhấn góc trái dưới -> Chọn **Stop Current Codespace**.
   - _Lưu ý: Chỉ tắt X cửa sổ VS Code thì server vẫn tính giờ chạy thêm 30p._
3. **Xóa Codespace cũ:** Truy cập [://github.com](https://://github.com) để xóa các bản không dùng.

---

## 📊 3. Cách kiểm tra "Tài sản"

- **Kiểm tra giờ còn lại:** [://github.com](https://github.com/settings/codespaces) (Mục Codespaces).
- **Cấu hình máy:** `Ctrl + Shift + P` -> `Codespaces: Change Machine Type` (Chọn 4-core nếu cần mạnh hơn).
- **Auto-stop:** [://github.com](https://github.com/settings/codespaces#:~:text=browser%20with%20JupyterLab.-,Default%20idle%20timeout,-A%20codespace%20will) -> Chỉnh **Idle Timeout** về **15 phút**.

---

_Ghi chú: Play with Docker sẽ ngừng hoạt động 01/03/2026, hãy trung thành với Codespaces!_
