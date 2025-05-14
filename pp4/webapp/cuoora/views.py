from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import date
from .models import Question, Answer, Vote, User, Topic, Notification
from .forms import AnswerForm, QuestionForm
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .notifications import create_answer_notification, create_celery_notification, create_vote_notification

# Lógica para los diferentes retrievers
class QuestionRetriever:
    @staticmethod   
    def get_social_questions(user, limit=100):
        following_users = user.following.all()
        questions = Question.objects.filter(user__in=following_users, visible=True)
        return QuestionRetriever._filter_and_sort(questions, user, limit)
    
    @staticmethod
    def get_topic_questions(user, limit=100):
        topics = user.topics_of_interest.all()
        questions = Question.objects.filter(topics__in=topics, visible=True).distinct()
        return QuestionRetriever._filter_and_sort(questions, user, limit)
    
    @staticmethod
    def get_news_questions(user, limit=100):
        # Imprimimos para depuración
        print("Buscando preguntas recientes...")
        
        # Usamos una lógica más flexible para encontrar preguntas recientes
        from datetime import timedelta
        recent_date = date.today()

        questions = Question.objects.filter(timestamp__date__gte=recent_date, visible=True)
        print(f"Encontradas {questions.count()} preguntas recientes")
        
        # Si no hay preguntas recientes, mostrar todas
        if not questions.exists():
            print("No hay preguntas recientes, mostrando todas")
            return Question.objects.filter(visible=True)
        
        return QuestionRetriever._filter_and_sort(questions, user, limit)
    
    @staticmethod
    def get_popular_questions(user, limit=100):
        today = date.today()
        from django.db.models import Count, Q
        
        questions = Question.objects.filter(timestamp__date=today, visible=True)
        if not questions.exists():
            print("no existen preguntas en popular")
            return []
        
        # Calcular el promedio de votos positivos
        questions = questions.annotate(
            positive_count=Count('votes', filter=Q(votes__is_positive_vote=True))
        )
        
        avg_positive = sum(q.positive_count for q in questions) / questions.count()
        
        # Filtrar las preguntas con más votos positivos que el promedio
        popular_questions = [q for q in questions if q.positive_count > avg_positive]
        
        return QuestionRetriever._filter_and_sort_list(popular_questions, user, limit)
    
    @staticmethod
    def _filter_and_sort(questions_queryset, user, limit):
        # Excluir preguntas del usuario actual
        #questions = questions_queryset.exclude(user=user)
        questions = questions_queryset
        
        # Convertir a lista para ordenar por número de votos positivos
        questions_list = list(questions)
        return QuestionRetriever._filter_and_sort_list(questions_list, user, limit)
    
    @staticmethod
    def _filter_and_sort_list(questions_list, user, limit):
        # Ordenar por número de votos positivos (de mayor a menor)
        sorted_questions = sorted(
            questions_list, 
            key=lambda q: q.positive_votes().count(),
            reverse=True
        )
        
        # Limitar a 'limit' resultados
        return sorted_questions[:min(limit, len(sorted_questions))]

def notifications_list(request):
    user = request.user
        
    # Usar el ORM para filtrar las notificaciones eficientemente
    notifications = Notification.objects.filter(receiver=request.user.id).select_related('receiver')
    unread_notifications = notifications.filter(read=False)
    
    context = {
        'notifications': notifications,
        'unread_notifications': unread_notifications
    }
    
    return render(request, 'cuoora/notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, receiver=request.user)
        notification.read = True
        notification.save()
    except Notification.DoesNotExist:
        pass
    
    # Redirigir a la URL almacenada en la notificación
    return redirect(notification.link)

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(receiver=request.user, read=False).update(read=True)
    return redirect('notifications_list')

def search_questions(request):
    query = request.GET.get('query', '')
    
    if query:
        # Buscar preguntas que contengan la consulta en el título
        questions = Question.objects.filter(title__icontains=query)
    else:
        # Si no hay consulta, mostrar una lista vacía
        questions = Question.objects.none()
    
    context = {
        'questions': questions,
        'query': query,
    }
    
    return render(request, 'cuoora/search_results.html', context)

@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user_id = request.user.id
            question.visible = False
            question.save()  # Guardamos primero para poder añadir los topics (ManyToMany)
            
            # Añadir topics existentes seleccionados
            existing_topics = form.cleaned_data.get('existing_topics')
            if existing_topics:
                for topic in existing_topics:
                    question.add_topic(topic)
            
            # Crear y añadir un nuevo topic si se proporciona
            new_topic_name = form.cleaned_data.get('new_topic')
            if new_topic_name:
                # Creamos o recuperamos el topic (para evitar duplicados)
                new_topic, created = Topic.objects.get_or_create(name=new_topic_name)
                question.add_topic(new_topic)
            
            create_celery_notification(question)
            from .tasks import analyzing_question
            analyzing_question.delay(question.id)

            return redirect('/')
    else:
        form = QuestionForm()
    return render(request, 'cuoora/create_question.html', {'form': form})

@login_required
def home(request):
    # Obtener o crear el usuario de CuOOra para el usuario de Django
    user, created = User.objects.get_or_create(
        django_user=request.user
    )
    
    # Determinar qué tipo de retriever usar
    retriever_type = request.GET.get('retriever', 'social')
    
    # Obtener las preguntas según el tipo de retriever
    if retriever_type == 'topics':
        questions = QuestionRetriever.get_topic_questions(user)
    elif retriever_type == 'news':
        questions = QuestionRetriever.get_news_questions(user)
    elif retriever_type == 'popular':
        questions = QuestionRetriever.get_popular_questions(user)
    else:  # Default: social
        questions = QuestionRetriever.get_social_questions(user)
    
    # Obtener todas las notificaciones del usuario
    notifications = Notification.objects.filter(receiver_id=request.user.id)
    
    # Contar las notificaciones no leídas
    unread_notifications_count = notifications.filter(read=False).count()

    context = {
        'questions': questions,
        'selected_retriever': retriever_type,
        'current_user': user,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    }
    
    return render(request, 'cuoora/home.html', context)

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user, created = User.objects.get_or_create(django_user=request.user)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = user
            answer.question = question
            answer.timestamp = timezone.now()
            answer.save()
            
            #if question.user != user:
            create_answer_notification(question, answer)
            
            return redirect('question_detail', question_id=question.id)
    else:
        form = AnswerForm()
    
    context = {
        'question': question,
        'form': form,
        'current_user': user
    }
    
    return render(request, 'cuoora/question_detail.html', context)

@login_required
def vote(request, content_type_id, object_id, is_positive):
    content_type = get_object_or_404(ContentType, pk=content_type_id)
    votable_object = get_object_or_404(content_type.model_class(), pk=object_id)
    user, created = User.objects.get_or_create(django_user=request.user)
    
    # Verificar si el usuario ya ha votado en este objeto
    vote, created = Vote.objects.get_or_create(
        user=user,
        content_type=content_type,
        object_id=object_id,
        defaults={'is_positive_vote': is_positive == 1}
    )
    
    if not created:
        vote.is_positive_vote = is_positive == 1
        vote.save()
    
    # Obtener el autor del objeto votado
    if hasattr(votable_object, 'user'):
        content_author = votable_object.user
        
        # Solo crear notificación si el autor no es quien vota
        if content_author != user:
            # Determinar si es pregunta o respuesta
            if content_type.model == 'question':
                content_type_name = "pregunta"
                link = f"/questions/{votable_object.id}/"
            else:  # Asumimos que es una respuesta
                content_type_name = "respuesta"
                link = f"/questions/{votable_object.question.id}/"
            
            # Crear la notificación
            Notification.objects.create(
                receiver=content_author,
                text=f"{user.django_user.username} ha votado una de sus {content_type_name}s. Ver.",
                link=link,
                read=False
            )
    
    # Redirigir de regreso a la página anterior
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def topic_list(request):
    # Obtener o crear el usuario de CuOOra
    user, created = User.objects.get_or_create(django_user=request.user)
    
    # Obtener todos los topics ordenados por nombre
    topics = Topic.objects.all().order_by('name')
    
    # Paginación (opcional)
    paginator = Paginator(topics, 20)  # 20 topics por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'topics': page_obj,  # Usar 'topics' si no quieres paginación
        'current_user': user
    }
    
    return render(request, 'cuoora/topic_list.html', context)