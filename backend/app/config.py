from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình đọc từ biến môi trường / .env.

    NFR-30: mọi khóa LLM chỉ tồn tại ở backend, đọc từ env — KHÔNG hardcode,
    KHÔNG gửi ra client.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://giasu:giasu@localhost:5432/giasu"
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = True

    # Khóa nhà cung cấp LLM — chỉ ở backend, đọc từ env (NFR-30)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    openai_base_url: str = "https://api.openai.com/v1"

    # Ánh xạ BẬC model → "provider:model" (FR-C07/C12). Mặc định dùng mock
    # để dev/test chạy không cần khóa; production đổi qua env (JSON).
    llm_tiers: dict[str, str] = {
        "re": "mock:mock-fast",
        "can_bang": "mock:mock-balanced",
        "reasoning": "mock:mock-reasoning",
        "vision": "mock:mock-vision",
    }
    # Bậc dự phòng khi bậc chính lỗi (suy giảm dịu — NFR-21). None = không fallback.
    llm_fallback_tier: str | None = None
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2
    llm_retry_backoff: float = 0.2

    # Xác thực (B03). jwt_secret PHẢI đổi ở production.
    jwt_secret: str = "dev-secret-doi-ngay-o-production-toi-thieu-32-byte"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 giờ (FR-C01)

    # OTP
    otp_length: int = 6
    otp_expire_minutes: int = 10


settings = Settings()
