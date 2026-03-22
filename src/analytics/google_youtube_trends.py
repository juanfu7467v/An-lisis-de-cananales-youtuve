import os
import logging
import json
import random
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)

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
            logger.warning(f"No se encontraron videos en YouTube para la búsqueda: '{query}'")
            return 0

        videos_stats = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        total_views = 0
        for item in videos_stats.get("items", []):
            total_views += int(item["statistics"].get("viewCount", 0))
        
        avg_views = total_views / len(video_ids)
        logger.info(f"✓ Validación de vistas en YouTube para '{query}': {avg_views:.0f} vistas promedio.")
        return avg_views

    except Exception as e:
        logger.error(f"Error al obtener vistas de YouTube para '{query}': {e}")
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
        logger.error(f"Error al transformar título con IA para '{trend_topic}': {e}")
        return trend_topic

def get_validated_trends(channel_id=None):
    """
    Flujo principal: Google Trends (Perú) -> YouTube Search Validation -> IA Title Transformation.
    """
    logger.info("Iniciando detección de tendencias con Google Trends (Perú) y validación de YouTube.")
    
    daily_trends_list = []
    # 1. Obtener tendencias diarias de Google Trends para Perú
    try:
        # Configuración específica para Perú
        pytrends = TrendReq(hl='es-PE', tz=360, timeout=(15, 15))
        daily_trends = pytrends.trending_searches(pn='peru')
        
        if not daily_trends.empty:
            daily_trends_list = daily_trends.iloc[:, 0].tolist()
            logger.info(f"✓ Tendencia obtenida de Google Trends (Perú): {len(daily_trends_list)} temas encontrados.")
        else:
            logger.warning("Google Trends no devolvió datos para Perú.")
    except Exception as e:
        logger.error(f"Error crítico al consultar Google Trends: {e}")

    if not daily_trends_list:
        logger.warning("No se encontraron tendencias reales. El sistema NO generará contenido (fallback eliminado).")
        return None

    validated_trends = []
    # Procesar máximo 10 tendencias para optimizar tiempo y cuotas de API
    for trend_topic in daily_trends_list[:10]:
        logger.info(f"Analizando tendencia potencial: '{trend_topic}'")
        
        # 2. Validación con YouTube Search
        avg_views = _get_youtube_search_views(trend_topic)

        # 3. Reglas de validación (Filtro Real de Viralidad)
        if avg_views > 500000:
            priority = "ALTA" if avg_views > 1000000 else "NORMAL"
            logger.info(f"✓ Tendencia aprobada: '{trend_topic}' con prioridad {priority} ({avg_views:.0f} vistas).")
            
            # 4. Transformación con IA
            transformed_title = _transform_title_with_ia(trend_topic)
            logger.info(f"✓ Título viral generado: '{transformed_title}'")
            
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
                "potential_category": "trending"
            })
        else:
            reason = "Vistas insuficientes (< 500,000)"
            logger.info(f"✗ Tendencia rechazada: '{trend_topic}'. Motivo: {reason} ({avg_views:.0f} vistas).")

    if not validated_trends:
        logger.warning("Ninguna tendencia de hoy superó el filtro de viralidad de 500K vistas.")
        return None

    # Ordenar por vistas para priorizar lo más viral
    validated_trends.sort(key=lambda x: x['avg_youtube_views'], reverse=True)
    
    return {"validated_trends": validated_trends}
