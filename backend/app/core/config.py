from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/loantrace"
    SECRET_KEY: str = "mysecretkey12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()
