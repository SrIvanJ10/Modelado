from django.shortcuts import render
from cuoora.models import Question, Answer, Description


def home(request):
    questions = Question.objects.all()
    answers = Answer.objects.all()
    descriptions = Description.objects.all()
    context = {"questions": questions,
               "answers": answers,
               "descriptions": descriptions
                }

    return render(request, 'home.html', context)

