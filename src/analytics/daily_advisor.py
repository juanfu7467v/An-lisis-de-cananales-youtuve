import os
import datetime
import logging
from src.metadata.generator import generate_metadata

logger = logging.getLogger(__name__)

def get_daily_recommendation():
    """
    Genera una recomendación diaria basada en tendencias y rendimiento histórico.
    """
    # En una implementación real, aquí se consultaría Google Trends o YouTube Search API
    # Por ahora, simulamos la obtención de una tendencia relevante para 'El Tío Jota'
    trends = [
        "Cómo Marco Aurelio enfrentaba la ansiedad moderna",
        "Hábitos estoicos para una mente inquebrantable",
        "La disciplina de Séneca en el siglo XXI",
        "Lecciones de Epicteto para el éxito personal"
    ]
    
    # Seleccionamos una tendencia (podría ser aleatoria o basada en fecha)
    today_index = datetime.datetime.now().day % len(trends)
    topic = trends[today_index]
    
    # Generamos metadatos sugeridos
    metadata = generate_metadata(f"Video sobre {topic}")
    
    # Simulamos la hora óptima basada en analíticas previas
    optimal_hour = "19:30"
    
    recommendation = {
        "topic": topic,
        "title": metadata['title'],
        "type": "Short" if datetime.datetime.now().weekday() < 5 else "Video Largo",
        "duration": "30-40 segundos" if datetime.datetime.now().weekday() < 5 else "8-12 minutos",
        "hashtags": metadata['tags'],
        "optimal_time": optimal_hour
    }
    
    return recommendation

def format_daily_message(rec):
    """
    Formatea la recomendación para el mensaje de Telegram.
    """
    msg = (
        f"☀️ *Buenos días, El Tío Jota*\n\n"
        f"Hoy se recomienda publicar un *{rec['type']}* sobre:\n"
        f"'{rec['topic']}'\n\n"
        f"📌 *Título sugerido:* {rec['title']}\n"
        f"⏱️ *Duración ideal:* {rec['duration']}\n"
        f"⏰ *Hora recomendada:* {rec['optimal_time']}\n"
        f"🏷️ *Hashtags:* {' '.join(['#' + t.replace(' ', '') for t in rec['hashtags']])}\n\n"
        f"¿Quieres que preparemos este contenido?"
    )
    return msg
