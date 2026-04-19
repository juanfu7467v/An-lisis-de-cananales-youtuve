import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

# Configuración de rotación de contenido
# Ahora alternamos entre Short y Video largo
CONTENT_ROTATION = {
    "Short": {
        "formato": "Short",
        "duracion": "30-60 segundos",
        "categoria_temas": "variado_shorts",
        "estilo": "viral, impactante, directo",
        "estructura": "gancho + punto clave + llamada a la acción"
    },
    "Video largo": {
        "formato": "Video largo",
        "duracion": "12-20 minutos",
        "categoria_temas": "peliculas_analisis",
        "estilo": "profundo, reflexivo, emocionante",
        "estructura": "introducción + análisis profundo + conclusiones + reflexión final"
    }
}

# Temas para cada categoría (como fallback o guía para la IA)
TEMA_POOLS = {
    "peliculas_analisis": [
        "Análisis profundo de películas",
        "Análisis de personajes y sus motivaciones",
        "Mensajes ocultos en el cine",
        "Análisis de guion y dirección",
        "Lecciones de vida a través del cine"
    ],
    "variado_shorts": [
        "Curiosidades de películas",
        "Filosofía aplicada (Estoicismo)",
        "Grandes pensadores (Sócrates, Diógenes, Maquiavelo)",
        "Historia fascinante (Imperio Inca, etc.)",
        "Lecciones rápidas de vida"
    ]
}

# Hooks predefinidos por tipo de contenido
HOOKS_TEMPLATES = {
    "Short": [
        "Espera al final, te sorprenderá...",
        "Esto es lo que nadie te dice sobre...",
        "Mira esto, es increíble...",
        "No puedes creer lo que pasó con...",
        "¿Sabías esto sobre...?"
    ],
    "Video largo": [
        "Descubre los secretos ocultos que nadie notó...",
        "Te revelaré la verdad detrás de...",
        "Prepárate, esto cambiará tu perspectiva sobre...",
        "Este análisis te hará repensar todo lo que sabías sobre...",
        "La historia detrás de esta película te dejará sin palabras..."
    ]
}

def get_last_format_for_channel(channel_name, filename="data.json"):
    """
    Busca en el historial el último formato publicado para un canal específico.
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # Filtrar por canal y ordenar por fecha/hora (el historial suele estar en orden cronológico)
                channel_history = [entry for entry in history if entry.get('canal') == channel_name]
                if channel_history:
                    last_entry = channel_history[-1]
                    return last_entry.get('analisis', {}).get('formato_sugerido')
    except Exception as e:
        logger.error(f"Error al leer historial para formato: {e}")
    return None

def get_content_type_for_day(channel_name=None):
    """
    Determina el tipo de contenido basándose en la configuración o alternancia Short/Largo.
    """
    # Nueva lógica: Si VIDEO_LARGO está en true, siempre recomienda Video largo.
    # Si no está configurado o es false, por defecto recomienda Shorts.
    video_largo_env = os.getenv("VIDEO_LARGO", "false").lower() == "true"
    
    if video_largo_env:
        return CONTENT_ROTATION["Video largo"]
    
    # Si no está configurado VIDEO_LARGO=true, por defecto recomienda Shorts.
    # Mantenemos la lógica de alternancia comentada por si se desea recuperar en el futuro,
    # pero cumplimos con el requerimiento de "por defecto debe recomendar videos Shorts".
    return CONTENT_ROTATION["Short"]

def get_theme_for_content_type(content_config):
    """
    Selecciona un tema apropiado para el tipo de contenido especificado.
    """
    categoria = content_config.get("categoria_temas")
    return f"Tema variado de {categoria}"

def get_hook_for_format(formato):
    """
    Selecciona un hook impactante para el formato especificado.
    """
    hooks = HOOKS_TEMPLATES.get(formato, HOOKS_TEMPLATES["Short"])
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    hook_index = day_of_year % len(hooks)
    return hooks[hook_index]

def generate_super_prompt(content_config, tema, titulo, idea_contenido, canal):
    """
    Genera un "Super Prompt" optimizado para la IA basándose en la configuración del contenido.
    """
    formato = content_config.get("formato")
    estilo = content_config.get("estilo")
    estructura = content_config.get("estructura")
    duracion = content_config.get("duracion")
    
    super_prompt = f"""
Actúa como un experto creador de contenido para YouTube especializado en {canal}.

OBJETIVO PRINCIPAL:
Crea un guion que capture la atención desde los primeros segundos y mantenga al espectador enganchado hasta el final. El contenido debe ser {estilo}.

TEMA: {tema}
TÍTULO: {titulo}
FORMATO: {formato}
DURACIÓN: {duracion}

IDEA DEL CONTENIDO:
{idea_contenido}

INSTRUCCIONES ESPECÍFICAS:
1. ESTILO: Mantén un tono {estilo} en todo momento.
2. ESTRUCTURA: Sigue este orden: {estructura}
3. GANCHO INICIAL: Comienza con una frase impactante que genere curiosidad inmediata (primeros 5 segundos).
4. CONTENIDO: Utiliza datos interesantes, ejemplos concretos y lenguaje claro que resuene con la audiencia.
5. RETENCIÓN: Cada sección debe fluir naturalmente hacia la siguiente, evitando caídas en el engagement.
6. CONCLUSIÓN: Termina con una reflexión memorable o una llamada a la acción que invite a la interacción.

RESULTADO ESPERADO:
Un guion completo, listo para ser grabado, que sea profesional, entretenido y que maximice la retención de la audiencia.
"""
    return super_prompt.strip()

def build_enhanced_recommendation(base_recommendation, content_config):
    """
    Enriquece la recomendación base con los nuevos campos del Super Prompt.
    """
    enhanced = base_recommendation.copy()
    
    enhanced["estilo_contenido"] = content_config.get("estilo")
    enhanced["estructura"] = content_config.get("estructura")
    enhanced["hook"] = get_hook_for_format(content_config.get("formato"))
    
    enhanced["prompt_ia"] = generate_super_prompt(
        content_config,
        enhanced.get("tema_recomendado", ""),
        enhanced.get("titulo", ""),
        enhanced.get("idea_contenido", ""),
        enhanced.get("canal", "")
    )
    
    enhanced["formato_sugerido"] = content_config.get("formato")
    
    return enhanced
