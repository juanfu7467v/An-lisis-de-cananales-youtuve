import os
import logging
import threading
from dotenv import load_dotenv
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler

from src.bot.handlers import start, handle_video
from src.analytics.daily_advisor import get_daily_recommendation, format_daily_message
from src.utils.config_manager import ConfigManager

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Servidor Flask para Railway
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Sistema Automático YouTube El Tío Jota Activo", 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

async def send_daily_advice(application):
    """Tarea programada para enviar el aviso diario."""
    if not ConfigManager.is_feature_enabled("daily_advice"):
        return

    logger.info("Generando aviso diario...")
    rec = get_daily_recommendation()
    message = format_daily_message(rec)
    
    # Obtener el ID del usuario principal de las variables de entorno
    user_ids = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "").split(",")
    for user_id in user_ids:
        if user_id:
            try:
                await application.bot.send_message(
                    chat_id=user_id.strip(),
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error enviando aviso diario a {user_id}: {e}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Falta TELEGRAM_BOT_TOKEN")
        return

    # Configurar Aplicación de Telegram
    application = ApplicationBuilder().token(token).build()
    
    # Manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Configurar Scheduler para Aviso Diario (Ejemplo: todos los días a las 08:00 AM)
    scheduler = BackgroundScheduler()
    # Usamos una función lambda para llamar a la corrutina en el loop de eventos correcto
    import asyncio
    scheduler.add_job(
        lambda: asyncio.run(send_daily_advice(application)),
        'cron',
        hour=8,
        minute=0
    )
    scheduler.start()
    
    # Hilo para Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info("Sistema Iniciado. Modo: %s", ConfigManager.get_mode())
    application.run_polling()

if __name__ == '__main__':
    main()
