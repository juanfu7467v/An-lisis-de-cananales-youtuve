import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.bot.handlers import start, handle_video
from flask import Flask
import threading

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Servidor Flask para mantener vivo el proceso en Railway
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Sistema de Publicación YouTube Activo", 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def main():
    # Obtener token de Telegram
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("No se encontró TELEGRAM_BOT_TOKEN")
        return

    # Configurar Bot de Telegram
    application = ApplicationBuilder().token(token).build()
    
    # Añadir manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Iniciar Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Iniciar Bot
    logging.info("Iniciando Bot de Telegram...")
    application.run_polling()

if __name__ == '__main__':
    main()
