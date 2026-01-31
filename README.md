# 📺 Sistema Automático de Publicación para YouTube - Canal "El Tío Jota"

Este sistema avanzado automatiza la gestión de contenidos para YouTube desde Telegram, integrando análisis de tendencias y programación inteligente.

## ✨ Novedades: Aviso Diario de Contenido
Cada mañana, el sistema analiza tendencias (Google/YouTube Trends) y el rendimiento histórico del canal para enviarte una sugerencia de publicación vía Telegram:
- **Tema recomendado** basado en tendencias actuales.
- **Título e Idea** de contenido.
- **Formato sugerido** (Short o Video Largo).
- **Hora óptima** de publicación.

## 🚀 Características Principales

- **Recepción vía Telegram**: Envía un video y el sistema procesa la subida.
- **Análisis de Audiencia**: Determina la hora de mayor impacto.
- **Optimización con IA**: Metadatos generados para maximizar el SEO.
- **Modos de Control**: 
  - `manual`: Solo sugerencias, tú decides qué hacer.
  - `semiautomatic`: El sistema prepara todo y pide tu confirmación final.
  - `automatic`: Gestión total sin intervención.

## ⚙️ Configuración y Seguridad

Puedes activar o desactivar funciones específicas mediante variables de entorno:
- `AUTO_UPLOAD`: Habilita la subida automática.
- `AUTO_SCHEDULE`: Habilita la programación según analíticas.
- `DAILY_ADVICE`: Activa el mensaje matutino de sugerencias.
- `SYSTEM_MODE`: Cambia entre los modos de control.

## 🛠️ Requisitos e Instalación

1. **Tokens**: Necesitas `TELEGRAM_BOT_TOKEN`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` y `YOUTUBE_REFRESH_TOKEN`.
2. **OpenAI**: Opcional para mejores sugerencias de títulos.
3. **Despliegue**: Listo para Railway mediante el `Procfile` incluido.

---
Desarrollado para el canal **El Tío Jota**.
