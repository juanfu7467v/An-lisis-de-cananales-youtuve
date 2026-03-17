import datetime
import logging

logger = logging.getLogger(__name__)

# Configuración de rotación de contenido
CONTENT_ROTATION = {
    0: {  # Día 1 del ciclo
        "formato": "Short",
        "duracion": "30-60 segundos",
        "categoria_temas": "trending",
        "estilo": "viral, impactante, directo",
        "estructura": "gancho + punto clave + llamada a la acción"
    },
    1: {  # Día 2 del ciclo
        "formato": "Video largo",
        "duracion": "12-20 minutos",
        "categoria_temas": "análisis_película",
        "estilo": "profundo, reflexivo, emocionante",
        "estructura": "introducción + análisis profundo + conclusiones + reflexión final"
    },
    2: {  # Día 3 del ciclo
        "formato": "Video educativo",
        "duracion": "8-15 minutos",
        "categoria_temas": "filosofía_educativo",
        "estilo": "educativo, inspirador, motivador",
        "estructura": "contexto histórico + enseñanza + aplicación práctica + conclusión"
    }
}

# Temas para cada categoría
TEMA_POOLS = {
    "trending": [
        "Tendencia viral de hoy",
        "Reacción a noticia trending",
        "Análisis rápido de tema del momento"
    ],
    "análisis_película": [
        "Análisis filosófico de película reciente",
        "Lecciones de vida en películas clásicas",
        "Mensajes ocultos en películas populares",
        "Análisis profundo de saga cinematográfica"
    ],
    "filosofía_educativo": [
        "Lecciones de Sócrates para la vida moderna",
        "Nicolás Maquiavelo y el poder en la actualidad",
        "Friedrich Nietzsche y la superación personal",
        "Marco Aurelio y el estoicismo en el siglo XXI",
        "Aristóteles y la virtud en nuestros días",
        "Immanuel Kant y la ética contemporánea",
        "Jean-Paul Sartre y la libertad individual"
    ]
}

# Hooks predefinidos por tipo de contenido
HOOKS_TEMPLATES = {
    "Short": [
        "Espera al final, te sorprenderá...",
        "Esto es lo que nadie te dice sobre...",
        "Mira esto, es increíble...",
        "No puedes creer lo que pasó con..."
    ],
    "Video largo": [
        "Descubre los secretos ocultos que nadie notó...",
        "Te revelaré la verdad detrás de...",
        "Prepárate, esto cambiará tu perspectiva sobre...",
        "Este análisis te hará repensar todo lo que sabías sobre..."
    ],
    "Video educativo": [
        "Aprende la lección que los filósofos querían que entendieras...",
        "Este principio antiguo sigue siendo relevante hoy porque...",
        "Descubre cómo aplicar esta enseñanza a tu vida...",
        "La sabiduría que necesitas para triunfar está aquí..."
    ]
}

def get_content_type_for_day(day_offset=0):
    """
    Determina el tipo de contenido para un día específico basándose en la rotación.
    
    Args:
        day_offset: Número de días desde hoy (0 = hoy, 1 = mañana, etc.)
    
    Returns:
        Diccionario con la configuración del tipo de contenido
    """
    target_date = datetime.datetime.now() + datetime.timedelta(days=day_offset)
    # Usar el día del año para crear un ciclo consistente
    day_of_year = target_date.timetuple().tm_yday
    cycle_position = (day_of_year - 1) % 3  # 0, 1 o 2
    
    return CONTENT_ROTATION[cycle_position]

def get_theme_for_content_type(content_type):
    """
    Selecciona un tema apropiado para el tipo de contenido especificado.
    
    Args:
        content_type: Diccionario con configuración del tipo de contenido
    
    Returns:
        Tema recomendado (string)
    """
    categoria = content_type.get("categoria_temas")
    temas = TEMA_POOLS.get(categoria, [])
    
    if not temas:
        return "Contenido de calidad"
    
    # Usar el día del año para seleccionar un tema de manera consistente
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    tema_index = day_of_year % len(temas)
    
    return temas[tema_index]

def get_hook_for_format(formato):
    """
    Selecciona un hook impactante para el formato especificado.
    
    Args:
        formato: Formato del video (Short, Video largo, Video educativo)
    
    Returns:
        Hook sugerido (string)
    """
    hooks = HOOKS_TEMPLATES.get(formato, HOOKS_TEMPLATES["Short"])
    
    # Usar el día del año para seleccionar un hook de manera consistente
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    hook_index = day_of_year % len(hooks)
    
    return hooks[hook_index]

def generate_super_prompt(content_config, tema, titulo, idea_contenido, canal):
    """
    Genera un "Super Prompt" optimizado para la IA basándose en la configuración del contenido.
    
    Args:
        content_config: Diccionario con configuración del tipo de contenido
        tema: Tema del video
        titulo: Título del video
        idea_contenido: Descripción de la idea del contenido
        canal: Nombre del canal
    
    Returns:
        String con el Super Prompt completo
    """
    formato = content_config.get("formato")
    estilo = content_config.get("estilo")
    estructura = content_config.get("estructura")
    
    super_prompt = f"""
Actúa como un experto creador de contenido para YouTube especializado en {canal}.

OBJETIVO PRINCIPAL:
Crea un guion que capture la atención desde los primeros segundos y mantenga al espectador enganchado hasta el final. El contenido debe ser {estilo}.

TEMA: {tema}
TÍTULO: {titulo}
FORMATO: {formato}
DURACIÓN: {content_config.get('duracion')}

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
    
    Args:
        base_recommendation: Diccionario con la recomendación base de Gemini
        content_config: Diccionario con configuración del tipo de contenido
    
    Returns:
        Diccionario enriquecido con los nuevos campos
    """
    enhanced = base_recommendation.copy()
    
    # Agregar campos de Super Prompt
    enhanced["estilo_contenido"] = content_config.get("estilo")
    enhanced["estructura"] = content_config.get("estructura")
    enhanced["hook"] = get_hook_for_format(content_config.get("formato"))
    
    # Generar el Super Prompt
    enhanced["prompt_ia"] = generate_super_prompt(
        content_config,
        enhanced.get("tema_recomendado", ""),
        enhanced.get("titulo", ""),
        enhanced.get("idea_contenido", ""),
        enhanced.get("canal", "")
    )
    
    # Asegurar que el formato sugerido esté actualizado
    enhanced["formato_sugerido"] = content_config.get("formato")
    
    return enhanced
