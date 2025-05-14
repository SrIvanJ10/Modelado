from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class User(models.Model):
    django_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    topics_of_interest = models.ManyToManyField('Topic', related_name='interested_users', blank=True)
    
    def __str__(self):
        return self.django_user.username
    
    def calculate_score(self):
        question_score = sum(10 for q in self.questions.all() 
                          if q.positive_votes().count() > q.negative_votes().count())
        answer_score = sum(20 for a in self.answers.all() 
                         if a.positive_votes().count() > a.negative_votes().count())
        return question_score + answer_score

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Para el Generic Foreign Key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
    
    def __str__(self):
        vote_type = "positive" if self.is_positive_vote else "negative"
        return f"{vote_type} vote by {self.user} on {self.content_object}"

class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    topics = models.ManyToManyField(Topic, related_name='questions')
    votes = GenericRelation(Vote)
    visible = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def positive_votes(self):
        return self.votes.filter(is_positive_vote=True)
    
    def negative_votes(self):
        return self.votes.filter(is_positive_vote=False)
    
    def add_topic(self, topic):
        self.topics.add(topic)
    
    def get_best_answer(self):
        if not self.answers.exists():
            return None
        return self.answers.annotate(
            score=models.Count('votes', filter=models.Q(votes__is_positive_vote=True)) - 
                  models.Count('votes', filter=models.Q(votes__is_positive_vote=False))
        ).order_by('-score').first()
        
    def get_content_type(self):
        return ContentType.objects.get_for_model(self)

class Answer(models.Model):
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    votes = GenericRelation(Vote)
    
    def __str__(self):
        return f"Answer to: {self.question.title[:30]}"
    
    def positive_votes(self):
        return self.votes.filter(is_positive_vote=True)
    
    def negative_votes(self):
        return self.votes.filter(is_positive_vote=False)
    
    def get_content_type(self):
        return ContentType.objects.get_for_model(self)

class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    text = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']