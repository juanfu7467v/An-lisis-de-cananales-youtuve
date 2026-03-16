import os
import logging
import requests
import threading
import time # Importar el módulo time para la función sleep
from src.analytics.youtube_trends import get_youtube_trends
from src.analytics.ai_analyzer import analyze_trends_and_recommend

logger = logging.getLogger(__name__)

def run_autonomous_job():
    """
    Inicia el proceso autónomo en un hilo separado.
    """
    job_thread = threading.Thread(target=_job_execution)
    job_thread.start()
    return {"status": "Job started in background"}, 202

def _job_execution():
    """
    Ejecución detallada del job en un hilo separado.
    Procesa canales secuencialmente con una espera de 2 horas entre ellos.
    """
    logger.info("Iniciando ejecución del job autónomo...")

    # Definir los canales a procesar
    channels = [
        {"id": os.getenv("ID_CANAL", "El Criterio ID"), "name": "El Criterio"},
        {"id": os.getenv("ID_CANAL_2", "El Tío Jota ID"), "name": "El Tío Jota"}
    ]

    target_url = os.getenv("TARGET_URL", "https://crear-videos-subir-youtuve.fly.dev/trigger-video")

    for i, channel in enumerate(channels):
        if i > 0:
            logger.info(f"Esperando 2 horas antes de analizar el siguiente canal: {channel['name']}...")
            time.sleep(7200) # Esperar 2 horas (7200 segundos)

        logger.info(f"Analizando canal: {channel['name']} (ID: {channel['id']})")
        
        # 1. Analizar tendencias de YouTube
        trends = get_youtube_trends(channel_id=channel['id']) # Pasar el ID del canal para un análisis más específico si es necesario
        if not trends:
            logger.error(f"No se pudieron obtener las tendencias de YouTube para {channel['name']}.")
            continue

        # 2. Generar recomendaciones usando Gemini 2.5 Flash
        recommendation = analyze_trends_and_recommend(trends, channel_name=channel['name'])
        if not recommendation:
            logger.error(f"No se pudo generar la recomendación para {channel['name']}.")
            continue

        # Asegurar que la recomendación incluya el nombre del canal para el sistema receptor
        recommendation["canal_objetivo"] = channel['name']

        # 3. Enviar el JSON al servidor externo (Endpoint Receptor)
        try:
            logger.info(f"Enviando recomendación para {channel['name']} a {target_url}...")
            response = requests.post(target_url, json=recommendation, timeout=60)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Recomendación para {channel['name']} enviada con éxito: {response.status_code}")
            else:
                logger.error(f"Error al enviar recomendación para {channel['name']}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error en la petición HTTP al servidor de destino para {channel['name']}: {e}")

    logger.info("Todos los jobs autónomos completados. Entrando en modo de espera hasta el siguiente ciclo.")
    # El servidor se apagará automáticamente después de este proceso si no hay más tráfico
    # gracias a la configuración auto_stop de Fly.io
