from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/aml_db"
    ENV: str = "dev"
    class Config:
        env_file = ".env"

settings = Settings()
