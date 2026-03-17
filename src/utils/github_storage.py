import os
import json
import base64
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

def save_to_github_json(data_to_save, filename="data.json"):
    """
    Guarda o actualiza información en un archivo JSON directamente en el repositorio de GitHub.
    Usa las variables de entorno GITHUB_REPO y GITHUB_TOKEN.
    """
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    
    if not repo or not token:
        logger.error("Faltan GITHUB_REPO o GITHUB_TOKEN para persistencia en GitHub.")
        # Guardar localmente como fallback para debugging
        with open(filename, "w") as f:
            json.dump(data_to_save, f, indent=2)
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Intentar obtener el archivo actual para conseguir el 'sha'
        response = requests.get(url, headers=headers)
        current_content = []
        sha = None

        if response.status_code == 200:
            file_data = response.json()
            sha = file_data["sha"]
            content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
            current_content = json.loads(content_decoded)
            if not isinstance(current_content, list):
                current_content = [current_content]
        
        # 2. Añadir el nuevo registro
        new_entry = {
            "canal": data_to_save.get("canal"),
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "analisis": data_to_save
        }
        current_content.append(new_entry)
        
        # 3. Preparar el payload para la API de GitHub
        new_content_json = json.dumps(current_content, indent=2, ensure_ascii=False)
        content_encoded = base64.b64encode(new_content_json.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": f"Actualización automática de análisis: {data_to_save.get('canal')} - {new_entry['fecha']}",
            "content": content_encoded,
            "sha": sha if sha else None
        }

        # 4. Enviar la actualización
        put_response = requests.put(url, headers=headers, json=payload)
        if put_response.status_code in [200, 201]:
            logger.info(f"Archivo {filename} actualizado con éxito en GitHub para el canal {data_to_save.get('canal')}.")
            return True
        else:
            logger.error(f"Error al actualizar {filename} en GitHub: {put_response.status_code} - {put_response.text}")
            return False

    except Exception as e:
        logger.error(f"Excepción al guardar en GitHub: {e}")
        return False

def check_if_analyzed_today(channel_name, filename="data.json"):
    """
    Verifica si un canal ya ha sido analizado en el día actual consultando el archivo en GitHub.
    """
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    
    if not repo or not token:
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
            history = json.loads(content_decoded)
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            for entry in history:
                if entry.get("canal") == channel_name and entry.get("fecha") == today:
                    return True
        return False
    except Exception as e:
        logger.error(f"Error al verificar análisis previo en GitHub: {e}")
        return False
