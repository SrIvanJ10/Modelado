import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from cuoora.models import User as CuooraUser

# Obtener el modelo de usuario configurado en AUTH_USER_MODEL
UserModel = apps.get_model(settings.AUTH_USER_MODEL)

# Obtener todos los usuarios
django_users = UserModel.objects.all()

# Asegurarse de que cada usuario tenga un perfil de CuOOra
for django_user in django_users:
    cuoora_user, created = CuooraUser.objects.get_or_create(django_user=django_user)
    if created:
        print(f"Perfil de CuOOra creado para: {django_user.username}")
    else:
        print(f"El usuario {django_user.username} ya tiene un perfil de CuOOra")    