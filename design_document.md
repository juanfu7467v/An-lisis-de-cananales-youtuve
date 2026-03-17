# Diseño de Mejoras para el Sistema de Publicación de YouTube

## 1. Nueva Estructura JSON para "Super Prompts"

La estructura JSON actual será enriquecida para incluir campos que permitan generar prompts más detallados y efectivos para la IA, siguiendo las recomendaciones del usuario. La nueva estructura propuesta es la siguiente:

```json
{
  "tema_recomendado": "Análisis de películas",
  "titulo": "El Señor de los Anillos",
  "idea_contenido": "Crea un análisis profundo, emocionante y entretenido de la película.",
  "formato_sugerido": "video largo",
  "hora_optima_publicacion": "19:30",
  "canal": "CHANNEL_NAME",
  "categoria": "películas",
  "estilo_contenido": "emocional, intrigante, motivador",
  "hook": "frase impactante al inicio (primeros 5 segundos)",
  "estructura": "inicio + desarrollo + giro + conclusión + llamada a la acción",
  "prompt_ia": "Actúa como un experto creador de contenido para YouTube. Crea un guion atractivo, emocionante y que genere curiosidad desde el inicio. Usa lenguaje claro, incluye datos interesantes y mantén la atención del espectador hasta el final."
}
```

**Justificación de los nuevos campos:**

*   `estilo_contenido`: Permite especificar el tono y la emoción deseada para el contenido, guiando a la IA a generar un guion que resuene con la audiencia de manera específica (ej., emocional, intrigante, motivador, polémico).
*   `hook`: Proporciona una instrucción explícita para la creación de una frase impactante al inicio del video, crucial para captar la atención en los primeros segundos.
*   `estructura`: Define el esqueleto narrativo del contenido, asegurando que la IA siga un flujo lógico y probado para maximizar la retención del espectador (inicio, desarrollo, giro, conclusión, llamada a la acción).
*   `prompt_ia`: Este campo encapsulará el "Super Prompt" final, generado dinámicamente, que se enviará a la IA. Incluirá el rol, el objetivo, el estilo y las instrucciones específicas, tal como se ejemplificó en la solicitud.

## 2. Lógica de Rotación de Contenido

Se implementará una estrategia de rotación de contenido en `src/analytics/daily_advisor.py` para alternar automáticamente entre diferentes tipos de videos. La rotación propuesta es un ciclo de tres días:

*   **Día 1:** Short
*   **Día 2:** Video largo (Análisis de película)
*   **Día 3:** Video educativo (Ej: Sócrates, Nicolás Maquiavelo, Friedrich Nietzsche)

Este ciclo se repetirá continuamente. La selección del tipo de contenido se basará en el día de la semana o un contador interno para asegurar la alternancia.

### Modificaciones en `daily_advisor.py`:

1.  **Función `get_daily_recommendation()`:**
    *   Se modificará para determinar el `formato_sugerido` (Short, Video largo, Video educativo) basándose en la lógica de rotación.
    *   El `tema_recomendado` se seleccionará en función del `formato_sugerido`. Por ejemplo, si es un "Video educativo", se elegirá un tema de una lista predefinida de filósofos o temas educativos.
    *   Se generarán los campos `estilo_contenido`, `hook` y `estructura` de manera dinámica o se seleccionarán de plantillas predefinidas según el tipo de contenido.

## 3. Modificaciones en `ai_analyzer.py` para el "Super Prompt"

El archivo `src/analytics/ai_analyzer.py` es donde se construye el prompt para Gemini. Se realizarán las siguientes modificaciones:

1.  **Construcción del `prompt_ia`:**
    *   El prompt actual será reemplazado por una construcción dinámica que integre los nuevos campos (`estilo_contenido`, `hook`, `estructura`) y el `idea_contenido` para formar un "Super Prompt" completo.
    *   Se definirá un rol claro para la IA (ej., "experto creador de contenido para YouTube") y un objetivo (ej., "retener al espectador hasta el final").
    *   Se utilizarán los valores de los nuevos campos para inyectar instrucciones específicas sobre el estilo, el gancho inicial y la estructura del guion.

## 4. Consideraciones para `data.json` y `github_storage.py`

*   El archivo `data.json` almacenará las recomendaciones generadas, incluyendo los nuevos campos. La función `save_to_github_json` en `src/utils/github_storage.py` ya maneja la adición de nuevos campos a la estructura JSON existente, por lo que no se esperan cambios significativos en esta función, más allá de asegurar que los nuevos campos se incluyan en el diccionario `data_to_save` antes de ser pasados a esta función.
