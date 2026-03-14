"""
Modelo de IA para el chatbot de viajes usando Gemini
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from loguru import logger
from config import settings
import re

# =========================
# PROMPTS DEL SISTEMA
# =========================

# Prompt base para conversación general (con instrucciones anti-alucinación)
CONVERSATIONAL_PROMPT = """Eres un asistente virtual de viajes amable, cercano y profesional ✨✈️  
Tu objetivo es ayudar al usuario a planear su viaje de forma clara y agradable.

REGLAS IMPORTANTES:
- Responde saludos de forma cordial 😊
- Haz preguntas para conocer destino, fechas y presupuesto 💰
- Usa un lenguaje cercano y natural.
- **NO inventes información**. Si no sabes la respuesta a una pregunta específica (por ejemplo, políticas de equipaje de una aerolínea, precios exactos, disponibilidad), indícalo amablemente y sugiere al usuario consultar fuentes oficiales o preguntar de otra manera.
- Basa tus respuestas en conocimiento general de viajes. Si el usuario pide información muy específica que no puedes confirmar, responde con un aproximado o indica que no tienes datos suficientes.
- Mantén un tono útil y evita dar información falsa.
"""

# Prompt para recomendación de vuelos (ya tiene formato estricto y advertencia)
RECOMMENDER_PROMPT = """Eres un SISTEMA INTELIGENTE DE RECOMENDACIÓN DE VUELOS con fines académicos 📊✈️

REGLAS ESTRICTAS:
- Indica al usuario TRES opciones de vuelos según su presupuesto.
- Usa un lenguaje claro y conciso.
- NO saludes.
- Explica brevemente.
- SOLO responde en este formato.
- SIEMPRE genera TRES opciones:
  - Económica 💸
  - Calidad-Precio ⚖️
  - Premium 💎
- **No inventes aerolíneas, números de vuelo, horarios o precios**. Si no tienes información concreta, utiliza valores de referencia ficticios pero consistentes, y deja claro que son ejemplos ilustrativos.
- Incluye la advertencia final obligatoria.

FORMATO OBLIGATORIO:

Aerolínea (Tipo de servicio)
- Número de vuelo:
- Origen:
- Destino:
- Hora de salida:
- Tiempo de trayecto:
- Precio por trayecto:
- Escala: (Sí/No)

- Preguntar si tiene alguna otra consulta o duda.

AL FINAL SIEMPRE MUESTRA ESTE TEXTO LITERAL EN NEGRA CURSIVA:

"Los precios son y están sujetos a cambios por condiciones meteorológicas, disponibilidad, temporada u otros factores externos. Valores de referencia hasta la fecha."
"""

class TravelChatbotModel:
    """
    Clase principal del chatbot de viajes con Gemini
    """

    def __init__(self):
        self.model = None
        self.is_loaded = False

    # =========================
    # DETECTOR DE INTENCIÓN
    # =========================
    def is_flight_request(self, message: str) -> bool:
        patrones = [
            r"\$\s?\d+",
            r"\d+\s?(mil|millones|millón|cop)",
            r"presupuesto",
            r"quiero viajar",
            r"vuelo",
            r"aerolinea",
            r"viajar de .* a .*"
        ]

        mensaje = message.lower()
        return any(re.search(p, mensaje) for p in patrones)

    # =========================
    # RECUPERACIÓN DE CONOCIMIENTO (RAG) - Placeholder
    # =========================
    def retrieve_knowledge(self, query: str) -> str:
        """
        Busca información relevante en una base de conocimiento.
        Por ahora es un placeholder. En el futuro se conectará a un vector store.
        """
        # TODO: Implementar búsqueda vectorial real
        # Por ahora, retornamos vacío (sin contexto adicional)
        return ""

    # =========================
    # CARGA DEL MODELO
    # =========================
    def load_model(self):
        """
        Inicializa el modelo Gemini con la API key
        """
        try:
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno")

            logger.info(f"Inicializando Gemini: {settings.gemini_model}")
            genai.configure(api_key=settings.gemini_api_key)

            generation_config = {
                "temperature": settings.temperature,
                "top_p": settings.top_p,
                "top_k": settings.top_k,
                "max_output_tokens": settings.max_tokens,
            }

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]

            # Nota: No pasamos system_instruction aquí porque cambiará según la intención.
            # En su lugar, lo inyectaremos en cada llamada mediante el historial o usando start_chat.
            self.model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            self.is_loaded = True
            logger.success("Modelo Gemini cargado exitosamente")

        except Exception as e:
            logger.error(f"Error al cargar Gemini: {str(e)}")
            raise

    # =========================
    # GENERACIÓN NORMAL
    # =========================
    def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:

        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")

        try:
            # 1. Detectar intención para elegir el prompt de sistema
            if self.is_flight_request(message):
                system_prompt = RECOMMENDER_PROMPT
            else:
                system_prompt = CONVERSATIONAL_PROMPT

            # 2. (Opcional) Recuperar conocimiento relevante (RAG)
            knowledge = self.retrieve_knowledge(message)
            if knowledge:
                # Insertar el conocimiento recuperado al inicio del mensaje o como contexto adicional
                # Podríamos añadirlo al prompt de sistema o como un mensaje separado.
                # Por simplicidad, lo añadimos al prompt de sistema.
                system_prompt = f"Contexto útil:\n{knowledge}\n\n{system_prompt}"

            # 3. Construir el historial interno para el chat
            # El historial recibido (conversation_history) contiene los mensajes previos (user/assistant)
            # pero NO incluye el system_prompt. Debemos crear un nuevo historial que comience con el system_prompt
            # como un mensaje del usuario (para dar instrucciones) y luego agregar los mensajes reales.
            internal_history = []

            # Añadir el system_prompt como primer mensaje (rol user) para establecer las reglas
            internal_history.append({"role": "user", "parts": system_prompt})

            # Añadir los mensajes previos de la conversación si existen
            if conversation_history:
                # Nota: conversation_history ya viene con roles "user" y "assistant" (o "model")
                # Asegurarse de que los roles sean los correctos para Gemini: "user" y "model"
                for msg in conversation_history:
                    # Si el rol es "assistant", cambiarlo a "model"
                    role = msg["role"]
                    if role == "assistant":
                        role = "model"
                    internal_history.append({"role": role, "parts": msg["parts"]})

            # 4. Iniciar chat con el historial construido
            chat = self.model.start_chat(history=internal_history)

            # 5. Enviar el nuevo mensaje del usuario
            response = chat.send_message(message)

            logger.info(f"✉️ Respuesta generada exitosamente para: {message[:50]}...")
            return response.text

        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            raise

    # =========================
    # GENERACIÓN EN STREAMING
    # =========================
    def generate_streaming_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
    ):

        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")

        try:
            # Misma lógica que generate_response, pero con streaming
            if self.is_flight_request(message):
                system_prompt = RECOMMENDER_PROMPT
            else:
                system_prompt = CONVERSATIONAL_PROMPT

            knowledge = self.retrieve_knowledge(message)
            if knowledge:
                system_prompt = f"Contexto útil:\n{knowledge}\n\n{system_prompt}"

            internal_history = [{"role": "user", "parts": system_prompt}]

            if conversation_history:
                for msg in conversation_history:
                    role = msg["role"]
                    if role == "assistant":
                        role = "model"
                    internal_history.append({"role": role, "parts": msg["parts"]})

            chat = self.model.start_chat(history=internal_history)

            response = chat.send_message(message, stream=True)

            for chunk in response:
                yield chunk.text

        except Exception as e:
            logger.error(f"Error en streaming: {str(e)}")
            raise

    # =========================
    # METADATOS DEL MODELO
    # =========================
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

    # =========================
    # CONTADOR DE TOKENS
    # =========================
    def count_tokens(self, text: str) -> int:
        """
        Cuenta los tokens en un texto
        """
        try:
            return self.model.count_tokens(text).total_tokens
        except Exception as e:
            logger.error(f"Error al contar tokens: {str(e)}")
            return 0


# =========================
# INSTANCIA GLOBAL
# =========================
chatbot_model = TravelChatbotModel()