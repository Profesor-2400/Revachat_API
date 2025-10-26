from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger
import uvicorn
import sys

from src.chatbot.model import chatbot_model
from config import settings

# Configurar logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/chatbot_{time}.log", rotation="1 day", retention="7 days")

app = FastAPI(
    title="Travel Assistant Chatbot API",
    description="API de chatbot inteligente para recomendaciones de viajes usando Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento temporal de conversaciones (en producción usar DB)
conversations: Dict[str, List[Dict]] = {}

# Modelos de datos
class Message(BaseModel):
    role: str = Field(..., description="Role del mensaje: 'user' o 'model'")
    parts: str = Field(..., description="Contenido del mensaje")

class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del usuario", min_length=1)
    conversation_id: Optional[str] = Field(None, description="ID de la conversación para mantener contexto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Quiero viajar a Japón en primavera, ¿qué me recomiendas?",
                "conversation_id": "user123-conv1"
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta del chatbot")
    conversation_id: str = Field(..., description="ID de la conversación")
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ModelInfo(BaseModel):
    model_name: str
    is_loaded: bool
    provider: str
    temperature: float
    max_tokens: int

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)


@app.on_event("startup")
async def startup_event():
    """
    Inicializa el modelo al arrancar la aplicación
    """
    try:
        logger.info("🚀 Iniciando Travel Assistant Chatbot API...")
        chatbot_model.load_model()
        logger.success("✅ Modelo cargado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar el modelo: {str(e)}")
        logger.warning("La API iniciará pero el chatbot no funcionará correctamente")


@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raíz con información de la API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Chatbot inteligente para recomendaciones de viajes",
        "features": [
            "Recomendaciones de vuelos",
            "Sugerencias de hoteles",
            "Destinos turísticos",
            "Consejos de viaje",
            "Información sobre países y ciudades"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "health": "/health",
            "model_info": "/api/model/info",
            "clear_conversation": "/api/conversation/{conversation_id}"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verifica el estado de la API y el modelo
    """
    return HealthResponse(
        status="ok" if chatbot_model.is_loaded else "degraded",
        model_loaded=chatbot_model.is_loaded
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Endpoint principal para conversar con el chatbot
    
    Mantiene el contexto de la conversación usando conversation_id
    """
    if not chatbot_model.is_loaded:
        raise HTTPException(
            status_code=503, 
            detail="El modelo no está cargado. Por favor intenta más tarde."
        )
    
    try:
        # Obtener o crear conversación
        conv_id = request.conversation_id or f"conv-{datetime.now().timestamp()}"
        
        # Obtener historial (limitado a últimos N mensajes)
        history = conversations.get(conv_id, [])
        limited_history = history[-settings.conversation_memory_turns:]
        
        # Generar respuesta
        response_text = chatbot_model.generate_response(
            message=request.message,
            conversation_history=limited_history
        )
        
        # Actualizar historial
        history.append({"role": "user", "parts": request.message})
        history.append({"role": "model", "parts": response_text})
        conversations[conv_id] = history
        
        logger.info(f"Conversación {conv_id}: Usuario preguntó, bot respondió")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id
        )
        
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")


@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Endpoint para chat con respuesta en streaming (tiempo real)
    """
    if not chatbot_model.is_loaded:
        raise HTTPException(
            status_code=503, 
            detail="El modelo no está cargado."
        )
    
    try:
        conv_id = request.conversation_id or f"conv-{datetime.now().timestamp()}"
        history = conversations.get(conv_id, [])
        limited_history = history[-settings.conversation_memory_turns:]
        
        async def generate():
            full_response = ""
            for chunk in chatbot_model.generate_streaming_response(
                message=request.message,
                conversation_history=limited_history
            ):
                full_response += chunk
                yield chunk
            
            # Guardar en historial después de completar
            history.append({"role": "user", "parts": request.message})
            history.append({"role": "model", "parts": full_response})
            conversations[conv_id] = history
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error en chat streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/conversation/{conversation_id}", tags=["Chat"])
async def clear_conversation(conversation_id: str):
    """
    Elimina el historial de una conversación específica
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversación {conversation_id} eliminada", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")


@app.get("/api/conversations", tags=["Chat"])
async def list_conversations():
    """
    Lista todas las conversaciones activas
    """
    return {
        "total": len(conversations),
        "conversations": [
            {
                "id": conv_id,
                "messages": len(history),
                "last_message": history[-1] if history else None
            }
            for conv_id, history in conversations.items()
        ]
    }


@app.get("/api/model/info", response_model=ModelInfo, tags=["Model"])
async def model_info():
    """
    Obtiene información sobre el modelo actual
    """
    if not chatbot_model.is_loaded:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    return chatbot_model.get_model_info()


@app.post("/api/model/reload", tags=["Model"])
async def reload_model(background_tasks: BackgroundTasks):
    """
    Recarga el modelo (útil si se cambian configuraciones)
    """
    def reload():
        try:
            chatbot_model.load_model()
            logger.success("Modelo recargado exitosamente")
        except Exception as e:
            logger.error(f"Error al recargar modelo: {str(e)}")
    
    background_tasks.add_task(reload)
    return {"message": "Recarga del modelo iniciada en segundo plano"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )
