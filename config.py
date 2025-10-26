from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Configuración de la aplicación - Chatbot de Viajes con Gemini
    """
    # App
    app_name: str = "Travel Assistant Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./travel_chatbot.db"
    
    # Gemini API
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"  # Puede ser gemini-pro o gemini-1.5-flash
    
    # Model Parameters
    max_tokens: int = 2048
    temperature: float = 0.8  # Mayor creatividad para recomendaciones
    top_p: float = 0.95
    top_k: int = 40
    
    # Sistema de contexto
    conversation_memory_turns: int = 10  # Recordar últimos 10 mensajes
    
    # Cache
    cache_ttl: int = 3600  # 1 hora en segundos
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
