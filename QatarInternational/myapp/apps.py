from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from .models import Users
        try:
            if not Users.objects.filter(username='admin').exists():
                Users.objects.create(
                    username='admin',
                    email='admin@gmail.com',
                    password='admin',  # You can hash this later
                    role='admin',
                    is_active=True
                )
        except (OperationalError, ProgrammingError):
            # DB table might not be ready yet (initial migration time)
            pass
