from rest_framework import serializers
from .models import Course, Module, Quiz, Question, ModuleFile


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class ModuleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleFile
        fields = ["id", "file"]


class ModuleSerializer(serializers.ModelSerializer):
    files = ModuleFileSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = "__all__"


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
