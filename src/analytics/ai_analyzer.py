import os
import json
import logging
import google.generativeai as genai
from src.analytics.channel_config import get_channel_config

logger = logging.getLogger(__name__)

def analyze_trends_and_recommend(trends_data, channel_name=None):
    """
    Utiliza Gemini 2.5 Flash para realizar un análisis profundo y generar recomendaciones de video.
    Incluye análisis de comentarios, engagement e interacción con la audiencia.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY para análisis de tendencias")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        config = get_channel_config(channel_name)
        channel_context = ""
        if config:
            channel_context = f"""
            Contexto del Canal '{channel_name}':
            - Temas principales: {", ".join(config['topics'])}
            - Descripción: {config['description']}
            - Web de referencia: {config['website_promo']}
            """

        prompt = f"""
        Eres un experto estratega de contenido para YouTube. Analiza los siguientes datos:

        {channel_context}

        DATOS DE TENDENCIAS GENERALES:
        {json.dumps(trends_data.get('general_trends', []), indent=2)}

        DATOS ESPECÍFICOS DEL CANAL (Rendimiento y Comentarios):
        {json.dumps(trends_data.get('channel_specific', {}), indent=2)}

        TAREAS:
        1. ANALISIS PROFUNDO: Identifica qué temas del canal están funcionando mejor (vistas/likes).
        2. ESCUCHA ACTIVA: Revisa los comentarios para detectar peticiones específicas de la audiencia o temas recurrentes.
        3. ESTRATEGIA: Genera una recomendación de video que combine las tendencias actuales con la esencia del canal.
        4. INTERACCIÓN: Genera respuestas sugeridas para los comentarios más relevantes, saludando y recomendando contenido relacionado o la web {config.get('website_promo') if config else 'la web oficial'}.

        Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
        {{
          "tema_recomendado": "Ejemplo: Análisis filosófico de la película X",
          "titulo": "Ejemplo: El secreto oculto en X que nadie notó",
          "idea_contenido": "Descripción detallada del video, tono y estructura para maximizar retención.",
          "formato_sugerido": "Short o video largo",
          "hora_optima_publicacion": "HH:MM",
          "canal": "{channel_name}",
          "categoria": "Categoría específica basada en el contenido (ej: películas, filosofía, etc.)",
          "analisis_audiencia": {{
            "temas_solicitados": ["tema1", "tema2"],
            "sentimiento_general": "positivo/neutro/negativo",
            "observaciones_engagement": "Breve nota sobre qué videos funcionaron mejor"
          }},
          "interaccion_sugerida": [
            {{
              "comentario_original": "Texto del comentario al que se responde",
              "respuesta_sugerida": "Respuesta amable, saludando al usuario y dirigiendo hacia contenido relacionado o la web de películas."
            }}
          ]
        }}
        """

        response = model.generate_content(prompt)
        
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        recommendation = json.loads(clean_text)
        
        # Asegurar campos requeridos por el usuario
        recommendation["canal"] = channel_name
        
        return recommendation

    except Exception as e:
        logger.error(f"Error al analizar tendencias con Gemini: {e}")
        return None
