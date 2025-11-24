from rest_framework import serializers
from .models import Course, Module, Quiz, Question, ModuleFile
from accounts.serializers import PositionSerializer, ShipTypeSerializer


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



class QuestionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "option_a", "option_b", "option_c", "option_d"]


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "questions"]


class ModuleDetailSerializer(serializers.ModelSerializer):
    quiz = QuizDetailSerializer(read_only=True)
    files = ModuleFileSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "video",
            "files",
            "quiz"
        ]



class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleDetailSerializer(many=True, read_only=True)
    ship_type = ShipTypeSerializer(read_only=True)
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "ship_type", "positions", "modules"]