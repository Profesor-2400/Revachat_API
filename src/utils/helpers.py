"""
Funciones auxiliares
"""
import uuid
from datetime import datetime
from typing import List, Dict
import json


def generate_conversation_id() -> str:
    """
    Genera un ID único para una conversación
    """
    return str(uuid.uuid4())


def format_timestamp(dt: datetime = None) -> str:
    """
    Formatea un timestamp
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def clean_text(text: str) -> str:
    """
    Limpia y normaliza texto
    """
    # Eliminar espacios extras
    text = " ".join(text.split())
    
    # Eliminar caracteres especiales problemáticos
    text = text.replace("\r", "").replace("\t", " ")
    
    return text.strip()


def load_training_data_from_json(file_path: str) -> List[Dict]:
    """
    Carga datos de entrenamiento desde un archivo JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        return []


def save_training_data_to_json(data: List[Dict], file_path: str):
    """
    Guarda datos de entrenamiento en un archivo JSON
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Datos guardados en: {file_path}")
    except Exception as e:
        print(f"Error al guardar datos: {str(e)}")


def calculate_accuracy(predictions: List, targets: List) -> float:
    """
    Calcula la precisión de las predicciones
    """
    if len(predictions) != len(targets):
        raise ValueError("Las listas deben tener la misma longitud")
    
    correct = sum(p == t for p, t in zip(predictions, targets))
    return correct / len(predictions) if predictions else 0.0


def format_conversation_history(messages: List[Dict]) -> str:
    """
    Formatea el historial de conversación para mostrar
    """
    formatted = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        formatted.append(f"[{timestamp}] {role}: {content}")
    
    return "\n".join(formatted)
