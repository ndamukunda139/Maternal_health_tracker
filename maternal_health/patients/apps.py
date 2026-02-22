from django.apps import AppConfig


class PatientsConfig(AppConfig):
    name = 'patients'
    
    def ready(self):
        # import signal handlers to auto-create Patient profiles
        try:
            import patients.signals  # noqa: F401
        except Exception:
            pass
