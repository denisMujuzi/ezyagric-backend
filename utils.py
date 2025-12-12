from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env at startup
load_dotenv()

class Settings(BaseSettings):

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Admin Key
    ADMIN_KEY: str

    class Config:
        env_file = ".env"

# Singleton-style access
settings = Settings()