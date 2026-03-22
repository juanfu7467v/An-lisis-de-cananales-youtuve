import os
import logging
import json
from googleapiclient.discovery import build
from datetime import datetime
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
    Flujo principal: Escucha Activa (Comentarios de YouTube) -> YouTube Search Validation -> IA Title Transformation.
    """
    logger.info("Iniciando detección de tendencias basada en Escucha Activa (Comentarios y YouTube).")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("Falta YOUTUBE_API_KEY para la Escucha Activa.")
        return None

    potential_topics = []
    channel_data = {"recent_performance": [], "audience_comments": []}

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # 1. Obtener los últimos videos del canal para extraer comentarios
        if channel_id:
            logger.info(f"Extrayendo comentarios del canal: {channel_id}")
            search_response = youtube.search().list(
                channelId=channel_id,
                part="id,snippet",
                order="date",
                maxResults=5,
                type="video"
            ).execute()

            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            if video_ids:
                videos_stats = youtube.videos().list(
                    part="snippet,statistics",
                    id=",".join(video_ids)
                ).execute()

                for v in videos_stats.get("items", []):
                    v_id = v["id"]
                    stats = v["statistics"]
                    snippet = v["snippet"]
                    
                    channel_data["recent_performance"].append({
                        "title": snippet["title"],
                        "views": stats.get("viewCount", 0),
                        "likes": stats.get("likeCount", 0)
                    })

                    # Obtener comentarios para detectar peticiones
                    try:
                        comments_response = youtube.commentThreads().list(
                            part="snippet",
                            videoId=v_id,
                            maxResults=20,
                            order="relevance"
                        ).execute()

                        for c in comments_response.get("items", []):
                            comment_text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                            channel_data["audience_comments"].append(comment_text)
                    except Exception as ce:
                        logger.warning(f"No se pudieron obtener comentarios para el video {v_id}: {ce}")

        # 2. Usar IA para identificar temas sugeridos por la audiencia o temas relacionados con el éxito actual
        if channel_data["audience_comments"] or channel_data["recent_performance"]:
            logger.info("Analizando comentarios y rendimiento con IA para detectar temas...")
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                prompt = f"""
                Analiza los siguientes comentarios y el rendimiento de los videos recientes de un canal de YouTube.
                Identifica 5 temas de alta demanda o curiosidades que la audiencia esté pidiendo o que tengan relación con los videos más exitosos.
                
                RENDIMIENTO RECIENTE:
                {json.dumps(channel_data['recent_performance'], indent=2)}
                
                COMENTARIOS DE LA AUDIENCIA:
                {json.dumps(channel_data['audience_comments'][:50], indent=2)}
                
                Responde ÚNICAMENTE con una lista de 5 temas cortos (ej: "El secreto de la Atlántida", "Teoría sobre el Joker").
                """
                response = model.generate_content(prompt)
                extracted_topics = response.text.strip().split('\n')
                potential_topics = [t.strip('- ').strip() for t in extracted_topics if t.strip()]
                logger.info(f"✓ Temas detectados por Escucha Activa: {potential_topics}")

    except Exception as e:
        logger.error(f"Error en el proceso de Escucha Activa: {e}")

    # Si no hay temas de comentarios, usar tendencias generales de YouTube como último recurso
    if not potential_topics:
        logger.info("No se detectaron temas en comentarios. Usando tendencias generales de YouTube.")
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            trends_response = youtube.videos().list(
                part="snippet",
                chart="mostPopular",
                regionCode="PE",
                maxResults=5
            ).execute()
            potential_topics = [item["snippet"]["title"] for item in trends_response.get("items", [])]
        except Exception as e:
            logger.error(f"Error al obtener tendencias generales: {e}")

    if not potential_topics:
        logger.warning("No se encontraron temas potenciales. El sistema NO generará contenido.")
        return None

    validated_trends = []
    for topic in potential_topics[:10]:
        logger.info(f"Validando tema: '{topic}'")
        avg_views = _get_youtube_search_views(topic)

        if avg_views > 500000:
            priority = "ALTA" if avg_views > 1000000 else "NORMAL"
            logger.info(f"✓ Tema aprobado: '{topic}' con prioridad {priority} ({avg_views:.0f} vistas).")
            
            transformed_title = _transform_title_with_ia(topic)
            logger.info(f"✓ Título viral generado: '{transformed_title}'")
            
            format_sugerido = "Short"
            if any(word in topic.lower() for word in ["análisis", "secreto", "teoría", "historia", "por qué", "explicación"]):
                format_sugerido = "Video largo"

            validated_trends.append({
                "original_topic": topic,
                "transformed_title": transformed_title,
                "avg_youtube_views": avg_views,
                "format_sugerido": format_sugerido,
                "priority": priority,
                "potential_category": "escucha_activa"
            })
        else:
            logger.info(f"✗ Tema rechazado: '{topic}'. Vistas insuficientes ({avg_views:.0f}).")

    if not validated_trends:
        logger.warning("Ningún tema de la Escucha Activa superó el filtro de 500K vistas.")
        return None

    validated_trends.sort(key=lambda x: x["avg_youtube_views"], reverse=True)
    
    return {
        "validated_trends": validated_trends,
        "channel_specific": channel_data
    }
