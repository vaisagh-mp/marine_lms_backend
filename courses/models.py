from django.db import models
from accounts.models import Position, ShipType
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ship_type = models.ForeignKey(ShipType, on_delete=models.CASCADE)
    positions = models.ManyToManyField(Position)  # assigned to multiple positions

    def __str__(self):
        return self.title


class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='modules/', blank=True, null=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Quiz(BaseModel):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')

    def __str__(self):
        return f"Quiz for {self.module.title}"


class Question(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])

    def __str__(self):
        return self.question_text
