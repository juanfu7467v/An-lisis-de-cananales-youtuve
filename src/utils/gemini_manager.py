import os
import logging
from google import genai

logger = logging.getLogger(__name__)

class GeminiManager:
    """
    Gestiona la rotación de múltiples API Keys de Gemini para evitar límites de cuota.
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
        
        Args:
            func: Función que realiza la llamada a Gemini. Debe aceptar el cliente configurado.
            *args, **kwargs: Argumentos para la función.
            
        Returns:
            El resultado de la función o None si todas las claves fallan.
        """
        keys = cls.get_available_keys()
        if not keys:
            logger.error("No se encontró ninguna GEMINI_API_KEY configurada.")
            return None

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
                    logger.warning(f"Límite de cuota alcanzado para la clave {i+1}. Intentando con la siguiente...")
                    continue
                else:
                    # Si es otro tipo de error, lo reportamos y pasamos a la siguiente por seguridad
                    logger.error(f"Error inesperado con la clave {i+1}: {e}")
                    continue
        
        logger.error("Todas las claves de Gemini han fallado o agotado su cuota.")
        return None
