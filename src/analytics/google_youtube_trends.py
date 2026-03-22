import os
import logging
import json
import random
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Países de Latinoamérica a consultar
LATAM_COUNTRIES = {
    "PE": {"hl": "es-PE", "pn": "peru"},
    "MX": {"hl": "es-MX", "pn": "mexico"},
    "AR": {"hl": "es-AR", "pn": "argentina"},
    "CO": {"hl": "es-CO", "pn": "colombia"},
    "CL": {"hl": "es-CL", "pn": "chile"},
}

def _get_youtube_search_views(query):
    """
    Busca el término en YouTube y calcula el promedio de vistas de los primeros 5 videos.
    """
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

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            logger.warning(f"No se encontraron videos en YouTube para la búsqueda: {query}")
            return 0

        videos_stats = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        total_views = 0
        for item in videos_stats.get("items", []):
            total_views += int(item["statistics"].get("viewCount", 0))
        
        avg_views = total_views / len(video_ids)
        logger.info(f"✓ Validación de vistas en YouTube para {query}: {avg_views:.0f} vistas promedio.")
        return avg_views

    except Exception as e:
        logger.error(f"Error al obtener vistas de YouTube para {query}: {e}")
        return 0

def _transform_title_with_ia(trend_topic):
    """
    Usa IA para transformar una tendencia en un título emocional y viral.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY para la transformación de títulos con IA.")
        return trend_topic

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Actúa como un experto en marketing viral de YouTube. 
        
        TAREA: Convierte el siguiente tema en un TÍTULO ALTAMENTE VIRAL.
        
        REGLAS DE ORO:
        1. Debe generar CURIOSIDAD EXTREMA, EMOCIÓN o MISTERIO.
        2. No usar títulos genéricos.
        3. Usar estilo clickbait inteligente (sin mentir).
        4. Debe sonar como algo que el usuario NECESITA saber ahora mismo.

        EJEMPLO:
        Entrada: "gatos"
        Salida: "Por qué los gatos te observan mientras duermes (da miedo)"
        
        Entrada: "Spider Man"
        Salida: "El caso real que nadie pudo explicar sobre Spider-Man"

        TEMA A TRANSFORMAR: "{trend_topic}"

        Salida (solo el título transformado, sin comillas):
        """
        response = model.generate_content(prompt)
        transformed_title = response.text.strip().replace('"', '')
        return transformed_title if transformed_title else trend_topic

    except Exception as e:
        logger.error(f"Error al transformar título con IA para {trend_topic}: {e}")
        return trend_topic

def get_validated_trends(channel_id=None):
    """
    Flujo principal: Google Trends (Latinoamérica) -> YouTube Search Validation -> IA Title Transformation.
    """
    logger.info("Iniciando detección de tendencias con Google Trends (Latinoamérica) y validación de YouTube.")
    
    all_latam_trends = set() # Usar un set para evitar duplicados
    trends_with_origin = [] # Para guardar el origen de cada tendencia

    # 1. Obtener tendencias diarias de Google Trends para cada país de Latinoamérica
    for country_code, config in LATAM_COUNTRIES.items():
        hl = config["hl"]
        pn = config["pn"]
        logger.info(f"Consultando Google Trends para {pn.upper()} (hl={hl})...")
        try:
            pytrends = TrendReq(hl=hl, tz=360, timeout=(15, 15))
            daily_trends = pytrends.trending_searches(pn=pn)
            
            if not daily_trends.empty:
                country_trends = daily_trends.iloc[:, 0].tolist()
                logger.info(f"✓ {len(country_trends)} tendencias obtenidas de Google Trends para {pn.upper()}.")
                for trend in country_trends:
                    if trend not in all_latam_trends:
                        all_latam_trends.add(trend)
                        trends_with_origin.append({"topic": trend, "origin": pn.upper()})
            else:
                logger.warning(f"Google Trends no devolvió datos para {pn.upper()}.")
        except Exception as e:
            logger.error(f"Error al consultar Google Trends para {pn.upper()}: {e}")

    if not all_latam_trends:
        logger.warning("No se encontraron tendencias reales en ningún país de Latinoamérica. El sistema NO generará contenido.")
        return None

    validated_trends = []
    # Procesar máximo 20 tendencias combinadas para optimizar tiempo y cuotas de API
    for trend_item in trends_with_origin[:20]:
        trend_topic = trend_item["topic"]
        trend_origin = trend_item["origin"]
        logger.info(f"Analizando tendencia potencial de {trend_origin}: {trend_topic}")
        
        # 2. Validación con YouTube Search
        avg_views = _get_youtube_search_views(trend_topic)

        # 3. Reglas de validación (Filtro Real de Viralidad)
        if avg_views > 500000:
            priority = "ALTA" if avg_views > 1000000 else "NORMAL"
            logger.info(f"✓ Tendencia aprobada de {trend_origin}: {trend_topic} con prioridad {priority} ({avg_views:.0f} vistas).")
            
            # 4. Transformación con IA
            transformed_title = _transform_title_with_ia(trend_topic)
            logger.info(f"✓ Título viral generado: {transformed_title}")
            
            # Detección de formato automático
            format_sugerido = "Short"
            if any(word in trend_topic.lower() for word in ["análisis", "secreto", "teoría", "historia", "por qué", "explicación"]):
                format_sugerido = "Video largo"

            validated_trends.append({
                "original_topic": trend_topic,
                "transformed_title": transformed_title,
                "avg_youtube_views": avg_views,
                "format_sugerido": format_sugerido,
                "priority": priority,
                "potential_category": "trending",
                "origin_country": trend_origin
            })
        else:
            reason = "Vistas insuficientes (< 500,000)"
            logger.info(f"✗ Tendencia rechazada de {trend_origin}: {trend_topic}. Motivo: {reason} ({avg_views:.0f} vistas).")

    if not validated_trends:
        logger.warning("Ninguna tendencia de hoy superó el filtro de viralidad de 500K vistas en Latinoamérica.")
        return None

    # Ordenar por vistas para priorizar lo más viral
    validated_trends.sort(key=lambda x: x["avg_youtube_views"], reverse=True)
    
    return {"validated_trends": validated_trends}
