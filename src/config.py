import os

from dotenv import load_dotenv

load_dotenv(os.getenv("ENV_FILE", ".env"))


class Config:
    # db config
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "muzli")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DRIVER = os.getenv("POSTGRES_DRIVER", "postgresql")
    SQLALCHEMY_DATABASE_URI = ("{}://{}:{}@{}:{}/{}").format(
        POSTGRES_DRIVER,
        POSTGRES_USER,
        POSTGRES_PASSWORD,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DATABASE,
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", True)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "004f2af45d3a4e161a7dd2d17fdae47f")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SENDER_EMAIL = os.getenv("EMAIL", "hardik187.rejoice@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SECRET_PASSWORD_KEY = os.getenv(
        "SECRET_KEY_FOR_PASSWORD_RESET", "ghgvgdhbtdgsfgbsdzd"
    )
