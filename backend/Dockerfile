FROM python:3.12-slim

WORKDIR /app

# Phụ thuộc hệ thống tối thiểu (psycopg/bcrypt dùng wheel sẵn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
# Render/host cấp PORT qua biến môi trường; chạy migration rồi mới phục vụ.
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
