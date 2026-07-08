import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    IA_PROVEEDOR: str = os.getenv("IA_PROVEEDOR", "default")
    IA_API_KEY: str = os.getenv("IA_API_KEY", "")
    IA_MODELO: str = os.getenv("IA_MODELO", "default_model")

    class Config:
        env_file = ".env"

settings = Settings()