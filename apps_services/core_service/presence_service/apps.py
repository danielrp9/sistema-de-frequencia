from django.apps import AppConfig


class PresenceServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'presence_service'

    def ready(self):
        import presence_service.signals
