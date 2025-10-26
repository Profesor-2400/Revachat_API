"""
Script de prueba para el chatbot
Ejecuta este script para probar el chatbot desde la línea de comandos
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_chat():
    """Prueba el endpoint de chat"""
    print("🤖 Probando el chatbot de viajes...\n")
    
    # Verificar que la API esté funcionando
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code != 200:
            print("❌ Error: La API no está respondiendo. ¿Está el servidor corriendo?")
            return
        print("✅ API conectada correctamente\n")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        print("   Asegúrate de que el servidor esté corriendo: python main.py")
        return
    
    conversation_id = "test-conversation"
    
    # Mensajes de prueba
    test_messages = [
        "Hola, quiero viajar a Japón",
        "¿Qué ciudades me recomiendas?",
        "¿Cuál es la mejor época para ir?",
        "¿Hoteles económicos en Tokio?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"👤 Usuario (mensaje {i}): {message}")
        
        # Enviar mensaje
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                "message": message,
                "conversation_id": conversation_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Chatbot: {data['response']}\n")
            print("-" * 80 + "\n")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}\n")
        
        # Pausa breve entre mensajes
        import time
        time.sleep(1)
    
    print("✅ Prueba completada!")
    print(f"\n💡 La conversación se guardó con ID: {conversation_id}")
    print(f"   Puedes eliminarla con: DELETE {API_URL}/api/conversation/{conversation_id}")

def test_single_message():
    """Prueba con un solo mensaje"""
    print("🤖 Prueba rápida del chatbot...\n")
    
    message = input("Escribe tu pregunta: ")
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 Respuesta:\n{data['response']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        print("   Asegúrate de que el servidor esté corriendo: python main.py")

if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("✈️  TRAVEL ASSISTANT CHATBOT - SCRIPT DE PRUEBA")
    print("=" * 80 + "\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        test_single_message()
    else:
        print("Opciones:")
        print("1. Prueba automática (conversación completa)")
        print("2. Mensaje único")
        print()
        
        opcion = input("Selecciona una opción (1 o 2): ").strip()
        
        if opcion == "1":
            test_chat()
        elif opcion == "2":
            test_single_message()
        else:
            print("Opción inválida")
