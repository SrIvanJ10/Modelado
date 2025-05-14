from datetime import datetime, timedelta
from cuoora.models import Question
from .notifications import create_result_question_notification
from .models import Question
import requests

from celery import shared_task 

@shared_task(bind=True)
def create_reminders(self):
    print("Creating reminders...")
    toDos = ToDoItem.objects.filter(completed=False)

@shared_task(bind=True)
def send_result(self, success, question_id):
    try:
        question = Question.objects.get(id=question_id)
        if (success):
            question.visible = True
            question.save()
            print("Pregunta publicada")
            create_result_question_notification(question, "Pregunta publicada")
        else:
            question.visible = False
            question.save()
            print("no se puede publicar tu pregunta")
            create_result_question_notification(question, "no se puede publicar tu pregunta")
    except Question.DoesNotExist:
        print(f"Error: No se encontró la pregunta con ID {question_id}")
    
@shared_task(bind=True)
def analyzing_question(self, board_id):
    print("A board was created and notifications are being sent...")
    print(board_id)

    try:
        question = Question.objects.get(id=board_id)
        title_text = question.title
        description_text = question.description
    except Question.DoesNotExist:
        print(f"Error: No se encontró la pregunta con ID {board_id}")
        # No podemos enviar notificación si no existe la pregunta
        return

    # Configuración
    base_url = "http://172.19.0.1:8001"
    login_data = {
        "username": "Dios",
        "password": "1234"
    }

    # 1. Obtener el token de acceso
    token_url = f"{base_url}/api/auth/token/"
    headers_token = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    print("Obteniendo token de autorización...")
    response_token = requests.post(token_url, json=login_data, headers=headers_token)

    if response_token.status_code == 200:       
        print(response_token.json())
        access_token = response_token.json().get("access")
        print("Access Token:", access_token)
    else:
        print("Error al obtener el token:", response_token.text)
        # MODIFICADO: Llamar a send_result en lugar de exit()
        send_result.delay(False, board_id)
        return

    # 2. Consumir el segundo endpoint con el token
    analysis_url = f"{base_url}/api/analyzer/analysis/"
    headers_analysis = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data_analysis = {
        "texts_list": [
            {"id": "title", "text": title_text}, 
            {"id": "description", "text": description_text}
        ]
    }

    print("Consumiendo analysis endpoint...")  # Corregido typo
    print(headers_analysis)
    response_analysis = requests.post(analysis_url, json=data_analysis, headers=headers_analysis)

    if response_analysis.status_code == 201:
        analysis_result = response_analysis.json()
        print("Respuesta del análisis:", analysis_result)
        
        # Verificar si alguno de los textos contiene palabrotas
        contains_bad_words = False
        
        for result in analysis_result.get('retrieved_result', []):
            # Si algún texto contiene palabrotas, marcar como True
            if result.get('palabrotas', {}).get('contains', False):
                contains_bad_words = True
                break
        
        # MODIFICADO: Pasar board_id en lugar del objeto Question
        send_result.delay(not contains_bad_words, board_id)
        
    else:
        print("Error al consumir el endpoint de análisis:", response_analysis.text)
        # Si hay error en el análisis, no se puede publicar
        send_result.delay(False, board_id)