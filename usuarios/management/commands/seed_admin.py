from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crea un superusuario predeterminado si no existe"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "NNK"
        password = "NNK2025IDAT"
        email = ""

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(
                f"✅ Superusuario '{username}' creado."))
        else:
            self.stdout.write(self.style.WARNING(
                f"⚠️ El superusuario '{username}' ya existe."))
