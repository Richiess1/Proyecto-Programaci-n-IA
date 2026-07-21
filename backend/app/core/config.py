from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    IA_PROVEEDOR: str = "deepseek"
    IA_API_KEY: str
    IA_MODELO: str = "deepseek-chat"
    # Endpoint compatible con la API de OpenAI que expone DeepSeek.
    IA_BASE_URL: str = "https://api.deepseek.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
