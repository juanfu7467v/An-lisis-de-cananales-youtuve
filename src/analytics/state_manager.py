import os
import json
import logging
import requests
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

# Orden de canales para alternancia
CHANNELS_ROTATION = ["El Tío Jota", "El Criterio"]

def get_next_channel_to_analyze(filename="data.json"):
    """
    Determina qué canal debe analizarse en la próxima petición.
    
    Lógica:
    - Si data.json está vacío, comienza con "El Tío Jota"
    - Si el último análisis fue de "El Tío Jota", analiza "El Criterio"
    - Si el último análisis fue de "El Criterio", analiza "El Tío Jota"
    
    Returns:
        str: Nombre del canal a analizar ("El Tío Jota" o "El Criterio")
    """
    try:
        # Intentar obtener el historial desde GitHub
        history = _get_analysis_history(filename)
        
        if not history:
            logger.info("Historial vacío. Iniciando con 'El Tío Jota'.")
            return "El Tío Jota"
        
        # Obtener el último análisis
        last_entry = history[-1]
        last_channel = last_entry.get("canal")
        
        logger.info(f"Último canal analizado: {last_channel}")
        
        # Determinar el siguiente canal
        if last_channel == "El Tío Jota":
            next_channel = "El Criterio"
        elif last_channel == "El Criterio":
            next_channel = "El Tío Jota"
        else:
            # Si hay un canal desconocido, reiniciar con "El Tío Jota"
            next_channel = "El Tío Jota"
        
        logger.info(f"Próximo canal a analizar: {next_channel}")
        return next_channel
        
    except Exception as e:
        logger.error(f"Error al determinar el próximo canal: {e}")
        # Por defecto, analizar "El Tío Jota"
        return "El Tío Jota"


def _get_analysis_history(filename="data.json"):
    """
    Obtiene el historial de análisis desde GitHub o localmente.
    
    Returns:
        list: Lista de análisis realizados
    """
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    
    # Intentar obtener desde GitHub
    if repo and token:
        try:
            url = f"https://api.github.com/repos/{repo}/contents/{filename}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_data = response.json()
                content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
                history = json.loads(content_decoded)
                
                if isinstance(history, list):
                    return history
                else:
                    return [history]
        except Exception as e:
            logger.warning(f"No se pudo obtener historial desde GitHub: {e}")
    
    # Fallback: intentar obtener localmente
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history
                else:
                    return [history]
    except Exception as e:
        logger.warning(f"No se pudo obtener historial localmente: {e}")
    
    return []


def has_channel_been_analyzed_today(channel_name, filename="data.json"):
    """
    Verifica si un canal ya ha sido analizado hoy.
    
    Args:
        channel_name (str): Nombre del canal
        filename (str): Nombre del archivo de datos
    
    Returns:
        bool: True si ya fue analizado hoy, False en caso contrario
    """
    try:
        history = _get_analysis_history(filename)
        today = datetime.now().strftime("%Y-%m-%d")
        
        for entry in history:
            if entry.get("canal") == channel_name and entry.get("fecha") == today:
                logger.info(f"Canal '{channel_name}' ya fue analizado hoy.")
                return True
        
        logger.info(f"Canal '{channel_name}' no ha sido analizado hoy.")
        return False
        
    except Exception as e:
        logger.error(f"Error al verificar si el canal fue analizado hoy: {e}")
        return False
