from rest_framework import serializers
from .models import UserCourseProgress, QuizAttempt
from courses.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCourseProgressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = UserCourseProgress
        fields = '__all__'

    def to_representation(self, instance):
        """Show names instead of IDs in response"""
        rep = super().to_representation(instance)
        rep['user'] = instance.user.username
        rep['course'] = instance.course.title
        return rep


class QuizAttemptSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    quiz = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = QuizAttempt
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = instance.user.username
        rep['quiz'] = instance.quiz.module.title
        return rep
