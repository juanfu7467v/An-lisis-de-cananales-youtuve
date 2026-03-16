import os
import logging
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

def get_youtube_trends(channel_id=None):
    """
    Analiza las tendencias actuales de YouTube utilizando videoCategories y videos.list (mostPopular).
    El parámetro channel_id se incluye para futura extensibilidad, pero no se usa para filtrar
    las tendencias populares generales.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("Falta YOUTUBE_API_KEY para analizar tendencias")
        return None

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # 1. Obtener categorías de video
        categories_request = youtube.videoCategories().list(
            part="snippet",
            regionCode="ES" # Se puede parametrizar o usar 'US'
        )
        categories_response = categories_request.execute()
        categories = {item["id"]: item["snippet"]["title"] for item in categories_response.get("items", [])}

        # 2. Obtener videos más populares
        videos_request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="ES",
            maxResults=10
        )
        videos_response = videos_request.execute()

        trends_data = []
        for item in videos_response.get("items", []):
            snippet = item["snippet"]
            category_id = snippet.get("categoryId")
            category_name = categories.get(category_id, "Unknown")
            
            trends_data.append({
                "title": snippet["title"],
                "category": category_name,
                "description": snippet["description"][:200],
                "tags": snippet.get("tags", [])
            })

        return trends_data

    except Exception as e:
        logger.error(f"Error al obtener tendencias de YouTube: {e}")
        return None
