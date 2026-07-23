from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    IA_PROVEEDOR: str = "deepseek"
    IA_API_KEY: str
    IA_MODELO: str = "deepseek-v4-flash"
    # Endpoint compatible con la API de OpenAI que expone DeepSeek.
    IA_BASE_URL: str = "https://api.deepseek.com"

    # Orígenes permitidos para CORS (front en dev: Vite 5173, CRA 3000).
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
