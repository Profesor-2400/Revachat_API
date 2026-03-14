# 🚀 GUÍA DE INICIO RÁPIDO

## Pasos para empezar:

### 1 - Obtener API Key de Gemini (GRATIS)
1. Ve a: https://aistudio.google.com/app/apikey
2. Haz clic en "Create API Key"
3. Copia la API key generada

### 2 - Configurar el proyecto
1. Abre el archivo `.env` en este proyecto
2. Pega tu API key en la línea:
   ```
   GEMINI_API_KEY=pega_tu_api_key_aqui
   ```
3. Guarda el archivo

### 3 - Instalar dependencias

**Opción A: Script automático (recomendado)**
```powershell
.\start.ps1
```

**Opción B: Manual**
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python main.py
```

### 4️⃣ Probar el chatbot

**En el navegador:**
- Abre: http://localhost:8000/docs
- Prueba el endpoint `/api/chat`

**Desde Python:**
```powershell
python test_chat.py
```

## 📝 Ejemplo de uso rápido

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Quiero viajar a París, ¿qué me recomiendas?"
    }
)

print(response.json()["response"])
```

## 🎯 Endpoints disponibles

- `GET /` - Información de la API
- `GET /health` - Estado del servidor
- `POST /api/chat` - Chatear con el bot
- `POST /api/chat/stream` - Chat en streaming
- `GET /api/model/info` - Info del modelo
- `DELETE /api/conversation/{id}` - Borrar conversación

## ❓ Problemas comunes

### Error: "GEMINI_API_KEY no está configurada"
→ Revisa que el archivo `.env` tenga tu API key correctamente

### Error: "No se pudo conectar"
→ Asegúrate de que el servidor esté corriendo (`python main.py`)

### Error al instalar dependencias
→ Actualiza pip: `python -m pip install --upgrade pip`

## 📚 Documentación completa
Ver `README_NEW.md` para documentación detallada.

---
¡Listo para viajar! ✈️🗺️
