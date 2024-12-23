from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Topic(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )
    max_attempts = models.IntegerField(default=3)  # Maximum attempts allowed per user

    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"

class UserTopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    best_score = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'topic']

    def can_attempt_quiz(self):
        return self.attempts < self.topic.max_attempts
    
    @property
    def performance_score(self):
        """
        Calculate a performance score that considers:
        - Best score achieved
        - Number of attempts taken
        - Difficulty level of the topic
        """
        difficulty_multiplier = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.0
        }
        base_score = self.best_score * difficulty_multiplier[self.topic.difficulty_level]
        attempt_factor = 1 + (0.1 * (self.topic.max_attempts - self.attempts))
        return base_score * attempt_factor

class Quiz(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.topic.name} quiz"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    selected_answer = models.CharField(max_length=500, null=True, blank=True)
    correct_answer = models.CharField(max_length=500)
    explanation = models.TextField()

    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
