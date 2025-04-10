from django.shortcuts import render
from cuoora.models import Question

def home(request):
    questions = Question.objects.all()
    context = {"questions": questions}

    return render(request, 'home.html', context)

