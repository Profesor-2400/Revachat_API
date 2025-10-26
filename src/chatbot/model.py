"""
Modelo de IA para el chatbot de viajes usando Gemini
"""
import google.generativeai as genai
from typing import List, Dict, Optional
from loguru import logger
from config import settings


class TravelChatbotModel:
    """
    Clase principal del chatbot de viajes con Gemini
    """
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Define el prompt del sistema que le da personalidad y contexto al chatbot
        """
        return """Eres un asistente de viajes experto y amigable especializado en ayudar a las personas a planificar sus vacaciones perfectas.

Tu especialidad incluye:
- 🛫 Recomendaciones de vuelos y aerolíneas
- 🌍 Información sobre países, ciudades y atracciones
- 💰 Consejos sobre presupuestos y mejores épocas para viajar
- 📋 Tips de viaje, visas, y requisitos

Características de tu personalidad:
- Eres entusiasta y motivador sobre los viajes
- Das recomendaciones personalizadas según las preferencias del usuario
- Preguntas para entender mejor las necesidades (presupuesto, fechas, intereses)
- Ofreces varias opciones cuando es posible
- Incluyes información práctica y útil

Formato de respuestas:
- Usa emojis relevantes para hacer las respuestas más visuales
- Organiza la información con bullets o numeraciones
- Sé conciso pero completo
- Pregunta si el usuario necesita más detalles

Recuerda: Tu objetivo es hacer que planificar un viaje sea fácil y emocionante."""

    def load_model(self):
        """
        Inicializa el modelo Gemini con la API key
        """
        try:
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno")
            
            logger.info(f"Inicializando Gemini: {settings.gemini_model}")
            genai.configure(api_key=settings.gemini_api_key)
            
            # Configuración de generación
            generation_config = {
                "temperature": settings.temperature,
                "top_p": settings.top_p,
                "top_k": settings.top_k,
                "max_output_tokens": settings.max_tokens,
            }
            
            # Configuración de seguridad (ajustable según necesidades)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
            
            self.model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self.is_loaded = True
            logger.success("Modelo Gemini cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cargar Gemini: {str(e)}")
            raise
    
    def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Genera una respuesta usando Gemini basada en el mensaje del usuario
        
        Args:
            message: Mensaje del usuario
            conversation_history: Historial de la conversación en formato [{"role": "user/model", "parts": "texto"}]
            
        Returns:
            Respuesta generada por Gemini
        """
        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")
        
        try:
            # Iniciar chat con historial si existe
            history = conversation_history if conversation_history else []
            
            # Agregar el system prompt como primer mensaje
            if not history:
                history = [{"role": "model", "parts": self.system_prompt}]
            
            chat = self.model.start_chat(history=history)
            
            # Generar respuesta
            response = chat.send_message(message)
            
            logger.info(f"Respuesta generada exitosamente para: {message[:50]}...")
            return response.text
            
        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            raise
    
    def generate_streaming_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None,
    ):
        """
        Genera una respuesta en streaming (para respuestas en tiempo real)
        
        Args:
            message: Mensaje del usuario
            conversation_history: Historial de la conversación
            
        Yields:
            Chunks de texto de la respuesta
        """
        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")
        
        try:
            # Iniciar chat con historial si existe
            history = conversation_history if conversation_history else []
            
            # Agregar el system prompt como primer mensaje
            if not history:
                history = [{"role": "model", "parts": self.system_prompt}]
            
            chat = self.model.start_chat(history=history)
            
            # Generar respuesta en streaming
            response = chat.send_message(message, stream=True)
            
            for chunk in response:
                yield chunk.text
                
        except Exception as e:
            logger.error(f"Error en streaming: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        """
        Obtiene información sobre el modelo
        """
        return {
            "model_name": settings.gemini_model,
            "is_loaded": self.is_loaded,
            "provider": "Google Gemini",
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens
        }
    
    def count_tokens(self, text: str) -> int:
        """
        Cuenta los tokens en un texto
        """
        try:
            return self.model.count_tokens(text).total_tokens
        except Exception as e:
            logger.error(f"Error al contar tokens: {str(e)}")
            return 0


# Instancia global del modelo (singleton)
chatbot_model = TravelChatbotModel()
