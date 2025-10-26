# Script de inicio rápido para Windows PowerShell
# Travel Assistant Chatbot API

Write-Host "🚀 Iniciando Travel Assistant Chatbot API..." -ForegroundColor Cyan

# Verificar si existe el entorno virtual
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  No se encontró el entorno virtual" -ForegroundColor Yellow
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Verificar si existe .env
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  No se encontró archivo .env" -ForegroundColor Yellow
    Write-Host "📋 Copiando .env.example a .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "" -ForegroundColor Yellow
    Write-Host "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu GEMINI_API_KEY" -ForegroundColor Red
    Write-Host "   Obtén tu API key en: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter cuando hayas configurado tu API key"
}

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Green
pip install -r requirements.txt

# Iniciar servidor
Write-Host ""
Write-Host "✅ Todo listo! Iniciando servidor..." -ForegroundColor Green
Write-Host "📍 API disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentación en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

python main.py
