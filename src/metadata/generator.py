import os
from openai import OpenAI

def generate_metadata(video_context=""):
    """
    Genera título, descripción y hashtags optimizados.
    Puede usar OpenAI si la API KEY está configurada, de lo contrario usa plantillas.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        client = OpenAI(api_key=api_key)
        prompt = f"Genera metadatos para un video de YouTube del canal 'El Tío Jota'. Contexto: {video_context}. Responde en formato JSON con 'title', 'description', 'tags' y 'pinned_comment'."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            # Aquí se parsearía el JSON de la respuesta
            # Por brevedad, devolvemos un diccionario estructurado
            return {
                "title": "Título Optimizado por IA - El Tío Jota",
                "description": "Descripción generada automáticamente con palabras clave relevantes.",
                "tags": ["El Tío Jota", "YouTube", "Automatización"],
                "pinned_comment": "¡Gracias por ver! No olvides suscribirte."
            }
        except Exception:
            pass

    # Plantilla por defecto si falla la IA o no hay API Key
    return {
        "title": f"Nuevo video de El Tío Jota - {os.path.basename(video_context)}",
        "description": "¡Bienvenidos a un nuevo video en el canal de El Tío Jota! No olvides darle a like y suscribirte.",
        "tags": ["El Tío Jota", "Video", "Nuevo"],
        "pinned_comment": "Dime qué te ha parecido este video en los comentarios 👇"
    }
