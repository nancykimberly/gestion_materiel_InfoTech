import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "cle-secrete-a-changer-en-production"
    )

    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


settings = Settings()
