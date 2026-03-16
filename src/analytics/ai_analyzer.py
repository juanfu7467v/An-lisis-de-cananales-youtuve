import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

def analyze_trends_and_recommend(trends_data, channel_name=None):
    """
    Utiliza Gemini 2.5 Flash para analizar tendencias y generar recomendaciones de video.
    Ahora considera el nombre del canal para adaptar las recomendaciones.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY para análisis de tendencias")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        channel_context = ""
        if channel_name:
            channel_context = f"El canal objetivo es '{channel_name}'. Adapta las recomendaciones para que sean altamente relevantes y atractivas para la audiencia específica de este canal, considerando su estilo y contenido habitual. El contenido debe ser interesante, dinámico y atractivo para el espectador, captando su atención desde el inicio y manteniéndola durante todo el video. Evita contenido aburrido y busca ideas que generen alta retención y crecimiento del canal.\n\n"

        prompt = f"""
        Analiza los siguientes datos de tendencias de YouTube:
        {json.dumps(trends_data, indent=2)}

        {channel_context}
        Basado en este análisis, genera una recomendación estratégica para un nuevo video.

        Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
        {{
          "tema_recomendado": "Ejemplo: Misterios del océano profundo descubiertos recientemente",
          "titulo": "Ejemplo: Los secretos del océano que los científicos acaban de descubrir",
          "idea_contenido": "Ejemplo: Un video que muestra descubrimientos recientes en el océano profundo, criaturas extrañas, lugares nunca explorados y datos sorprendentes. El contenido debe ser dinámico, con transiciones rápidas, música envolvente y narración cautivadora para mantener al espectador enganchado.",
          "formato_sugerido": "Short o video largo",
          "hora_optima_publicacion": "19:30",
          "tags_sugeridos": ["tag1", "tag2", "tag3"],
          "miniaturas_sugeridas": ["Descripción de miniatura 1", "Descripción de miniatura 2"],
          "gancho_inicial": "Pregunta intrigante o afirmación sorprendente para los primeros 15 segundos."
        }}
        """

        response = model.generate_content(prompt)
        
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        recommendation = json.loads(clean_text)
        
        return recommendation

    except Exception as e:
        logger.error(f"Error al analizar tendencias con Gemini: {e}")
        return None
