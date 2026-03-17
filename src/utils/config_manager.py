import os

class ConfigManager:
    @staticmethod
    def get_mode():
        return os.getenv("SYSTEM_MODE", "manual").lower()

    @staticmethod
    def is_feature_enabled(feature_name):
        # Mapeo de variables de entorno a funciones
        features = {
            "auto_upload": os.getenv("AUTO_UPLOAD", "false").lower() == "true",
            "auto_schedule": os.getenv("AUTO_SCHEDULE", "false").lower() == "true",
            "daily_advice": os.getenv("DAILY_ADVICE", "true").lower() == "true",
            "auto_comments": os.getenv("AUTO_COMMENTS", "true").lower() == "true",
            "deep_analysis": os.getenv("DEEP_ANALYSIS", "true").lower() == "true",
            "github_storage": os.getenv("GITHUB_STORAGE", "true").lower() == "true"
        }
        return features.get(feature_name, False)

    @staticmethod
    def should_auto_publish():
        mode = ConfigManager.get_mode()
        return mode == "automatic" and ConfigManager.is_feature_enabled("auto_upload")

    @staticmethod
    def requires_confirmation():
        mode = ConfigManager.get_mode()
        return mode == "semiautomatic"
