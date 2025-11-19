from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Position, ShipType
from courses.models import Course, Module
from progress.models import UserCourseProgress
from django.contrib.auth.models import update_last_login

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom JWT payload fields
        token['username'] = user.username
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Update last login manually
        update_last_login(None, self.user)

        # Add custom response fields
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['role'] = self.user.role
        data['last_login'] = self.user.last_login

        return data


class ShipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipType
        fields = ['id', 'name', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)
    ship_type = ShipTypeSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'position', 'ship_type',
            'role', 'last_login', 'created_at'
        ]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'position', 'ship_type',
            'role', 'password'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminCourseSerializer(serializers.ModelSerializer):
    ship_type = serializers.CharField(source="ship_type.name")
    positions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    modules_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "ship_type", "positions", "modules_count"]

    def get_modules_count(self, obj):
        return obj.modules.count()


class AdminUserSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source="position.name", default=None)
    ship_type = serializers.CharField(source="ship_type.name", default=None)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "role", "position", "ship_type", "last_login", "created_at"]


class LearnerProfileSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source="position.name", default=None)
    ship_type = serializers.CharField(source="ship_type.name", default=None)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "position", "ship_type", "role"]


class LearnerCourseProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = UserCourseProgress
        fields = ["course_id", "course_title", "status", "started_at", "completed_at"]


class LearnerCourseSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    modules_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "modules_count", "status"]

    def get_status(self, obj):
        user = self.context['request'].user
        progress = UserCourseProgress.objects.filter(user=user, course=obj).first()
        return progress.status if progress else "not_started"

    def get_modules_count(self, obj):
        return obj.modules.count()
