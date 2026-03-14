from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
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
from src.database.models import get_db
from sqlalchemy.orm import Session
from src.database import crud  # Importamos nuestras nuevas funciones

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

# Modelos de datos (se mantienen igual, pero añadimos ConversationCreate)
class Message(BaseModel):
    role: str
    parts: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = Field(None, description="ID de la conversación. Si no se envía, se crea una nueva.")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Quiero viajar a Japón en primavera, ¿qué me recomiendas?",
                "conversation_id": "user123-conv1"
            }
        }

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationCreateResponse(BaseModel):
    conversation_id: str
    title: Optional[str] = None
    created_at: datetime

class ConversationListItem(BaseModel):
    id: str
    title: str
    created_at: str
    last_message: str
    message_count: int

class ModelInfo(BaseModel):
    model_name: str
    is_loaded: bool
    provider: str
    temperature: float
    max_tokens: int

    class Config:
        protected_namespaces = ()

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        protected_namespaces = ()


@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Iniciando Travel Assistant Chatbot API...")
        chatbot_model.load_model()
        logger.success("✅ Modelo cargado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar el modelo: {str(e)}")
        logger.warning("La API iniciará pero el chatbot no funcionará correctamente")


@app.get("/", tags=["Info"])
async def root():
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
            "conversations": "/api/conversations",
            "create_conversation": "/api/conversations",
            "conversation_messages": "/api/conversations/{conversation_id}/messages",
            "clear_conversation": "/api/conversation/{conversation_id}"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="ok" if chatbot_model.is_loaded else "degraded",
        model_loaded=chatbot_model.is_loaded
    )


# Nuevo endpoint: crear conversación
@app.post("/api/conversations", response_model=ConversationCreateResponse, tags=["Conversations"])
async def create_conversation(db: Session = Depends(get_db)):
    """
    Crea una nueva conversación y devuelve su ID.
    """
    conv = crud.create_conversation(db)
    return ConversationCreateResponse(
        conversation_id=conv.conversation_id,
        title=conv.title,
        created_at=conv.created_at
    )


# Modificar endpoint listar conversaciones para usar BD
@app.get("/api/conversations", response_model=List[ConversationListItem], tags=["Conversations"])
async def list_conversations(db: Session = Depends(get_db)):
    """
    Lista todas las conversaciones con metadatos.
    """
    convs = crud.get_all_conversations(db)
    return convs


# Nuevo endpoint: obtener mensajes de una conversación
@app.get("/api/conversations/{conversation_id}/messages", tags=["Conversations"])
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los mensajes de una conversación específica.
    """
    messages = crud.get_conversation_messages(db, conversation_id)
    if not messages and not crud.get_conversation_by_public_id(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return messages


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal para conversar con el chatbot.
    Mantiene el contexto usando todo el historial de la conversación.
    """
    if not chatbot_model.is_loaded:
        raise HTTPException(status_code=503, detail="El modelo no está cargado. Por favor intenta más tarde.")

    try:
        # 1. Determinar o crear conversación
        if request.conversation_id:
            conv = crud.get_conversation_by_public_id(db, request.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="ID de conversación no válido")
            conv_id = request.conversation_id
        else:
            # Crear nueva conversación automáticamente
            conv = crud.create_conversation(db)
            conv_id = conv.conversation_id
            logger.info(f"Nueva conversación creada: {conv_id}")

        # 2. Recuperar TODO el historial de mensajes
        history = crud.get_conversation_messages(db, conv_id)

        # 3. Generar respuesta con el modelo (le pasamos el historial completo)
        response_text = chatbot_model.generate_response(
            message=request.message,
            conversation_history=history  # Ahora pasamos todo el historial
        )

        # 4. Guardar los mensajes en BD
        crud.add_message(db, conv_id, "user", request.message)
        crud.add_message(db, conv_id, "assistant", response_text)

        # 5. Si es una conversación nueva y no tiene título, asignar un título basado en el primer mensaje
        if not conv.title:
            # Tomamos las primeras palabras del mensaje como título
            title = request.message[:50] + ("..." if len(request.message) > 50 else "")
            crud.update_conversation_title(db, conv_id, title)

        logger.info(f"Conversación {conv_id}: mensaje procesado y guardado")

        return ChatResponse(
            response=response_text,
            conversation_id=conv_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")


@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint para chat con respuesta en streaming.
    """
    if not chatbot_model.is_loaded:
        raise HTTPException(status_code=503, detail="El modelo no está cargado.")

    try:
        # Misma lógica que chat normal
        if request.conversation_id:
            conv = crud.get_conversation_by_public_id(db, request.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="ID de conversación no válido")
            conv_id = request.conversation_id
        else:
            conv = crud.create_conversation(db)
            conv_id = conv.conversation_id

        history = crud.get_conversation_messages(db, conv_id)

        async def generate():
            full_response = ""
            # El método generate_streaming_response debe estar adaptado para recibir el historial
            for chunk in chatbot_model.generate_streaming_response(
                message=request.message,
                conversation_history=history
            ):
                full_response += chunk
                yield chunk

            # Al terminar, guardamos en BD
            crud.add_message(db, conv_id, "user", request.message)
            crud.add_message(db, conv_id, "assistant", full_response)
            if not conv.title:
                title = request.message[:50] + ("..." if len(request.message) > 50 else "")
                crud.update_conversation_title(db, conv_id, title)

        return StreamingResponse(generate(), media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/conversation/{conversation_id}", tags=["Chat"])
async def clear_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Elimina una conversación y todos sus mensajes.
    """
    conv = crud.get_conversation_by_public_id(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    db.delete(conv)
    db.commit()
    return {"message": f"Conversación {conversation_id} eliminada", "status": "success"}


@app.get("/api/model/info", response_model=ModelInfo, tags=["Model"])
async def model_info():
    if not chatbot_model.is_loaded:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    return chatbot_model.get_model_info()


@app.post("/api/model/reload", tags=["Model"])
async def reload_model(background_tasks: BackgroundTasks):
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