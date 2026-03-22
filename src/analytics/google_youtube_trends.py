
import os
import logging
import json
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)

def _get_google_trends(keyword):
    pytrends = TrendReq(hl='es-ES', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe='now 1-d', geo='ES', gprop='')
    data = pytrends.interest_over_time()
    if not data.empty:
        return data[keyword].iloc[-1] # Último valor de interés
    return 0

def _get_youtube_search_views(query):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("Falta YOUTUBE_API_KEY para la validación de YouTube Search.")
        return 0

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            order="viewCount",
            maxResults=5
        ).execute()

        total_views = 0
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            return 0

        videos_stats = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        for item in videos_stats.get("items", []):
            total_views += int(item["statistics"].get("viewCount", 0))
        
        return total_views / len(video_ids) if video_ids else 0 # Promedio de vistas

    except Exception as e:
        logger.error(f"Error al obtener vistas de YouTube para '{query}': {e}")
        return 0

def _transform_title_with_ia(trend_topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY para la transformación de títulos con IA.")
        return trend_topic # Retorna el original si no hay API key

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Actúa como un experto en marketing de YouTube. Transforma el siguiente tema de tendencia en un título de video altamente atractivo y clickbait que aumente el CTR. Debe ser intrigante, generar curiosidad y ser emocionalmente resonante.

        Tema: "{trend_topic}"

        Ejemplo de transformación:
        Entrada: "Spider Man"
        Salida: "El secreto oscuro de Spider-Man que nadie entendió"

        Salida (solo el título transformado):
        """
        response = model.generate_content(prompt)
        transformed_title = response.text.strip().replace('"', '')
        return transformed_title if transformed_title else trend_topic

    except Exception as e:
        logger.error(f"Error al transformar título con IA para '{trend_topic}': {e}")
        return trend_topic

def get_validated_trends(channel_id=None):
    logger.info("Iniciando detección de tendencias con Google Trends y validación de YouTube.")
    
    daily_trends_list = []
    # 1. Obtener tendencias diarias y búsquedas en crecimiento de Google Trends
    try:
        pytrends = TrendReq(hl='es-ES', tz=360, timeout=(10, 10))
        daily_trends = pytrends.trending_searches(pn='united_states') # Usamos US por defecto, se puede parametrizar
        # Convertir a lista de strings
        daily_trends_list = daily_trends.iloc[:, 0].tolist() if not daily_trends.empty else []
    except Exception as e:
        logger.warning(f"Error al inicializar o consultar Google Trends: {e}")
    

    # Búsquedas en crecimiento (rising queries) - No hay una API directa para esto en pytrends para un timeframe 'now 1-d'
    # Se podría simular buscando términos relacionados con las tendencias diarias y viendo su interés.
    # Por simplicidad, nos centraremos en las tendencias diarias y las validaremos.
    
    potential_trends = daily_trends_list # + rising_queries_list (si se implementa)
    
    if not potential_trends:
        logger.warning("No se encontraron tendencias potenciales de Google Trends. Usando temas de respaldo basados en intereses del canal.")
        # Fallback: Usar temas de interés general que suelen ser virales/emocionales
        potential_trends = ["Misterios sin resolver", "Curiosidades impactantes", "Teorías conspirativas famosas", "Secretos oscuros de la historia"]
    

    validated_trends = []
    for trend_topic in potential_trends:
        logger.info(f"Analizando tendencia: '{trend_topic}'")
        
        # Filtrar tendencias reales (alto volumen, actuales, virales/emocionales)
        # La API de pytrends ya nos da tendencias actuales. El volumen y la virilidad
        # se infieren de que sea una tendencia. La validación de YouTube confirmará el interés.
        
        # 2. Validación con YouTube
        avg_views = _get_youtube_search_views(trend_topic)
        logger.info(f"Promedio de vistas en YouTube para '{trend_topic}': {avg_views:.0f}")

        if avg_views >= 100000: # Más de 100K vistas -> CREAR VIDEO
            logger.info(f"✓ Tendencia '{trend_topic}' validada con éxito (>{avg_views:.0f} vistas).")
            transformed_title = _transform_title_with_ia(trend_topic)
            
            # Detección de formato automático (simplificado por ahora)
            # Si el tema es viral (alta validación), sugerir Short. Si es más de análisis, Video largo.
            # Por ahora, si pasa la validación de 100K, asumimos que es viral y sugerimos Short.
            # Esto se puede refinar con un análisis de texto del trend_topic.
            format_sugerido = "Short" # Default para tendencias virales
            if "análisis" in trend_topic.lower() or "secreto" in trend_topic.lower() or "teoría" in trend_topic.lower():
                format_sugerido = "Video largo"

            validated_trends.append({
                "original_topic": trend_topic,
                "transformed_title": transformed_title,
                "avg_youtube_views": avg_views,
                "format_sugerido": format_sugerido,
                "potential_category": "trending", # Se puede refinar con IA
                "emotional_appeal": True # Asumimos que una tendencia viral tiene atractivo emocional
            })
        elif avg_views < 50000: # Menos de 50K vistas -> DESCARTAR
            logger.info(f"✗ Tendencia '{trend_topic}' descartada (<{avg_views:.0f} vistas).")
        else:
            logger.info(f"Tendencia '{trend_topic}' en zona gris ({avg_views:.0f} vistas). Descartando por seguridad.")

    if not validated_trends:
        logger.warning("Ninguna tendencia validada cumplió los criterios.")
        return None

    return {"validated_trends": validated_trends}


