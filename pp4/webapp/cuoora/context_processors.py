from cuoora.models import Notification
from django.contrib.auth.models import User  # O tu modelo User personalizado

def notifications_count(request):
    # Verificar que request.user es un objeto User válido y está autenticado
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Verificar que request.user no es un string sino un objeto User
        from django.contrib.auth.models import User  # o tu modelo de usuario personalizado
        if isinstance(request.user, User):
            unread_count = Notification.objects.filter(receiver=request.user, read=False).count()
            return {'notifications_count': unread_count}
    return {'notifications_count': 0}