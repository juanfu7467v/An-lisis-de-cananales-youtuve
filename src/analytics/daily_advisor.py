import os
import datetime
import logging
from src.metadata.generator import generate_metadata
from src.analytics.content_strategy import get_content_type_for_day, get_theme_for_content_type, get_hook_for_format

logger = logging.getLogger(__name__)

def get_daily_recommendation():
    """
    Genera una recomendación diaria basada en la estrategia de rotación de contenido.
    Alterna entre Short, Video largo (análisis de película) y Video educativo (filosofía).
    """
    # Obtener el tipo de contenido para hoy según la rotación
    content_config = get_content_type_for_day()
    formato = content_config.get("formato")
    duracion = content_config.get("duracion")
    
    # Seleccionar un tema apropiado para el tipo de contenido
    topic = get_theme_for_content_type(content_config)
    
    # Generar metadatos sugeridos
    metadata = generate_metadata(f"Video sobre {topic}")
    
    # Obtener un hook impactante
    hook = get_hook_for_format(formato)
    
    # Simulamos la hora óptima basada en analíticas previas
    optimal_hour = "19:30"
    
    recommendation = {
        "topic": topic,
        "title": metadata['title'],
        "type": formato,
        "duration": duracion,
        "hashtags": metadata['tags'],
        "optimal_time": optimal_hour,
        "hook": hook,
        "style": content_config.get("estilo")
    }
    
    return recommendation

def format_daily_message(rec):
    """
    Formatea la recomendación para el mensaje de Telegram.
    Incluye información sobre el Super Prompt y la estrategia de contenido.
    """
    msg = (
        f"☀️ *Buenos días, El Tío Jota*\n\n"
        f"Hoy se recomienda publicar un *{rec['type']}* sobre:\n"
        f"'{rec['topic']}'\n\n"
        f"📌 *Título sugerido:* {rec['title']}\n"
        f"⏱️ *Duración ideal:* {rec['duration']}\n"
        f"⏰ *Hora recomendada:* {rec['optimal_time']}\n"
        f"🎯 *Estilo:* {rec.get('style', 'Profesional')}\n"
        f"🪝 *Hook inicial:* {rec.get('hook', 'Impactante')}\n"
        f"🏷️ *Hashtags:* {' '.join(['#' + t.replace(' ', '') for t in rec['hashtags']])}\n\n"
        f"Este contenido ha sido optimizado con nuestro sistema de Super Prompts para máxima retención.\n\n"
        f"¿Quieres que preparemos este contenido?"
    )
    return msg
