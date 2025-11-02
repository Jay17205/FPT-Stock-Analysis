# 🚀 FPT Stock Analysis

Phân tích dữ liệu cổ phiếu **FPT** bằng Python và SQL Server.  
Dự án này giúp thu thập, lưu trữ và trực quan hóa dữ liệu chứng khoán tự động.

---

## 🧩 Công nghệ sử dụng
- Python (`pandas`, `sqlalchemy`, `matplotlib`, `vnstock`)
- Microsoft SQL Server
- GitHub (lưu trữ mã nguồn)

---

## ⚙️ Các chức năng chính
1. Kết nối API để lấy dữ liệu cổ phiếu FPT.
2. Lưu dữ liệu vào SQL Server (tự động ghi đè phần trùng).
3. Tạo View tính toán biến động giá.
4. Vẽ biểu đồ giá, khối lượng, và Open/Close trực quan.

---

## 📦 Cách chạy code
```bash
pip install pandas sqlalchemy pyodbc matplotlib vnstock
python lap4_5.py
## 2️⃣ Data Understanding

- **Nguồn dữ liệu:** Lấy từ API `vnstock` (nguồn VCI).  
- **Khoảng thời gian:** 2020-11-04 → 2025-11-03  
- **Tổng số dòng:** 1,246 bản ghi  
- **Các cột chính:**
  | Cột | Ý nghĩa | Kiểu dữ liệu |
  |------|----------|--------------|
  | date | Ngày giao dịch | DATE |
  | open | Giá mở cửa | FLOAT |
  | high | Giá cao nhất | FLOAT |
  | low | Giá thấp nhất | FLOAT |
  | close | Giá đóng cửa | FLOAT |
  | volume | Khối lượng giao dịch | BIGINT |

✅ **Missing values:** Không có giá trị bị thiếu, dữ liệu được cập nhật liên tục từ API.
## 3️⃣ Visualization

Các biểu đồ được vẽ bằng `matplotlib`:
1. **Giá đóng cửa (Close)** – theo thời gian, thể hiện xu hướng tăng giảm.  
2. **Khối lượng giao dịch (Volume)** – cho biết hoạt động mua bán từng ngày.  
3. **So sánh Open/Close** – cho thấy chênh lệch giá mở và đóng cửa.  

📊 Dưới đây là ví dụ biểu đồ xuất từ code Python:  
_(Bạn có thể chụp ảnh từ matplotlib và upload vào GitHub bằng drag & drop)_.
