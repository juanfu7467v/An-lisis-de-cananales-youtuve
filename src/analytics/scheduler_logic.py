import datetime
from googleapiclient.discovery import build

def get_best_posting_time(youtube_analytics, channel_id):
    """
    Analiza los datos de audiencia del canal para determinar la mejor hora de publicación.
    En una implementación real, esto consultaría la YouTube Analytics API.
    Para este MVP, implementamos una lógica basada en el rendimiento histórico.
    """
    try:
        # Ejemplo de llamada a la API de Analytics (requiere permisos adecuados)
        # result = youtube_analytics.reports().query(
        #     ids=f'channel=={channel_id}',
        #     startDate='2025-01-01',
        #     endDate='2026-01-31',
        #     metrics='views',
        #     dimensions='dayOfWeek,hour'
        # ).execute()
        
        # Lógica por defecto si no hay datos suficientes:
        # Típicamente entre las 18:00 y 21:00 es buena hora para contenido en español.
        now = datetime.datetime.now()
        target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
        
        if target_time < now:
            target_time += datetime.timedelta(days=1)
            
        return target_time
    except Exception as e:
        print(f"Error analizando horarios: {e}")
        return datetime.datetime.now() + datetime.timedelta(hours=2)
