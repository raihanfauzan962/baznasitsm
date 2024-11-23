from django.apps import AppConfig

class IncidentReportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incident_report'
    verbose_name = "Incident Report" 

    def ready(self):
        # Import and register your signals here
        import incident_report.signals  # This ensures your signals are connected
