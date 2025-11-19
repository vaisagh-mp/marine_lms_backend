from django.contrib import admin
from .models import UserCourseProgress, QuizAttempt


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "started_at", "completed_at")
    list_filter = ("status", "course")
    search_fields = ("user__username", "course__title")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "passed", "attempted_at")
    list_filter = ("passed", "quiz")
    search_fields = ("user__username", "quiz__module__title")
