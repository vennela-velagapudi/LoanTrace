from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./local_schema.db"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_JWT_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
