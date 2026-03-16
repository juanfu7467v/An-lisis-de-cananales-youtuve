import os
import logging
import requests
import threading
from src.analytics.youtube_trends import get_youtube_trends
from src.analytics.ai_analyzer import analyze_trends_and_recommend

logger = logging.getLogger(__name__)

def run_autonomous_job():
    """
    Inicia el proceso autónomo en un hilo separado.
    1. Analiza tendencias.
    2. Genera recomendaciones.
    3. Envía el JSON al servidor de destino.
    """
    job_thread = threading.Thread(target=_job_execution)
    job_thread.start()
    return {"status": "Job started in background"}, 202

def _job_execution():
    """
    Ejecución detallada del job en un hilo separado.
    """
    logger.info("Iniciando ejecución del job autónomo...")
    
    # 1. Analizar tendencias de YouTube
    trends = get_youtube_trends()
    if not trends:
        logger.error("No se pudieron obtener las tendencias de YouTube.")
        return

    # 2. Generar recomendaciones usando Gemini 2.5 Flash
    recommendation = analyze_trends_and_recommend(trends)
    if not recommendation:
        logger.error("No se pudo generar la recomendación.")
        return

    # 3. Enviar el JSON al servidor externo (Endpoint Receptor)
    target_url = "https://crear-videos-subir-youtuve.fly.dev/trigger-video"
    try:
        logger.info(f"Enviando reporte matutino a {target_url}...")
        response = requests.post(target_url, json=recommendation, timeout=60)
        if response.status_code in [200, 201, 202]:
            logger.info(f"Reporte matutino enviado con éxito: {response.status_code}")
        else:
            logger.error(f"Error al enviar reporte matutino: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error en la petición HTTP al servidor de destino: {e}")

    logger.info("Job autónomo completado con éxito.")
    # El servidor se apagará automáticamente después de este proceso si no hay más tráfico
    # gracias a la configuración auto_stop de Fly.io
