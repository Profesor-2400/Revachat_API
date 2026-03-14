"""
Operaciones CRUD para la base de datos
"""
from sqlalchemy.orm import Session
from src.database.models import Conversation, Message
import uuid
from datetime import datetime
from typing import List, Optional, Dict


def create_conversation(db: Session, title: Optional[str] = None) -> Conversation:
    """Crea una nueva conversación y devuelve el objeto."""
    conv_id = str(uuid.uuid4())
    db_conv = Conversation(conversation_id=conv_id, title=title)
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv


def get_conversation_by_public_id(db: Session, public_id: str) -> Optional[Conversation]:
    """Obtiene una conversación por su conversation_id público."""
    return db.query(Conversation).filter(Conversation.conversation_id == public_id).first()


def get_conversation_messages(db: Session, public_id: str) -> List[Dict]:
    """
    Recupera todos los mensajes de una conversación ordenados cronológicamente.
    Devuelve una lista de diccionarios con role y content (para el modelo).
    """
    conv = get_conversation_by_public_id(db, public_id)
    if not conv:
        return []
    messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at).all()
    return [{"role": msg.role, "parts": msg.content} for msg in messages]


def add_message(db: Session, public_id: str, role: str, content: str):
    """Añade un mensaje a una conversación."""
    conv = get_conversation_by_public_id(db, public_id)
    if not conv:
        raise ValueError("Conversación no encontrada")
    db_msg = Message(conversation_id=conv.id, role=role, content=content)
    db.add(db_msg)
    db.commit()


def get_all_conversations(db: Session) -> List[Dict]:
    """Devuelve todas las conversaciones con metadatos para el historial."""
    convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    result = []
    for conv in convs:
        # Podemos contar mensajes o tomar el último mensaje como resumen
        last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).first()
        result.append({
            "id": conv.conversation_id,
            "title": conv.title or "Chat sin título",
            "created_at": conv.created_at.isoformat(),
            "last_message": last_msg.content if last_msg else "",
            "message_count": db.query(Message).filter(Message.conversation_id == conv.id).count()
        })
    return result


def update_conversation_title(db: Session, public_id: str, title: str):
    """Actualiza el título de una conversación."""
    conv = get_conversation_by_public_id(db, public_id)
    if conv:
        conv.title = title
        db.commit()