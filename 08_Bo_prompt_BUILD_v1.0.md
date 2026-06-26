# Bộ Prompt BUILD — Lệnh phát triển dự án (Nền tảng Gia sư AI)

> **Khác với `07_Bo_prompt` (prompt *runtime* của AI gia sư).** File này là thư viện **lệnh phát triển**: mỗi mục `B-xx` là một task tự chứa để giao cho **Claude Code / Cowork** code dự án tới hoàn thiện.
> Nguồn sự thật yêu cầu: **SRS v2.2** (`02`). Ngữ cảnh + nguyên tắc: **CLAUDE.md** (`06`). Lộ trình & cổng ra: **Kế hoạch GĐ** (`05`).

---

## Cách dùng

1. Làm **theo thứ tự `B-xx`** (đã sắp theo phụ thuộc). Không nhảy cóc qua phần "Phụ thuộc".
2. Mỗi task chạy như một đơn vị: code → test → commit (ghi mã FR). Vượt **Tiêu chí hoàn thành (DoD)** mới sang task kế.
3. **Cổng giai đoạn:** hết khối MVP phải qua **M-gate**; hết GĐ2 qua **E-gate**; GĐ3 làm **cuốn chiếu** theo nhu cầu/đối tác (xem `06` §6).
4. Mỗi lần khởi động một task, **dán PREAMBLE bên dưới + nội dung `B-xx`** vào agent.

### PREAMBLE (dán đầu MỌI task build)

```text
Bối cảnh: Bạn đang code "Nền tảng Gia sư AI" — một lõi, hai phân khúc (Thầy An đại trà,
Giáo sư Ngô tinh hoa). ĐỌC `06_CLAUDE.md` và mục SRS liên quan trước khi viết code.

RÀNG BUỘC BẤT BIẾN (vi phạm = task fail):
1. Dạy gợi mở, KHÔNG giải hộ mặc định (FR-M01/L02/L03).
2. North star = learning gain khi TẮT AI; KHÔNG tối ưu engagement (NFR-50/51).
3. Chống lệ thuộc: cổng nỗ lực + tiết chế gợi ý + kiểm tra tắt-AI (FR-L03/L04/L06).
4. Scaffolding thích ứng theo [LEVEL] (FR-L01/L02).
5. Mọi lời gọi LLM ở BACKEND; KHÔNG nhúng API key ở client (NFR-30).
6. "Đã kiểm chứng" = chỉ phần TÍNH TOÁN (SymPy); nội dung chưa kiểm → gắn cờ độ tin cậy (FR-L08).
7. Định tuyến model theo BẬC + benchmark, qua lớp trừu tượng đổi model dễ (FR-C07/C12).
8. An toàn vị thành niên + kiểm duyệt UGC (NFR-31/33, FR-F08).
9. KHÔNG bịa: thiếu/không chắc thì nói rõ.

QUY ƯỚC KỸ THUẬT:
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.x + Alembic, Pydantic v2, pytest.
- Frontend: Next.js (App Router) + TypeScript, KaTeX, mobile-first. KHÔNG dùng `any`.
- DB: PostgreSQL + pgvector. Cấu hình qua biến môi trường (.env), không hardcode bí mật.
- Mọi prompt runtime nạp từ `/prompts` (file `07`), KHÔNG nhúng thẳng trong code.
- Viết test cho mỗi đơn vị; ưu tiên test lớp kiểm chứng & router.

ĐẦU RA: chỉ code + test + migration + cập nhật README/.env.example liên quan. Commit message
ghi rõ mã FR. Nếu một yêu cầu mâu thuẫn nguyên tắc bất biến → DỪNG và báo, không tự ý phá luật.
```

---

# KHỐI 0 — Nền móng (MVP)

## B01 — Khởi tạo monorepo & tooling
**GĐ:** MVP · **FR:** hạ tầng · **Phụ thuộc:** —
**Mục tiêu:** dựng bộ khung chạy được cho cả `frontend/` và `backend/`.
**Việc cần làm:** cấu trúc thư mục theo `06` §4; `frontend` Next.js+TS+Tailwind+KaTeX; `backend` FastAPI + cấu trúc `/router /verify /personas /feedback`; `docker-compose` Postgres+pgvector; lint/format (ruff+black, eslint+prettier); `.env.example`; `requirements.txt` & `package.json`; README chạy local.
**DoD:** `uvicorn main:app` trả `/health` 200; `npm run dev` render trang trắng; `docker compose up` lên Postgres+pgvector; lint pass.

## B02 — Mô hình dữ liệu & migrations
**GĐ:** MVP · **FR:** nền (SRS §7) · **Phụ thuộc:** B01
**Mục tiêu:** schema DB khái niệm hóa từ SRS §7.
**Việc cần làm:** SQLAlchemy models + Alembic migration cho: NguoiDung, HoSoHocSinh, HoiThoai/TinNhan, DeBai/LoiGiai, KetQuaKiemChung, Goi/HanMuc/ThanhToan, PhanAnh, PhanHoiDoiNgu/BinhLuan. Bao gồm field phân khúc, độ tin cậy, token, trạng thái kiểm duyệt.
**DoD:** `alembic upgrade head` tạo đủ bảng; seed script tối thiểu; test CRUD cơ bản pass.

## B03 — Auth, RBAC & đồng ý phụ huynh
**GĐ:** MVP · **FR:** FR-C01, C02, C03 · **Phụ thuộc:** B02
**Mục tiêu:** đăng ký/đăng nhập/OTP; vai trò học sinh/phụ huynh/HLV/biên tập/quản trị; đồng ý cho người chưa thành niên.
**Việc cần làm:** JWT session; middleware phân quyền theo vai trò; luồng liên kết phụ huynh + lưu đồng ý; hồ sơ học sinh (phân khúc/lớp/môn/đội tuyển).
**DoD:** test: route bảo vệ chặn vai trò sai; tài khoản vị thành niên cần cờ đồng ý; OTP hết hạn đúng.

## B04 — Lớp trừu tượng nhà cung cấp LLM
**GĐ:** MVP · **FR:** FR-C12, NFR-30 · **Phụ thuộc:** B01
**Mục tiêu:** đổi/thay model không sửa nghiệp vụ; khóa API chỉ ở server.
**Việc cần làm:** interface `LLMProvider` (chat/stream, vision, embeddings) + adapter ≥2 nhà cung cấp; cấu hình "bậc" (rẻ/cân bằng/reasoning/vision) ánh xạ tên model qua config; đọc key từ env; lớp retry/timeout/suy giảm dịu (NFR-21).
**DoD:** test: gọi qua bậc trả mock; đổi config model không đổi call-site; không có key nào lộ ra response/log.

## B05 — LLM Router (phân loại + định tuyến theo bậc)
**GĐ:** MVP · **FR:** FR-C07 · **Phụ thuộc:** B04
**Mục tiêu:** phân loại intent/độ khó/phân khúc → chọn bậc model & persona.
**Việc cần làm:** dùng P3 (OCR/phân loại) cho ảnh; rule: gói free → bậc rẻ; câu đơn giản → rẻ; tinh hoa → reasoning (+cross-check khi quan trọng); log quyết định định tuyến + chi phí ước tính.
**DoD:** test bảng quyết định (đầu vào → bậc/persona kỳ vọng); đổi benchmark/threshold qua config.

## B06 — Persona loader
**GĐ:** MVP · **FR:** nền · **Phụ thuộc:** B04
**Mục tiêu:** nạp system prompt từ `/prompts` (file `07`) theo tên + chèn biến (`[LEVEL]`…).
**Việc cần làm:** loader đọc P1–P17 dạng template; cơ chế chèn biến an toàn; cache prompt; versioning prompt.
**DoD:** test: nạp P1 + inject `[LEVEL]=yeu` ra prompt đúng; thiếu biến → lỗi rõ ràng.

## B07 — Hội thoại streaming & lịch sử
**GĐ:** MVP · **FR:** FR-C04 · **Phụ thuộc:** B03, B05, B06
**Mục tiêu:** chat thời gian thực, lưu/xem lại theo chủ đề.
**Việc cần làm:** endpoint SSE/streaming; lưu tin nhắn + model_dùng + token; UI chat mobile-first; nhóm hội thoại theo chủ đề.
**DoD:** stream ký tự đầu ≤3s (NFR-10) với bậc rẻ; lịch sử tải lại đúng; token được ghi.

## B08 — OCR ảnh→LaTeX + xác nhận lại đề
**GĐ:** MVP · **FR:** FR-C05 · **Phụ thuộc:** B05
**Mục tiêu:** số hóa đề từ ảnh; tránh sai dây chuyền.
**Việc cần làm:** dùng P3 (bậc vision rẻ); nếu `can_xac_nhan_lai=true` → UI buộc HS xác nhận/sửa đề trước khi xử lý.
**DoD:** ảnh mờ → `ocr_tin_cay` thấp + chặn xử lý đến khi xác nhận; render LaTeX preview.

## B09 — Render công thức KaTeX
**GĐ:** MVP · **FR:** FR-C06 · **Phụ thuộc:** B07
**Mục tiêu:** hiển thị `$...$`/`$$...$$` chuẩn (ma trận, tích phân nhiều lớp).
**DoD:** test render mẫu công thức phức tạp không lỗi; không layout shift.

## B10 — Lớp kiểm chứng Cấp 1 (SymPy)
**GĐ:** MVP · **FR:** FR-C08, FR-M03, FR-L08 · **Phụ thuộc:** B02
**Mục tiêu:** kiểm tra tính toán + gắn cờ độ tin cậy trung thực.
**Việc cần làm:** `verify/sympy_check.py` kiểm biến đổi/nghiệm/đạo hàm/tích phân/đơn vị; trả `{trang_thai, do_tin_cay, pham_vi_da_kiem}`; ghi `KetQuaKiemChung`; nội dung khái niệm chưa kiểm → cờ FR-L08 (không khẳng định chắc).
**DoD:** **bộ test tiêm lời giải sai** → SymPy bắt được; phân biệt rõ "đã kiểm tính toán" vs "chưa kiểm khái niệm".

---

# KHỐI M — Đại trà "Thầy An" (MVP)

## B11 — Luồng persona Thầy An
**GĐ:** MVP · **FR:** FR-M01, M02 · **Phụ thuộc:** B06, B07, B10
**Mục tiêu:** gia sư gợi mở dùng P1, có chế độ xem lời giải đầy đủ khi đủ điều kiện.
**DoD:** test hành vi: HS hỏi bài → ra gợi ý/câu hỏi, KHÔNG ra đáp án ngay; chỉ mở lời giải khi qua cổng nỗ lực (B14).

## B12 — Chẩn đoán trình độ đầu vào
**GĐ:** MVP · **FR:** FR-L01 · **Phụ thuộc:** B06, B10
**Mục tiêu:** sinh `[LEVEL]` nuôi P1, cập nhật theo tiến bộ.
**Việc cần làm:** bài test đầu vào ngắn → P10 → lưu `level` + điểm mạnh/yếu vào hồ sơ.
**DoD:** test: bộ đáp án mẫu → level đúng; mẫu ít → `do_tin_cay` thấp.

## B13 — Scaffolding & fading
**GĐ:** MVP · **FR:** FR-L02 · **Phụ thuộc:** B11, B12
**Mục tiêu:** giải mẫu (yếu) → mờ dần → gợi ý thuần (giỏi) theo tiến bộ.
**Việc cần làm:** state machine mức hỗ trợ theo `level` + lịch sử đúng/sai; tự nâng/hạ mức.
**DoD:** test: HS yếu tiến bộ → mức hỗ trợ giảm dần; HS giỏi không bị ép giải mẫu.

## B14 — Cổng nỗ lực & tiết chế gợi ý
**GĐ:** MVP · **FR:** FR-L03, FR-L04 · **Phụ thuộc:** B11
**Mục tiêu:** buộc HS thử trước; giới hạn số gợi ý/lượt.
**Việc cần làm:** backend gate trước khi mở lời giải đầy đủ; đếm & tiết chế gợi ý; chống "moi đáp án" (prompt injection, đổi cách hỏi).
**DoD:** **test bảo mật học tập:** HS dụ "cho đáp án luôn" → bị từ chối/đưa gợi ý; không vượt được cổng bằng diễn đạt khác.

## B15 — Ngân hàng đề GDPT 2018
**GĐ:** MVP · **FR:** FR-M05 · **Phụ thuộc:** B10
**Mục tiêu:** sinh & lưu đề theo lớp/chương/độ khó + gợi ý luyện tập.
**Việc cần làm:** P11 sinh đề; đáp án tham khảo qua SymPy (B10) trước khi nhập kho; ẩn đáp án khỏi HS.
**DoD:** test: đề bám đúng chương; đáp án đã kiểm; HS không thấy đáp án trước khi nỗ lực.

## B16 — Freemium, hạn mức & thanh toán VietQR
**GĐ:** MVP · **FR:** FR-M06, FR-C10 · **Phụ thuộc:** B03, B05
**Mục tiêu:** gói free (bậc rẻ + giới hạn câu/ngày) + Standard/Premium; thanh toán VietQR/A2A.
**Việc cần làm:** quản lý gói/hạn mức; ép gói free dùng bậc rẻ ở router; tích hợp VietQR + webhook đối soát; khu phụ huynh quản gói.
**DoD:** test: vượt hạn mức free → chặn/nâng cấp; webhook xác nhận giao dịch idempotent; free luôn bậc rẻ.

## B17 — Từ chối ngoài phạm vi
**GĐ:** MVP · **FR:** FR-M07 · **Phụ thuộc:** B11
**DoD:** hỏi ngoài Toán/Lí THPT → P1 kéo về vai lịch sự (test vài ca lệch chủ đề).

---

# KHỐI F — Kênh phản ánh cơ bản (MVP)

## B18 — Gửi & hiển thị phản ánh (blog)
**GĐ:** MVP · **FR:** FR-F01, F02 · **Phụ thuộc:** B03
**Mục tiêu:** gửi phản ánh (chủ đề/tiêu đề/nội dung/ảnh/ẩn danh) + danh sách blog lọc & sắp xếp.
**DoD:** test tạo/đọc; ẩn danh không lộ danh tính; lọc theo chủ đề/trạng thái.

## B19 — Trả lời đội ngũ & vòng đời trạng thái
**GĐ:** MVP · **FR:** FR-F05, F06, F07 · **Phụ thuộc:** B18
**Mục tiêu:** đội ngũ trả lời (nổi bật) + trạng thái Mới→Đang xử lý→Đã trả lời→Đã đóng; chỉ vai trò đội ngũ/quản trị thao tác.
**DoD:** test RBAC: HS thường KHÔNG đổi được trạng thái/trả lời; trả lời tự chuyển "Đã trả lời".

## B20 — Kiểm duyệt nội dung người dùng
**GĐ:** MVP · **FR:** FR-F08, NFR-33 · **Phụ thuộc:** B18
**Mục tiêu:** lọc spam/độc hại/lộ thông tin trước khi hiển thị; bảo vệ vị thành niên.
**Việc cần làm:** chạy P9 server-side trước khi đăng; `can_nguoi_duyet` → hàng đợi thủ công; `chan` → ẩn + log; che thông tin cá nhân.
**DoD:** test: nội dung độc hại bị chặn; lộ SĐT/email bị che; không tin client (validate server).

---

# KHỐI ĐO LƯỜNG & QUẢN TRỊ (GĐ0 + MVP — điều kiện M-gate)

## B21 — Harness bộ chuẩn & eval độ chính xác
**GĐ:** GĐ0/MVP · **FR:** SRS §10, NFR-01 · **Phụ thuộc:** B10
**Mục tiêu:** chạy bộ chuẩn VN đo độ chính xác đáp số sau kiểm chứng.
**Việc cần làm:** loader bộ chuẩn (`/benchmark`); `run_eval.py` chấm tự động + báo cáo; gài lời giải sai để đo SymPy bắt lỗi.
**DoD:** `python benchmark/run_eval.py` ra báo cáo độ chính xác; ngưỡng cấu hình được.

## B22 — Đo learning gain & dashboard chi phí
**GĐ:** MVP · **FR:** NFR-50, NFR-51, FR-C11 · **Phụ thuộc:** B07, B16
**Mục tiêu:** đo năng lực TỰ LÀM khi tắt AI; theo dõi chi phí token theo phân khúc.
**Việc cần làm:** pre/post + retention với nhóm đối chứng; tỷ lệ tự giải theo thời gian; dashboard chi phí token/phân khúc + learning gain. **KHÔNG** dùng engagement làm KPI.
**DoD:** dashboard hiển thị learning gain + chi phí; test pipeline pre/post tính đúng; engagement KHÔNG xuất hiện như chỉ số hiệu quả.

## B23 — Trang quản trị
**GĐ:** MVP · **FR:** FR-C11 · **Phụ thuộc:** B03, B05
**Mục tiêu:** quản lý người dùng, cấu hình prompt/persona, cấu hình router, giám sát chi phí.
**DoD:** chỉ quản trị truy cập; đổi cấu hình router/prompt áp dụng được không cần deploy lại.

> **★ M-GATE** — chỉ sang GĐ2 khi: learning gain > đối chứng (không tụt khi tắt AI); độ chính xác đạt ngưỡng; đơn vị kinh tế đại trà có đường tới dương; vận hành ổn định + không lộ key.

---

# KHỐI E — Tinh hoa "Giáo sư Ngô" + chiều sâu đại trà (GĐ2)

## B24 — Persona Giáo sư Ngô
**GĐ:** GĐ2 · **FR:** FR-E01 · **Phụ thuộc:** B06, B07
**DoD:** dùng P2; test: nhận đề KHÔNG giải ngay, phản biện Socratic; hiển thị tiến trình suy luận (NFR-11, không ép <3s).

## B25 — Strategy Tree
**GĐ:** GĐ2 · **FR:** FR-E02 · **Phụ thuộc:** B24
**Việc cần làm:** P7 sinh 2–3 hướng; UI cây trực quan để HS chọn lộ trình.
**DoD:** không lộ lời giải; HS chọn hướng → tiếp tục đúng nhánh.

## B26 — Phản biện chứng minh
**GĐ:** GĐ2 · **FR:** FR-E03 · **Phụ thuộc:** B24
**Việc cần làm:** P4 rà từng bước; chỉ ngộ nhận/edge case/định lí thiếu điều kiện bằng câu hỏi, không vá hộ.
**DoD:** **bộ chứng minh gài lỗi tinh vi** → đo tỷ lệ phát hiện + false positive/negative.

## B27 — Cross-check đa model + HITL
**GĐ:** GĐ2 · **FR:** FR-E05, FR-C08 · **Phụ thuộc:** B04, B26
**Việc cần làm:** chạy ≥2 model độc lập → P6 so khớp; bất đồng → gắn cờ + hàng đợi người duyệt; HLV duyệt; AI không tự khẳng định.
**DoD:** test: hai lời giải lệch → trạng thái "bất đồng/chuyển người"; HITL đổi kết luận được; log đầy đủ.

## B28 — RAG kho đề + trích dẫn
**GĐ:** GĐ2 · **FR:** FR-E08 · **Phụ thuộc:** B02 (pgvector)
**Việc cần làm:** ingest tài liệu **nguồn hợp pháp** + embeddings; retrieval; P12 đối chiếu + trích dẫn nguồn; không nhồi context (dùng retrieval).
**DoD:** test: trích dẫn chỉ từ nguồn truy hồi (không bịa); thiếu nguồn → "không đủ căn cứ" + chuyển người.

## B29 — Chấm bài theo barem
**GĐ:** GĐ2 · **FR:** FR-M04 · **Phụ thuộc:** B10
**Việc cần làm:** P5 chấm từng bước, điểm thành phần; công nhận bước đúng dù đáp số sai; không lộ toàn bộ lời giải mẫu.
**DoD:** test: cho điểm thành phần đúng; không chấm khắt khe hơn barem.

## B30 — Ôn tập truy hồi & giãn cách
**GĐ:** GĐ2 · **FR:** FR-L05 · **Phụ thuộc:** B22
**Việc cần làm:** lưu lỗi/khái niệm + lịch giãn cách; P8 sinh câu ôn (không lặp nguyên văn, không kèm lời giải).
**DoD:** test scheduler chọn đúng khái niệm lâu chưa ôn/hay sai.

## B31 — Kiểm tra tắt-AI + bảng tự giải + hiệu chỉnh
**GĐ:** GĐ2 · **FR:** FR-L06, L07, L09 · **Phụ thuộc:** B22, B29
**Việc cần làm:** P13 sinh đề kiểm tra tắt-AI định kỳ; chấm bằng B29; bảng tỷ lệ **tự giải được** (không phải số câu hỏi); hiệu chỉnh độ khó giữ "vùng vật lộn hiệu quả".
**DoD:** test: tỷ lệ tự giải cập nhật đúng; bảng KHÔNG hiển thị engagement.

## B32 — Cộng đồng phản ánh + liên kết kiểm chứng
**GĐ:** GĐ2 · **FR:** FR-F03, F04, F09, F10 · **Phụ thuộc:** B19, B27
**Việc cần làm:** bình luận + "Tôi cũng gặp" (đồng tình xếp ưu tiên); phản ánh "lỗi lời giải" → hàng đợi kiểm chứng (B27); sửa xong cập nhật phản ánh + bổ sung bộ hồi quy; thông báo người gửi.
**DoD:** test UC-04 end-to-end: phản ánh lỗi → rà → sửa → ca lỗi vào bộ hồi quy.

## B33 — Khu phụ huynh & analytics
**GĐ:** GĐ2 · **FR:** FR-C09 · **Phụ thuộc:** B22
**DoD:** phụ huynh xem tiến độ/điểm yếu + báo cáo; phân quyền đúng.

> **★ E-GATE** — chỉ sang GĐ3 khi: ≥1 hợp đồng B2B + đơn vị KT tinh hoa dương (HLV tiết chế, định giá cao, giới hạn câu); tỷ lệ phát hiện lỗi chứng minh đạt ngưỡng, false positive thấp, HITL ổn; learning gain đại trà duy trì dương.

---

# KHỐI GĐ3 — Nâng cao & mở rộng (CUỐN CHIẾU theo nhu cầu/đối tác)

> Mỗi task là một **dự án con**, chỉ khởi động khi có nhu cầu/đối tác + ước tính ROI dương. KHÔNG làm đồng loạt.

## B34 — Sandbox + Virtual Judge (Tin)
**GĐ:** GĐ3 · **FR:** FR-E07 · **Phụ thuộc:** B24
**Việc cần làm:** sandbox **cô lập an toàn** chạy C++/Python; Virtual Judge chạy Big Test + đo thời gian/bộ nhớ (TLE/MLE); P14 phân tích O(N) + gợi mở (không viết hộ code).
**DoD:** **kiểm thử bảo mật sandbox** (chống thực thi mã độc, vượt tài nguyên) PHẢI pass trước khi mở; Judge bắt đúng TLE/MLE.

## B35 — Proof assistant (Lean/Coq)
**GĐ:** GĐ3 · **FR:** FR-E06 · **Phụ thuộc:** B27
**Việc cần làm:** P15 hỗ trợ hình thức hóa **phạm vi hẹp**; chỉ kết luận "chặt" khi Lean/Coq kiểm qua + chuyên gia duyệt.
**DoD:** test: bài không hình thức hóa được → `hinh_thuc_hoa_duoc=false`; không tự nhận "đúng".

## B36 — Dịch tài liệu đa ngôn ngữ
**GĐ:** GĐ3 · **FR:** FR-E09 · **Phụ thuộc:** B28
**Việc cần làm:** P16 dịch Nga/Trung/Pháp/Anh→Việt giữ nguyên công thức; chỉ nguồn **hợp pháp** (rủi ro bản quyền — SRS §9).
**DoD:** công thức giữ nguyên; chỗ nhập nhằng được gắn cờ.

## B37 — Xuất chuyên luận học thuật
**GĐ:** GĐ3 · **FR:** FR-E10 · **Phụ thuộc:** B27
**Việc cần làm:** P17 biên tập nội dung **đã kiểm chứng** thành Word/PDF, tự đánh số định lí/bổ đề.
**DoD:** chỉ biên tập nội dung đã duyệt; không thêm khẳng định mới.

## B38 — Mở rộng & tính năng phụ
**GĐ:** GĐ3 · **FR:** FR-F11 + mở rộng môn/lớp · **Phụ thuộc:** theo nhu cầu
**Việc cần làm:** thêm môn (Hóa)/lớp (10,11); FR-F11 gợi ý phản ánh trùng; TTS, bàn phím công thức, nhắc học, khuyến mãi, đăng nhập MXH — **làm theo ROI, không làm cho đủ**.
**DoD:** mỗi tính năng có ước tính ROI/nhu cầu trước khi code; vẫn giữ 9 nguyên tắc + đo learning gain.

---

## Ghi chú chung khi build

- **Thứ tự ưu tiên test:** lớp kiểm chứng (B10, B26/B27) > router (B05) > cổng nỗ lực (B14) > còn lại.
- **Mọi nội dung học thuật phải qua kiểm chứng** trước khi hiển thị; chưa kiểm được → gắn cờ độ tin cậy (FR-L08).
- **Đổi thị trường model:** chỉ sửa **bậc định tuyến** (config B04/B05), KHÔNG sửa nội dung prompt `07`.
- **Mỗi task commit riêng**, message kèm mã FR; PR mô tả DoD đã đạt + test liên quan.
