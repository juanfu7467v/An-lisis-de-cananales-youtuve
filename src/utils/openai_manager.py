import os
import logging
import json
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIManager:
    """
    Gestiona las llamadas a OpenAI como sistema de respaldo (fallback).
    """
    
    @classmethod
    def get_client(cls):
        """Retorna un cliente de OpenAI si la clave está configurada."""
        api_key = os.getenv("OPEN_AI_TOKEN")
        if not api_key:
            logger.error("No se encontró la variable de entorno OPEN_AI_TOKEN.")
            return None
        return OpenAI(api_key=api_key)

    @classmethod
    def analyze_with_fallback(cls, prompt, model="gpt-3.5-turbo"):
        """
        Realiza un análisis utilizando OpenAI GPT-3.5 Turbo.
        
        Args:
            prompt: El prompt a enviar a la IA.
            model: El modelo de OpenAI a utilizar (por defecto gpt-3.5-turbo).
            
        Returns:
            str: La respuesta de la IA o None si falla.
        """
        client = cls.get_client()
        if not client:
            return None

        try:
            logger.info(f"Iniciando fallback con OpenAI utilizando el modelo {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un experto estratega de contenido para YouTube."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al llamar a OpenAI: {e}")
            return None
