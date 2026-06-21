from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    """
    Configuración de la aplicación 'website'.
    Establece el tipo de campo clave auto-incremental por defecto (BigAutoField)
    y registra el nombre modular de la aplicación dentro del proyecto Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'
