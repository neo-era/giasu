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

    # Khóa nhà cung cấp LLM (điền ở .env, không commit)
    llm_api_key_primary: str = ""
    llm_api_key_secondary: str = ""

    # Xác thực (B03). jwt_secret PHẢI đổi ở production.
    jwt_secret: str = "dev-secret-doi-ngay-o-production-toi-thieu-32-byte"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 giờ (FR-C01)

    # OTP
    otp_length: int = 6
    otp_expire_minutes: int = 10


settings = Settings()
