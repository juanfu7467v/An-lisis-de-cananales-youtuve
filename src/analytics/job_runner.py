import os
import logging
import requests
import threading
from datetime import datetime
from src.analytics.youtube_trends import get_youtube_trends
from src.analytics.ai_analyzer import analyze_trends_and_recommend
from src.analytics.channel_config import get_channel_config
from src.analytics.state_manager import get_next_channel_to_analyze, has_channel_been_analyzed_today
from src.utils.github_storage import save_to_github_json

logger = logging.getLogger(__name__)

def run_autonomous_job():
    """
    Inicia el proceso autónomo en un hilo separado.
    
    La activación ocurre únicamente por peticiones externas al endpoint.
    No hay temporizadores internos.
    """
    job_thread = threading.Thread(target=_job_execution)
    job_thread.start()
    return {"status": "Job de análisis profundo iniciado en background"}, 202

def _job_execution():
    """
    Ejecución del job autónomo.
    
    Lógica:
    1. Determina qué canal analizar basándose en el historial (data.json)
    2. Si el canal ya fue analizado hoy, intenta con el siguiente
    3. Analiza el canal seleccionado
    4. Guarda el resultado en data.json
    5. Envía el reporte al servidor externo
    6. Se duerme esperando la siguiente petición externa
    
    No hay temporizadores internos. Todo se activa por peticiones externas.
    """
    logger.info("=" * 80)
    logger.info("Iniciando ejecución del job autónomo (activado por petición externa)")
    logger.info("=" * 80)

    target_url = os.getenv("TARGET_URL", "https://crear-videos-subir-youtuve.fly.dev/trigger-video")

    # Determinar qué canal analizar
    channel_name = get_next_channel_to_analyze()
    
    # Verificar si ya fue analizado hoy
    if has_channel_been_analyzed_today(channel_name):
        logger.warning(f"El canal '{channel_name}' ya fue analizado hoy.")
        logger.info("Esperando la siguiente petición externa (en 12 horas)...")
        logger.info("=" * 80)
        return
    
    # Obtener configuración del canal
    channel_config = get_channel_config(channel_name)
    if not channel_config:
        logger.error(f"No se encontró configuración para el canal: {channel_name}")
        logger.info("=" * 80)
        return
    
    channel_id = channel_config.get("id")
    logger.info(f"Analizando canal: {channel_name} (ID: {channel_id})")

    try:
        # 1. Analizar tendencias de YouTube
        logger.info(f"Obteniendo tendencias de YouTube para {channel_name}...")
        trends = get_youtube_trends(channel_id=channel_id)
        if not trends:
            logger.error(f"No se pudieron obtener las tendencias de YouTube para {channel_name}.")
            logger.info("=" * 80)
            return

        # 2. Generar recomendaciones profundas usando Gemini 2.5 Flash
        logger.info(f"Generando recomendaciones profundas para {channel_name}...")
        recommendation = analyze_trends_and_recommend(trends, channel_name=channel_name)
        if not recommendation:
            logger.error(f"No se pudo generar la recomendación profunda para {channel_name}.")
            logger.info("=" * 80)
            return

        # Asegurar campos requeridos
        recommendation["canal_objetivo"] = channel_name
        recommendation["fecha_analisis"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Guardar el resultado en data.json
        logger.info(f"Guardando resultado del análisis para {channel_name}...")
        save_success = save_to_github_json(recommendation)
        if save_success:
            logger.info(f"✓ Resultado del análisis para {channel_name} guardado exitosamente en GitHub.")
        else:
            logger.warning(f"⚠ No se pudo guardar el resultado para {channel_name} en GitHub.")

        # 4. Enviar el JSON al servidor externo
        try:
            logger.info(f"Enviando recomendación para {channel_name} a {target_url}...")
            response = requests.post(target_url, json=recommendation, timeout=60)
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Recomendación para {channel_name} enviada con éxito: {response.status_code}")
            else:
                logger.error(f"✗ Error al enviar recomendación para {channel_name}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"✗ Error en la petición HTTP al servidor de destino para {channel_name}: {e}")

        logger.info(f"✓ Análisis de {channel_name} completado exitosamente.")
        logger.info("Esperando la siguiente petición externa (en 12 horas)...")

    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución del job: {e}")
    
    finally:
        logger.info("=" * 80)
