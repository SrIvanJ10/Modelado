from .models import Notification

def create_answer_notification(question, answer):
    # No crear notificación si el autor de la pregunta es quien responde
    if question.user == answer.user:
        return
    
    # Crear la notificación para el autor de la pregunta
    text = f"{answer.user} ha respondido a una de tus preguntas."
    link = f"/question/{question.id}/"  # Ajusta esto a tu estructura de URLs
    
    Notification.objects.create(
        receiver=question.user,
        text=text,
        link=link
    )

def create_vote_notification(content_object, voter):
    # No crear notificación si el autor del contenido es quien vota
    if content_object.user == voter:
        return
    
    # Determinar si es pregunta o respuesta
    if hasattr(content_object, 'question'):
        # Es una respuesta
        content_type = "respuesta"
        link = f"/question/{content_object.question.id}/"
    else:
        # Es una pregunta
        content_type = "pregunta"
        link = f"/question/{content_object.id}/"
    
    # Crear la notificación
    text = f"{voter.username} ha votado una de tus {content_type}s."
    
    Notification.objects.create(
        receiver=content_object.user,
        text=text,
        link=link
    )

def create_celery_notification(question):
    # Crear la notificación para el autor de la pregunta
    text = f"Se está revisando tu pregunta antes de ser publicada.\n le llegará otra notificación con el resultado del analisis y si se aprueba su publicación"
    link = f"/notifications/"  # Ajusta esto a tu estructura de URLs
    
    Notification.objects.create(
        receiver=question.user,
        text=text,
        link=link
    )

def create_result_question_notification(question, text_result):
    # Crear la notificación para el autor de la pregunta
    text = text_result
    link = f"/notifications/"  # Ajusta esto a tu estructura de URLs
    
    Notification.objects.create(
        receiver=question.user,
        text=text,
        link=link
    )