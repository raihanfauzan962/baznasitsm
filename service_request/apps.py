from django.apps import AppConfig

class ServiceRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service_request'
    verbose_name = "Service Request"

    def ready(self):
        import service_request.signals  # Import the signals module to register the signals
