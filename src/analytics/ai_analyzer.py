import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

def analyze_trends_and_recommend(trends_data):
    """
    Utiliza Gemini 2.5 Flash para analizar tendencias y generar recomendaciones de video.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY para análisis de tendencias")
        return None

    try:
        # Configurar Gemini 2.5 Flash
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Analiza los siguientes datos de tendencias de YouTube:
        {json.dumps(trends_data, indent=2)}

        Basado en este análisis, genera una recomendación estratégica para un nuevo video.
        Considera que tenemos dos canales disponibles (ID_CANAL e ID_CANAL_2).
        Debes decidir cuál es el canal más apropiado según el tema.

        Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
        {{
          "tema_recomendado": "Ejemplo: Misterios del océano profundo descubiertos recientemente",
          "titulo": "Ejemplo: Los secretos del océano que los científicos acaban de descubrir",
          "idea_contenido": "Ejemplo: Un video que muestra descubrimientos recientes en el océano profundo, criaturas extrañas, lugares nunca explorados y datos sorprendentes.",
          "formato_sugerido": "Short o video largo",
          "hora_optima_publicacion": "19:30",
          "canal": "ID_CANAL o ID_CANAL_2"
        }}
        """

        response = model.generate_content(prompt)
        
        # Limpiar respuesta por si acaso Gemini incluye markdown
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        recommendation = json.loads(clean_text)
        
        # Asegurar que el campo 'canal' tenga un valor coherente
        # El sistema receptor espera CHANNEL_NAME o CHANNEL_NAME_2 según el ejemplo
        if "canal" not in recommendation:
            recommendation["canal"] = "CHANNEL_NAME"
            
        return recommendation

    except Exception as e:
        logger.error(f"Error al analizar tendencias con Gemini: {e}")
        return None
