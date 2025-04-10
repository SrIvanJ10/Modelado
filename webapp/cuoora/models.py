from django.db import models

# Create your models here.
class Question(models.Model):
    tittle = models.CharField(max_length=200)

