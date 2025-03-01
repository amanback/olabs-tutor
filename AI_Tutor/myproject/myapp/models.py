from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    has_accepted_answer = models.BooleanField(default=False)
    votes = models.ManyToManyField(User, through='QuestionVote', related_name='question_votes', blank=True)

    def __str__(self):
        return self.title

    def total_votes(self):
        upvotes = Vote.objects.filter(question=self, value=1).count()
        downvotes = Vote.objects.filter(question=self, value=-1).count()
        return upvotes - downvotes

    def total_answers(self):
        return self.answers.count()

class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.title[:50]}"

class QuestionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=[('upvote', 'Upvote'), ('downvote', 'Downvote')])

class Vote(models.Model):
    VOTE_CHOICES = ((1, "Upvote"), (-1, "Downvote"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class View(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="views")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
