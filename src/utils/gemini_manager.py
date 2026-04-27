import os
import logging
from google import genai
from src.utils.openai_manager import OpenAIManager

logger = logging.getLogger(__name__)

class GeminiManager:
    """
    Gestiona la rotación de múltiples API Keys de Gemini y el fallback a OpenAI.
    """
    _keys = [
        "GEMINI_API_KEY",
        "GEMINI_API_KEY_B",
        "GEMINI_API_KEY_C",
        "GEMINI_API_KEY_D",
        "GEMINI_API_KEY_E"
    ]
    
    @classmethod
    def get_available_keys(cls):
        """Retorna una lista de las claves API que están configuradas en el entorno."""
        available_keys = []
        for key_name in cls._keys:
            val = os.getenv(key_name)
            if val:
                available_keys.append(val)
        return available_keys

    @classmethod
    def call_with_rotation(cls, func, *args, **kwargs):
        """
        Ejecuta una función que usa la API de Gemini, rotando las claves si falla por cuota.
        Si todas las claves de Gemini fallan, intenta usar OpenAI como fallback.
        
        Args:
            func: Función que realiza la llamada a Gemini. Debe aceptar el cliente configurado.
            *args, **kwargs: Argumentos para la función.
            
        Returns:
            El resultado de la función o el resultado del fallback a OpenAI.
        """
        keys = cls.get_available_keys()
        
        # Intentar con Gemini primero (si hay claves)
        if keys:
            for i, api_key in enumerate(keys):
                try:
                    # Crear el cliente con la clave actual
                    client = genai.Client(api_key=api_key)
                    
                    # Intentar ejecutar la función pasando el cliente
                    return func(client, *args, **kwargs)
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    # Verificar si es un error de cuota (429 Too Many Requests)
                    if "429" in error_msg or "quota" in error_msg or "limit" in error_msg:
                        logger.warning(f"Límite de cuota alcanzado para la clave Gemini {i+1}. Intentando con la siguiente...")
                        continue
                    else:
                        # Si es otro tipo de error, lo reportamos y pasamos a la siguiente por seguridad
                        logger.error(f"Error inesperado con la clave Gemini {i+1}: {e}")
                        continue
        else:
            logger.warning("No se encontraron claves de Gemini configuradas.")

        # Si llegamos aquí, Gemini falló o no tiene claves. Intentar fallback a OpenAI.
        logger.info("Intentando fallback automático a OpenAI (GPT-3.5 Turbo)...")
        
        # Necesitamos el prompt original. Por convención en este proyecto, 
        # las funciones pasadas a call_with_rotation suelen construir el prompt internamente.
        # Para el fallback, llamaremos a una función especial si existe en kwargs o intentaremos deducirla.
        
        if 'fallback_func' in kwargs:
            fallback_func = kwargs.pop('fallback_func')
            return fallback_func(*args, **kwargs)
        
        logger.error("Todas las opciones de IA han fallado.")
        return None
