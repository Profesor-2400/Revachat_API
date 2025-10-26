"""
Modelos de base de datos
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# Configurar base de datos
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Conversation(Base):
    """
    Tabla de conversaciones
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con mensajes
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """
    Tabla de mensajes
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(50))  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con conversación
    conversation = relationship("Conversation", back_populates="messages")


class TrainingExample(Base):
    """
    Tabla de ejemplos de entrenamiento
    """
    __tablename__ = "training_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # SQLite no tiene boolean nativo


class ModelVersion(Base):
    """
    Tabla de versiones del modelo
    """
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True)
    model_path = Column(String(255))
    accuracy = Column(String(50), nullable=True)
    training_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=0)
    notes = Column(Text, nullable=True)


def init_db():
    """
    Inicializa la base de datos
    """
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente")


def get_db():
    """
    Obtiene una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Inicializar BD al importar
if __name__ == "__main__":
    init_db()
