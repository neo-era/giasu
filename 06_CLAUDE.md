# CLAUDE.md — Nền tảng Gia sư AI

> File ngữ cảnh cho Claude Code / Cowork. Đọc kỹ phần **Nguyên tắc bất biến** trước khi viết bất kỳ dòng code nào.
> Nguồn sự thật về yêu cầu: **SRS Hợp nhất v2.2**. Khi code, tham chiếu mã FR (FR-C/M/E/L/F).

---

## 1. Dự án là gì

Một nền tảng gia sư AI cho học sinh Việt Nam, **một lõi – hai phân khúc**:

- **Đại trà — "Thầy An"**: Toán/Lí THPT (lớp 10–12). Dạy gợi mở, ấm áp. Kiểm chứng bằng SymPy. Kinh doanh freemium.
- **Tinh hoa — "Giáo sư Ngô"**: Olympiad/HSG (Toán, Lí, Hóa, Tin, Văn/Anh chuyên). Phản biện Socratic, đào sâu. Kiểm chứng đa lớp. Bán B2B trường chuyên.

Hai persona là 2 system prompt khác nhau (xem `prompts/` — Bộ prompt). Chúng chạy trên cùng router, kiểm chứng, thanh toán, hạ tầng.

---

## 2. NGUYÊN TẮC BẤT BIẾN (không được vi phạm)

1. **Dạy gợi mở, KHÔNG giải hộ.** Mặc định nêu gợi ý/câu hỏi dẫn dắt; chỉ cho lời giải đầy đủ khi học sinh thật sự bí hoặc yêu cầu rõ. (FR-M01, FR-L02, FR-L03)
2. **North star = learning gain khi TẮT AI**, KHÔNG tối ưu engagement/thời lượng/số câu hỏi. Mọi tính năng phải phục vụ năng lực tự làm của học sinh. (NFR-50, NFR-51)
3. **Chống lệ thuộc**: buộc nỗ lực trước khi mở gợi ý; tiết chế gợi ý; kiểm tra tắt-AI định kỳ. (FR-L03, FR-L04, FR-L06)
4. **Scaffolding thích ứng theo trình độ**: HS yếu → giải mẫu → mờ dần → gợi ý thuần khi tiến bộ. Không một-công-thức-cho-tất-cả. (FR-L01, FR-L02)
5. **Bảo mật khóa LLM**: mọi lời gọi model ở backend. KHÔNG nhúng API key ở client. (NFR-30)
6. **Phạm vi kiểm chứng trung thực**: "đã kiểm chứng" = phần TÍNH TOÁN (SymPy). KHÔNG khẳng định lập luận khái niệm/chứng minh là đúng nếu chưa kiểm được → gắn cờ độ tin cậy. (mục 3.4 SRS, FR-L08)
7. **Định tuyến model theo BẬC + benchmark**, không gán cứng thương hiệu. Phải có lớp trừu tượng để thay model dễ. (FR-C07, FR-C12)
8. **An toàn trẻ vị thành niên + kiểm duyệt nội dung người dùng** (phản ánh/bình luận). (NFR-31, NFR-33, FR-F08)
9. **Không bịa**: thiếu dữ liệu/không chắc thì nói rõ, không tạo đáp số/chứng minh giả.

---

## 3. Kiến trúc & tech stack (đề xuất)

- **Frontend**: React/Next.js, mobile-first. Render công thức bằng **KaTeX**. (FR-C06)
- **Backend**: Python **FastAPI** (chung với SymPy verification).
- **DB**: PostgreSQL. **Vector DB** (RAG) cho phân khúc tinh hoa.
- **LLM Router**: phân loại intent → định tuyến theo bậc:
  - *Tuyến đầu* (OCR ảnh→LaTeX, phân loại): model vision rẻ-nhanh.
  - *Đại trà*: bậc cân bằng; câu đơn giản → bậc rẻ; gói free → bậc rẻ.
  - *Tinh hoa*: bậc reasoning hàng đầu; cross-check ≥2 model cho bài quan trọng.
- **Lớp kiểm chứng**:
  - *Cấp 1* (tính toán): SymPy — biến đổi, nghiệm, đạo hàm/tích phân, đơn vị.
  - *Cấp 2* (chứng minh, tinh hoa): RAG đối chiếu + cross-check đa model + (Lean/Coq ở GĐ3) + người duyệt (HITL).
- **Kênh phản ánh & cộng đồng** (FR-F, nâng cấp chủ đạo của SRS v2.2): blog/comment để người dùng báo lỗi lời giải/góp ý; đội ngũ trả lời + đổi trạng thái (RBAC); **kiểm duyệt nội dung người dùng** (spam/độc hại/lộ thông tin) bắt buộc trước khi hiển thị; phản ánh "lỗi lời giải" nối thẳng vào hàng đợi của lớp kiểm chứng (FR-F09). (FR-F01–F08, NFR-33)
- **Thanh toán**: ưu tiên **VietQR/A2A** (phí ~0); ví Momo/ZaloPay/VNPay là phụ.
- **Cache**: đệm system prompt + lời giải/đề phổ biến để giảm chi phí token.

---

## 4. Cấu trúc thư mục (đề xuất)

```
/frontend        # React/Next, KaTeX, chat UI, strategy tree (elite), kênh phản ánh (blog/comment)
/backend         # FastAPI: auth, router, verification, payment
  /router        # phân loại + định tuyến model (lớp trừu tượng đổi model)
  /verify        # sympy_check.py, crosscheck.py, rag.py
  /personas      # nạp prompt từ /prompts
  /feedback      # kênh phản ánh (FR-F): gửi/trả lời/trạng thái + kiểm duyệt UGC (FR-F08) + nối hàng đợi kiểm chứng (FR-F09)
/prompts         # bộ prompt sản xuất (xem file Bộ prompt)
/benchmark       # bộ chuẩn chương trình VN (Giai đoạn 0) + eval runner
/docs            # SRS, mô hình kinh tế, kế hoạch
```

---

## 5. Quy ước

- **Nguồn sự thật là SRS**: khi làm tính năng, ghi mã FR liên quan trong commit/PR.
- **Đa ngôn ngữ nội dung**: tiếng Việt, bám **GDPT 2018**; thuật ngữ Toán/Lí chuẩn VN.
- **Công thức**: luôn dùng LaTeX trong `$...$` / `$$...$$`.
- **Quy ước xuất file của Mr. Lâm**: tăng version mỗi lần (v1.0, v1.1…); ghi rõ đuôi định dạng; dùng **double extension** (vd `Bao_gia_v1.1.docx.docx`).
- **Đo lường**: log learning gain (tắt-AI), tỷ lệ tự giải, độ chính xác bộ chuẩn, chi phí token theo phân khúc. KHÔNG coi engagement là KPI hiệu quả.

---

## 6. Việc PHẢI làm trước (Giai đoạn 0 — trước MVP)

1. Xây **bộ chuẩn chương trình VN** (đề + lời giải mẫu đã thẩm định, ~400 mục).
2. Dựng **khung đo learning gain** (pre/post/retention, có nhóm đối chứng, làm khi tắt AI).
3. Qua **cổng Go/No-Go** (G1 bộ chuẩn, G2 độ chính xác AI, G3 learning gain) → mới xây MVP.
Chi tiết: tài liệu *Kế hoạch Giai đoạn 0*.

### Lộ trình sau Giai đoạn 0 (theo *Kế hoạch GĐ MVP–GĐ3*)

Mỗi giai đoạn có **CỔNG RA**; chỉ chuyển tiếp khi vượt cổng. **Learning gain (đo khi tắt AI)** là điều kiện ra cổng ở mọi giai đoạn — KHÔNG dùng engagement.

| GĐ | Trọng tâm | Nhóm FR chính | Cổng ra |
|----|-----------|---------------|---------|
| **MVP** | Lõi + Đại trà (Toán 12, 1–2 chương) | FR-C01–C12; FR-M01,M02,M03,M05,M06,M07; FR-L01,L02,L03,L04,L08; FR-F01,F02,F05,F06,F07,F08 | **M-gate**: learning gain > đối chứng (không tụt khi tắt AI); độ chính xác đạt ngưỡng vận hành; đơn vị kinh tế đại trà có đường tới dương (free đã siết, chuyển đổi đạt mục tiêu) |
| **GĐ2** | Lớp Tinh hoa + chiều sâu đại trà | FR-E01–E05,E08; FR-M04; FR-L05,L06,L07,L09; FR-F03,F04,F09,F10; FR-C09 + phụ huynh + phân tích | **E-gate**: ≥1 hợp đồng B2B; đơn vị KT tinh hoa dương (HLV tiết chế, định giá cao, giới hạn câu); tỷ lệ phát hiện lỗi chứng minh đạt ngưỡng, false positive thấp; learning gain đại trà duy trì dương |
| **GĐ3** | Nâng cao & mở rộng (**cuốn chiếu**) | FR-E06,E07,E09,E10; FR-F11; mở rộng môn/lớp; tính năng phụ | **ROI từng năng lực** dương + có nhu cầu/đối tác; sandbox cô lập đạt kiểm thử bảo mật (nếu làm Virtual Judge) |

**Nguyên tắc phân kỳ:** đại trà (rẻ, nhanh) đi trước để xây dòng tiền + kiểm chứng độ tin cậy; đắp lớp tinh hoa lên **cùng lõi**; GĐ3 làm **cuốn chiếu theo nhu cầu/đối tác, KHÔNG làm đồng loạt**. *Ngoại lệ fast-track:* có đối tác B2B trường chuyên cam kết sớm → đẩy phần tinh hoa GĐ2 song song (tinh hoa không vướng bài toán free-burn của đại trà). Chi tiết: *Kế hoạch GĐ MVP–GĐ3*.

---

## 7. KHÔNG làm (anti-patterns)

- ❌ Cho đáp án trực tiếp theo mặc định (vi phạm gợi mở + tạo lệ thuộc).
- ❌ Tối ưu engagement/thời lượng/giữ chân làm mục tiêu sản phẩm.
- ❌ Nhồi cả kho tài liệu lớn vào context cache (dùng **RAG/retrieval**).
- ❌ Gán cứng "model X chỉ làm việc Y" theo thương hiệu (định tuyến theo benchmark).
- ❌ Dùng số liệu/model đời cũ 2024–2025 (Gemini 1.5, o1/o3, Claude 3.5). Lineup hiện hành 2026.
- ❌ Khẳng định "chứng minh đúng/chặt" khi chưa kiểm chứng được.
- ❌ Lộ API key ở client.

---

## 8. Lệnh thường dùng

```bash
# DB (Postgres + pgvector)
docker compose up -d db

# backend (từ thư mục backend/)
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements-dev.txt
alembic upgrade head            # tạo bảng
python -m scripts.seed          # seed admin + gói free + đề mẫu
uvicorn main:app --reload       # http://localhost:8000/health
pytest                          # toàn bộ test (SQLite in-memory, không cần DB)
ruff check . && black --check . # lint + format

# eval bộ chuẩn (cổng Go/No-Go độ chính xác)
python benchmark/run_eval.py

# frontend (từ thư mục frontend/)
npm install && npm run dev      # http://localhost:3000
npm test                        # vitest (render KaTeX…)
```

> Trạng thái build: backlog `08_Bo_prompt_BUILD` B01–B38 đã hiện thực (MVP + GĐ2
> + khung GĐ3). Sandbox Virtual Judge (FR-E07) TẮT mặc định tới khi qua kiểm thử
> bảo mật; thực thi code sandbox & embedding provider thật là phần tích hợp sau.
