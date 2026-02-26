from django.apps import AppConfig


# PatientsConfig with ready() method to import signal handlers for auto-creating Patient profiles when new users are created, ensuring seamless integration between user accounts and patient profiles.
class PatientsConfig(AppConfig):
    name = 'patients'
    
    def ready(self):
        # import signal handlers to auto-create Patient profiles
        try:
            import patients.signals  # noqa: F401
        except Exception:
            pass
