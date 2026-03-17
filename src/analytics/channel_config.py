import os

CHANNEL_CONFIGS = {
    "El Tío Jota": {
        "id": os.getenv("ID_CANAL", "UC_EL_TIO_JOTA_ID"),
        "topics": [
            "Análisis de películas",
            "Filosofía",
            "Crecimiento personal",
            "Motivación",
            "Noticias actuales"
        ],
        "description": "Canal enfocado en el crecimiento personal a través del cine, la filosofía y la motivación, analizando la realidad desde una perspectiva crítica y profunda.",
        "website_promo": "https://masitaprex.com/PeliPREX",
        "order": 1
    },
    "El Criterio": {
        "id": os.getenv("ID_CANAL_2", "UC_EL_CRITERIO_ID"),
        "topics": [
            "Análisis crítico",
            "Cine y cultura",
            "Reflexiones filosóficas",
            "Actualidad con criterio"
        ],
        "description": "Canal dedicado al análisis profundo de la cultura, el cine y la sociedad, buscando siempre un criterio propio y fundamentado.",
        "website_promo": "https://masitaprex.com/PeliPREX",
        "order": 2
    }
}

def get_channel_config(channel_name):
    return CHANNEL_CONFIGS.get(channel_name)

def get_all_channels_ordered():
    return sorted(CHANNEL_CONFIGS.items(), key=lambda x: x[1]['order'])
