# HỒ SƠ DỰ ÁN — NỀN TẢNG GIA SƯ AI

*Một nền tảng – Hai phân khúc – Đo bằng kết quả học thật.*

Cập nhật: 06/2026 · Người soạn: Mr. Lâm

---

## Luận điểm cốt lõi của cả hồ sơ

Bằng chứng khoa học cho thấy **gia sư AI không mặc nhiên giúp học tốt hơn** — kết quả tùy hoàn toàn vào thiết kế, và phải đo bằng **năng lực TỰ LÀM khi tắt AI (learning gain)**, không phải mức độ sử dụng. Mọi tài liệu trong hồ sơ đều quy về một chuẩn: *học sinh có thật sự giỏi lên khi tắt AI không?*

---

## Thứ tự đọc đề xuất

| # | Tài liệu | Vai trò |
|---|----------|---------|
| 01 | **KeHoach_Tong_The_v1.0.docx** | Tóm tắt điều hành — đọc đầu tiên. Tầm nhìn, 2 phân khúc, phát hiện kinh tế, lộ trình, chỉ số thành công. |
| 02 | **SRS_HopNhat_v2.2.docx** | Đặc tả yêu cầu đầy đủ (nguồn sự thật). Hai phân khúc, router 2026, kiểm chứng 2 cấp, FR-C/M/E/L/F, kênh phản ánh. |
| 03 | **MoHinh_KinhTe_v1.1.xlsx** | Mô hình tài chính có driver. Sheet đại trà + sheet TinhHoa (B2B). Đổi giả định → tự tính lại. |
| 04 | **KeHoach_GiaiDoan0_v1.0.docx** | Tiền đề bắt buộc trước MVP: bộ chuẩn chương trình VN + khung đo learning gain + cổng Go/No-Go. |
| 05 | **KeHoach_CacGiaiDoan_MVP-GD3_v1.0.docx** | Kế hoạch chi tiết MVP, GĐ2, GĐ3: phạm vi FR, mốc thời gian, cổng ra, rủi ro. |
| 06 | **CLAUDE.md** | File ngữ cảnh để build bằng Claude Code/Cowork: 9 nguyên tắc bất biến, kiến trúc, anti-pattern. |
| 07 | **Bo_prompt_v1.0.md** | Thư viện 17 system prompt sản xuất (*runtime* AI gia sư), phủ trọn MVP→GĐ3: Thầy An, Giáo sư Ngô, OCR, kiểm chứng, chấm barem, cross-check, strategy tree, ôn tập, kiểm duyệt UGC, chẩn đoán trình độ, sinh đề GDPT, RAG trích dẫn, kiểm tra tắt-AI, Virtual Judge, Lean/Coq, dịch thuật, xuất chuyên luận. Có bảng ánh xạ prompt↔giai đoạn. |
| 08 | **Bo_prompt_BUILD_v1.0.md** | Bộ prompt **BUILD** — backlog 38 lệnh phát triển (B01–B38) để giao Claude Code/Cowork code dự án tới hoàn thiện, sắp theo phụ thuộc qua các cổng M-gate/E-gate. Mỗi task có FR, deliverables, tiêu chí hoàn thành + test. Có PREAMBLE ràng buộc 9 nguyên tắc bất biến. |

### Thư mục `demo/`
- **Demo_ThayAn_v1.0.html** — nguyên mẫu gia sư gợi mở (chạy thật, có nhập ảnh + render công thức).
- **Demo_PhanAnh_v1.0.html** — nguyên mẫu kênh phản ánh dạng blog/comment (lưu trữ bền).

### Thư mục `phien_ban_cu/`
Các bản đã được thay thế, giữ lại để truy vết: SRS đại trà v1.0, SRS hợp nhất v2.0 & v2.1, mô hình kinh tế v1.0.

---

## Phát hiện quan trọng (đã đưa vào hồ sơ)

- **Đại trà:** token rẻ, nhưng rủi ro sống còn là *free-burn + chuyển đổi thấp* → phải siết gói free, hard paywall, phân phối B2B2C qua trường.
- **Tinh hoa:** chi phí/câu cao gấp ~20 lần (Opus + cross-check + người duyệt) → chỉ khả thi khi *bán B2B giá cao + tiết chế HLV + giới hạn câu*.
- **Kết luận:** không phân khúc nào "tự nhiên có lãi"; mô hình kinh tế v1.1 dùng để chạy kịch bản trước khi rót vốn.

## Lộ trình tóm tắt

GĐ0 (bộ chuẩn + đo lường, có cổng Go/No-Go) → MVP (lõi + đại trà) → GĐ2 (lớp tinh hoa + chiều sâu) → GĐ3 (nâng cao, cuốn chiếu theo ROI).

---

*Quy ước: tài liệu chính thức dùng Times New Roman, khổ A4. Các bản gốc (có double-extension theo quy ước xuất file) vẫn nằm trong thư mục outputs.*
