import os
import logging
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

def get_youtube_trends(channel_id=None):
    """
    Analiza las tendencias actuales de YouTube utilizando videoCategories y videos.list (mostPopular).
    Si se proporciona channel_id, también obtiene información específica del canal.
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
            regionCode="ES"
        )
        categories_response = categories_request.execute()
        categories = {item["id"]: item["snippet"]["title"] for item in categories_response.get("items", [])}

        # 2. Obtener videos más populares (Tendencias generales)
        videos_request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="ES",
            maxResults=5
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
                "description": snippet["description"][:150],
                "tags": snippet.get("tags", [])[:5]
            })

        # 3. Análisis específico del canal (Si hay ID)
        channel_data = {}
        if channel_id:
            # Obtener los últimos videos del canal para ver engagement
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

                channel_videos = []
                all_comments = []
                
                for v in videos_stats.get("items", []):
                    v_id = v["id"]
                    stats = v["statistics"]
                    snippet = v["snippet"]
                    
                    channel_videos.append({
                        "title": snippet["title"],
                        "views": stats.get("viewCount", 0),
                        "likes": stats.get("likeCount", 0),
                        "comments_count": stats.get("commentCount", 0)
                    })

                    # Obtener comentarios de este video
                    try:
                        comments_response = youtube.commentThreads().list(
                            part="snippet",
                            videoId=v_id,
                            maxResults=10,
                            order="relevance"
                        ).execute()

                        for c in comments_response.get("items", []):
                            comment_text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                            author = c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                            all_comments.append({"author": author, "text": comment_text})
                    except Exception as ce:
                        logger.warning(f"No se pudieron obtener comentarios para el video {v_id}: {ce}")

                channel_data = {
                    "recent_performance": channel_videos,
                    "audience_comments": all_comments
                }

        return {
            "general_trends": trends_data,
            "channel_specific": channel_data
        }

    except Exception as e:
        logger.error(f"Error al obtener tendencias de YouTube: {e}")
        return None
