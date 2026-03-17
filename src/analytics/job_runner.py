import os
import logging
import requests
import threading
import time
from datetime import datetime
from src.analytics.youtube_trends import get_youtube_trends
from src.analytics.ai_analyzer import analyze_trends_and_recommend
from src.analytics.channel_config import get_all_channels_ordered
from src.utils.github_storage import save_to_github_json, check_if_analyzed_today

logger = logging.getLogger(__name__)

def run_autonomous_job():
    """
    Inicia el proceso autónomo en un hilo separado.
    """
    job_thread = threading.Thread(target=_job_execution)
    job_thread.start()
    return {"status": "Job de análisis profundo iniciado en background"}, 202

def _job_execution():
    """
    Ejecución detallada del job en un hilo separado.
    Procesa canales secuencialmente con una espera de 2 horas entre ellos.
    Persiste los resultados en data.json en GitHub.
    """
    logger.info("Iniciando ejecución del job autónomo con análisis profundo...")

    # Obtener los canales configurados en orden
    channels_data = get_all_channels_ordered()
    target_url = os.getenv("TARGET_URL", "https://crear-videos-subir-youtuve.fly.dev/trigger-video")

    for i, (channel_name, config) in enumerate(channels_data):
        channel_id = config.get("id")
        
        # Verificar si ya fue analizado hoy en data.json (especificación del usuario)
        if check_if_analyzed_today(channel_name):
            logger.info(f"El canal {channel_name} ya ha sido analizado hoy. Saltando...")
            continue

        if i > 0:
            logger.info(f"Esperando 2 horas antes de analizar el siguiente canal: {channel_name}...")
            time.sleep(7200) # Esperar 2 horas (7200 segundos)

        logger.info(f"Analizando canal: {channel_name} (ID: {channel_id})")
        
        # 1. Analizar tendencias de YouTube (Generales + Específicas del canal)
        trends = get_youtube_trends(channel_id=channel_id)
        if not trends:
            logger.error(f"No se pudieron obtener las tendencias de YouTube para {channel_name}.")
            continue

        # 2. Generar recomendaciones profundas usando Gemini 2.5 Flash
        recommendation = analyze_trends_and_recommend(trends, channel_name=channel_name)
        if not recommendation:
            logger.error(f"No se pudo generar la recomendación profunda para {channel_name}.")
            continue

        # Asegurar campos requeridos
        recommendation["canal_objetivo"] = channel_name
        recommendation["fecha_analisis"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Guardar el resultado en data.json en GitHub (Persistencia)
        save_success = save_to_github_json(recommendation)
        if save_success:
            logger.info(f"Resultado del análisis para {channel_name} guardado exitosamente en GitHub.")
        else:
            logger.warning(f"No se pudo guardar el resultado para {channel_name} en GitHub.")

        # 4. Enviar el JSON al servidor externo (Endpoint Receptor)
        try:
            logger.info(f"Enviando recomendación para {channel_name} a {target_url}...")
            response = requests.post(target_url, json=recommendation, timeout=60)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Recomendación para {channel_name} enviada con éxito: {response.status_code}")
            else:
                logger.error(f"Error al enviar recomendación para {channel_name}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error en la petición HTTP al servidor de destino para {channel_name}: {e}")

    logger.info("Todos los jobs autónomos completados. Entrando en modo de espera hasta el siguiente ciclo.")
