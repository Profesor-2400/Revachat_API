# 🤖 API Chatbot con IA

API REST construida con FastAPI para entrenar y utilizar un chatbot basado en Inteligencia Artificial.

## 🚀 Características

- ✅ API REST con FastAPI
- 🤖 Integración con modelos de IA (Transformers, PyTorch)
- 📚 Sistema de entrenamiento personalizado
- 💾 Persistencia de conversaciones
- 🔄 Actualización en tiempo real
- 📊 Monitoreo del estado del modelo

## 📋 Requisitos

- Python 3.8+
- pip

## 🛠️ Instalación

1. **Clonar o navegar al proyecto**
```bash
cd api-chatv
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
cp .env.example .env
# Edita el archivo .env con tus configuraciones
```

## 🎯 Uso

### Iniciar el servidor

```bash
python main.py
```

O con uvicorn:
```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 Endpoints Principales

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Hola, ¿cómo estás?",
  "conversation_id": "optional-id"
}
```

### Entrenamiento
```http
POST /train
Content-Type: application/json

[
  {
    "question": "¿Qué es FastAPI?",
    "answer": "FastAPI es un framework web moderno y rápido para Python",
    "category": "tecnología"
  }
]
```

### Estado del Modelo
```http
GET /model/status
```

## 📁 Estructura del Proyecto

```
api-chatv/
│
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración de la app
├── requirements.txt       # Dependencias Python
├── .env.example          # Ejemplo de variables de entorno
├── .gitignore            # Archivos ignorados por git
├── README.md             # Este archivo
│
├── models/               # Modelos entrenados
│   └── .gitkeep
│
├── data/                 # Datos de entrenamiento
│   └── .gitkeep
│
├── src/                  # Código fuente
│   ├── __init__.py
│   ├── chatbot/         # Lógica del chatbot
│   │   ├── __init__.py
│   │   ├── model.py     # Modelo de IA
│   │   └── trainer.py   # Entrenamiento
│   │
│   ├── database/        # Base de datos
│   │   ├── __init__.py
│   │   └── models.py    # Modelos de BD
│   │
│   └── utils/           # Utilidades
│       ├── __init__.py
│       └── helpers.py
│
└── tests/               # Tests
    └── __init__.py
```

## 🧠 Próximos Pasos

1. Implementar la lógica del modelo de IA en `src/chatbot/model.py`
2. Crear el sistema de entrenamiento en `src/chatbot/trainer.py`
3. Configurar la base de datos para almacenar conversaciones
4. Agregar autenticación y autorización
5. Implementar sistema de logging
6. Crear tests unitarios

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 📧 Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Project Link: [https://github.com/tu-usuario/api-chatv](https://github.com/tu-usuario/api-chatv)
