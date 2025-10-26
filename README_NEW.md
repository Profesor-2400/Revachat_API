# ✈️ Travel Assistant Chatbot API

API REST construida con FastAPI y Google Gemini para un chatbot inteligente de asistencia de viajes. Especializado en recomendar vuelos, hoteles, destinos turísticos y todo lo relacionado con planificación de viajes.

## 🚀 Características

- ✅ API REST con FastAPI
- 🤖 Integración con Google Gemini AI
- ✈️ Recomendaciones de vuelos y aerolíneas
- 🏨 Sugerencias de hoteles y alojamientos
- 🗺️ Información sobre destinos turísticos
- 💬 Conversaciones contextuales (memoria de chat)
- 🔄 Respuestas en tiempo real (streaming)
- 📊 Sistema de logging avanzado

## 🎯 Especialidades del Chatbot

El chatbot está especializado en:
- Recomendaciones de vuelos y mejores aerolíneas
- Sugerencias de hoteles según presupuesto
- Destinos turísticos populares y escondidos
- Información sobre países, ciudades y atracciones
- Consejos sobre presupuestos y mejores épocas para viajar
- Tips de viaje, visas y requisitos

## 📋 Requisitos

- Python 3.10+
- Google Gemini API Key (gratuita en https://aistudio.google.com/app/apikey)
- pip

## 🛠️ Instalación

### 1. **Navegar al proyecto**
```bash
cd api-chatv
```

### 2. **Crear entorno virtual**
```bash
python -m venv venv
```

### 3. **Activar entorno virtual**
```bash
# Windows PowerShell
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### 5. **Configurar API Key de Gemini**

1. Visita https://aistudio.google.com/app/apikey
2. Crea una API Key (es gratuita)
3. Copia el archivo `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```
4. Edita `.env` y pega tu API key:
   ```
   GEMINI_API_KEY=tu_api_key_aqui
   ```

## 🎯 Uso

### Iniciar el servidor

```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn main:app --reload --port 8000
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva

- **Swagger UI**: `http://localhost:8000/docs` (recomendado para probar)
- **ReDoc**: `http://localhost:8000/redoc`

## 📡 Endpoints Principales

### 💬 Chat Normal
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Quiero viajar a Japón en primavera, ¿qué me recomiendas?",
  "conversation_id": "user123-conv1"
}
```

**Respuesta:**
```json
{
  "response": "¡Japón en primavera es espectacular! 🌸...",
  "conversation_id": "user123-conv1",
  "timestamp": "2025-10-26T10:30:00"
}
```

### ⚡ Chat con Streaming (tiempo real)
```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "¿Cuáles son los mejores hoteles en París?",
  "conversation_id": "user123-conv1"
}
```

### 🗑️ Limpiar conversación
```http
DELETE /api/conversation/{conversation_id}
```

### 📊 Info del modelo
```http
GET /api/model/info
```

### ❤️ Health Check
```http
GET /health
```

## 📁 Estructura del Proyecto

```
api-chatv/
│
├── main.py                    # Aplicación FastAPI principal
├── config.py                  # Configuración centralizada
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno (NO subir a git)
├── .env.example              # Ejemplo de configuración
├── .gitignore                # Archivos ignorados
├── README.md                 # Este archivo
│
├── logs/                     # Logs de la aplicación
│   └── chatbot_*.log
│
├── data/                     # Datos (si se necesitan)
│   └── .gitkeep
│
├── src/                      # Código fuente
│   ├── __init__.py
│   │
│   ├── chatbot/             # Lógica del chatbot
│   │   ├── __init__.py
│   │   └── model.py         # Integración con Gemini
│   │
│   ├── database/            # Base de datos
│   │   └── __init__.py
│   │
│   └── utils/               # Utilidades
│       └── __init__.py
│
└── tests/                   # Tests
    └── __init__.py
```

## 🧪 Ejemplos de Uso

### Ejemplo 1: Búsqueda de destino
```json
{
  "message": "Busco un destino paradisíaco para luna de miel, presupuesto alto"
}
```

### Ejemplo 2: Recomendación de vuelos
```json
{
  "message": "¿Cuál es la mejor aerolínea para volar a Europa desde América?"
}
```

### Ejemplo 3: Hoteles económicos
```json
{
  "message": "Necesito hoteles baratos en Barcelona para 3 noches"
}
```

### Ejemplo 4: Contexto conversacional
```json
// Primera pregunta
{
  "message": "Quiero viajar a Italia",
  "conversation_id": "conv123"
}

// Segunda pregunta (recuerda el contexto)
{
  "message": "¿Qué ciudades me recomiendas visitar?",
  "conversation_id": "conv123"
}
```

## ⚙️ Configuración Avanzada

### Cambiar modelo de Gemini
En `.env`:
```bash
GEMINI_MODEL=gemini-pro  # Más potente pero más lento
# o
GEMINI_MODEL=gemini-1.5-flash  # Más rápido (recomendado)
```

### Ajustar creatividad
```bash
TEMPERATURE=0.8  # Mayor = más creativo (0.0 - 1.0)
```

### Memoria de conversación
```bash
CONVERSATION_MEMORY_TURNS=10  # Recuerda últimos 10 mensajes
```

## 🚀 Próximas Mejoras

- [ ] Integración con APIs de vuelos reales (Amadeus, Skyscanner)
- [ ] Integración con APIs de hoteles (Booking.com, Expedia)
- [ ] Base de datos para persistir conversaciones
- [ ] Sistema de usuarios y autenticación
- [ ] Cache de respuestas comunes
- [ ] Análisis de sentimientos
- [ ] Exportar conversaciones a PDF
- [ ] Panel de administración

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY no está configurada"
- Verifica que el archivo `.env` existe y tiene la API key correcta
- Asegúrate de que la variable se llama exactamente `GEMINI_API_KEY`

### Error: "No se ha podido resolver la importación"
- Ejecuta: `pip install -r requirements.txt`
- Asegúrate de tener el entorno virtual activado

### El chatbot no responde bien
- Verifica que tienes la API key correcta
- Revisa los logs en `logs/chatbot_*.log`
- Intenta con el modelo `gemini-1.5-flash` que es más rápido

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 📧 Contacto

Andrés Díaz - Desarrollador

---

**¡Construido con ❤️ usando FastAPI y Google Gemini!**
