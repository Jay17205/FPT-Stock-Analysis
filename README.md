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
