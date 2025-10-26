"""
Ejemplos de conversaciones para probar el chatbot de viajes
"""

EJEMPLOS_CONVERSACIONES = {
    "viaje_familiar": [
        "Hola, quiero planear un viaje familiar a Europa",
        "Somos 4 personas, 2 adultos y 2 niños",
        "¿Qué países son más amigables para niños?",
        "¿Cuánto presupuesto necesitaría aproximadamente?",
        "¿Mejor en verano o primavera?"
    ],
    
    "luna_de_miel": [
        "Busco destinos románticos para luna de miel",
        "Presupuesto alto, queremos lujo",
        "Preferimos playas paradisíacas",
        "¿Maldivas o Bora Bora?",
        "¿Mejores hoteles en el destino que recomiendes?"
    ],
    
    "mochilero": [
        "Quiero viajar como mochilero por Sudamérica",
        "Tengo 3 meses disponibles",
        "Presupuesto bajo, $50 por día máximo",
        "¿Por dónde empiezo?",
        "¿Necesito visas?"
    ],
    
    "viaje_negocios": [
        "Necesito viajar a Tokio por negocios",
        "¿Hoteles cerca del distrito financiero?",
        "¿Mejor aerolínea desde México?",
        "¿Qué debo saber sobre etiqueta de negocios en Japón?"
    ],
    
    "aventura": [
        "Me encanta la aventura y deportes extremos",
        "¿Destinos para hacer paracaidismo?",
        "También me interesa el buceo",
        "¿Nueva Zelanda sería buena opción?",
        "¿Qué época del año es mejor?"
    ],
    
    "cultural": [
        "Busco un viaje cultural e histórico",
        "Me fascina la historia antigua",
        "¿Egipto, Grecia o Roma?",
        "Tengo 2 semanas disponibles",
        "¿Puedo combinar varios países?"
    ]
}

PREGUNTAS_COMUNES = [
    "¿Cuál es el mejor momento para comprar vuelos baratos?",
    "¿Cómo encuentro hoteles económicos pero buenos?",
    "¿Necesito seguro de viaje?",
    "¿Qué documentos necesito para viajar internacional?",
    "¿Cómo evitar el jet lag?",
    "¿Es seguro viajar solo?",
    "¿Cuánto dinero debo llevar en efectivo?",
    "¿Mejor cambiar dinero antes o después de llegar?",
    "¿Qué vacunas necesito?",
    "¿Puedo usar mi celular en el extranjero?"
]

DESTINOS_POPULARES = [
    "París, Francia",
    "Tokio, Japón",
    "Nueva York, USA",
    "Barcelona, España",
    "Roma, Italia",
    "Dubai, EAU",
    "Bangkok, Tailandia",
    "Londres, Reino Unido",
    "Cancún, México",
    "Bali, Indonesia"
]

def obtener_ejemplo(tipo: str) -> list:
    """Obtiene un ejemplo de conversación por tipo"""
    return EJEMPLOS_CONVERSACIONES.get(tipo, [])

def listar_ejemplos() -> list:
    """Lista todos los tipos de ejemplos disponibles"""
    return list(EJEMPLOS_CONVERSACIONES.keys())

if __name__ == "__main__":
    print("📝 Ejemplos de conversaciones disponibles:\n")
    for tipo in listar_ejemplos():
        print(f"- {tipo}")
        conversacion = obtener_ejemplo(tipo)
        for i, msg in enumerate(conversacion, 1):
            print(f"  {i}. {msg}")
        print()
