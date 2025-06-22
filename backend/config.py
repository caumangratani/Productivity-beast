import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    mongodb_uri: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()