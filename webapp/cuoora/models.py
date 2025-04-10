from django.db import models

# Create your models here.
class Question(models.Model):
   tittle = models.CharField(max_length=200)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField(null=True)

class Description(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    content = models.TextField(null=True)
