# Nền tảng Gia sư AI

Một nền tảng – hai phân khúc: **Thầy An** (đại trà, Toán/Lí THPT) và **Giáo sư Ngô** (tinh hoa, Olympiad/HSG). Chạy trên cùng lõi: router, kiểm chứng, thanh toán, hạ tầng.

> Nguồn sự thật yêu cầu: `02_SRS_HopNhat_v2.2.docx`. Ngữ cảnh & nguyên tắc bất biến: `06_CLAUDE.md`. Lộ trình: `05_KeHoach_CacGiaiDoan_MVP-GD3_v1.0.docx`. Backlog phát triển: `08_Bo_prompt_BUILD_v1.0.md`.

## Cấu trúc

```
/frontend   # Next.js + TypeScript + Tailwind + KaTeX (mobile-first)
/backend    # FastAPI: /router /verify /personas /feedback
docker-compose.yml  # PostgreSQL + pgvector
```

## Chạy local

### 1. Database (Postgres + pgvector)
```bash
docker compose up -d db
```

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # điền khóa LLM ở đây — KHÔNG commit (NFR-30)
alembic upgrade head          # tạo bảng (cần DB ở bước 1)
python -m scripts.seed        # seed admin + gói free + đề mẫu (idempotent)
uvicorn main:app --reload     # http://localhost:8000/health
pytest                        # chạy test (SQLite in-memory, không cần DB)
```

### 3. Frontend (Next.js)
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                   # http://localhost:3000
npm test                      # vitest (render công thức KaTeX…)
```

## Nguyên tắc bất biến

Mọi đóng góp phải tuân **9 nguyên tắc bất biến** trong `06_CLAUDE.md` (dạy gợi mở không giải hộ; north star = learning gain khi tắt AI; khóa LLM chỉ ở backend; kiểm chứng trung thực; …). Commit ghi rõ mã FR liên quan.
