# 📺 Sistema Automático de Publicación para YouTube - Canal "El Tío Jota"

Este sistema automatiza la recepción de videos desde Telegram, analiza el mejor horario de publicación basado en la audiencia del canal, genera metadatos optimizados (título, descripción, hashtags) y realiza la subida a YouTube mediante la API oficial.

## 🚀 Características

- **Recepción vía Telegram**: Envía un video al bot y el sistema se encarga del resto.
- **Análisis de Audiencia**: Utiliza YouTube Analytics para encontrar la hora de mayor impacto.
- **Optimización con IA**: Generación automática de títulos y descripciones optimizados para SEO.
- **Modos de Control**: Soporta modos Manual, Semiautomático y Automático.
- **Listo para Railway**: Configuración incluida para despliegue inmediato.

## 🛠️ Requisitos Previos

1. **Telegram Bot Token**: Créalo con [@BotFather](https://t.me/botfather).
2. **Google Cloud Project**:
   - Habilita YouTube Data API v3 y YouTube Analytics API.
   - Crea credenciales OAuth 2.0.
   - Obtén el `Client ID`, `Client Secret` y un `Refresh Token`.
3. **OpenAI API Key** (Opcional): Para generación de metadatos con IA.

## 📦 Instalación y Despliegue

### Local
1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`.
3. Configura el archivo `.env` basándote en `.env.example`.
4. Ejecuta: `python main.py`.

### Railway
1. Conecta este repositorio a tu cuenta de Railway.
2. Configura las **Variables de Entorno** en el panel de Railway.
3. El sistema se desplegará automáticamente usando el `Procfile`.

## ⚙️ Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token de tu bot de Telegram. |
| `YOUTUBE_CLIENT_ID` | ID de cliente de Google Cloud. |
| `YOUTUBE_CLIENT_SECRET` | Secreto de cliente de Google Cloud. |
| `YOUTUBE_REFRESH_TOKEN` | Token de refresco para acceso permanente. |
| `OPENAI_API_KEY` | (Opcional) Para optimización con GPT. |
| `SYSTEM_MODE` | `manual`, `semiautomatic` o `automatic`. |

## 🔒 Seguridad y Políticas

Este sistema utiliza únicamente la **API oficial de YouTube** y cumple con sus políticas de uso. No utiliza técnicas de spam ni bots prohibidos.

---
Desarrollado para el canal **El Tío Jota**.
