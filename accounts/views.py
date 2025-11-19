from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .models import Position, ShipType
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    PositionSerializer,
    ShipTypeSerializer,
    AdminCourseSerializer,
    AdminUserSerializer,
    LearnerProfileSerializer,
    LearnerCourseProgressSerializer,
    CustomTokenObtainPairSerializer,
    LearnerCourseSerializer
)
from courses.models import Course
from progress.models import UserCourseProgress
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AdminDashboardAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Active Employee Count
        active_user_count = User.objects.filter(
            is_active=True,
            role='employee'
        ).count()

        # Assigned Course Count
        assigned_course_count = Course.objects.count()

        # Completion Rate (for employees only)
        total_enrollments = UserCourseProgress.objects.filter(
            user__role='employee'
        ).count()

        completed_courses = UserCourseProgress.objects.filter(
            user__role='employee',
            status='completed'
        ).count()

        completion_rate = 0
        if total_enrollments > 0:
            completion_rate = (completed_courses / total_enrollments) * 100

        # ALL COURSES
        courses = Course.objects.all()
        course_data = AdminCourseSerializer(courses, many=True).data

        # ONLY EMPLOYEES
        users = User.objects.filter(role='employee')
        user_data = AdminUserSerializer(users, many=True).data

        data = {
            "active_user_count": active_user_count,
            "assigned_course_count": assigned_course_count,
            "completion_rate": round(completion_rate, 2),
            "courses": course_data,
            "users": user_data,
        }

        return Response(data, status=status.HTTP_200_OK)


class LearnerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Assigned courses (based on ship type & position)
        assigned_courses = Course.objects.filter(
            ship_type=user.ship_type,
            positions=user.position
        ).distinct()

        # 2. Course Details Serializer
        course_serializer = LearnerCourseSerializer(
            assigned_courses,
            many=True,
            context={'request': request}
        )

        # 3. User Profile
        profile_serializer = LearnerProfileSerializer(user)

        # 4. User Progress for all assigned courses
        progress = UserCourseProgress.objects.filter(user=user)
        progress_serializer = LearnerCourseProgressSerializer(progress, many=True)

        return Response({
            "profile": profile_serializer.data,
            "progress": progress_serializer.data,
            "courses": course_serializer.data
        })

    

# ----------------------------
# Position CRUD (Admin only)
# ----------------------------
class PositionAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        try:
            return Position.objects.get(pk=pk)
        except Position.DoesNotExist:
            return None

    # GET all or detail
    def get(self, request, pk=None):
        if pk:
            position = self.get_object(pk)
            if not position:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = PositionSerializer(position)
            return Response(serializer.data)
        else:
            positions = Position.objects.all()
            serializer = PositionSerializer(positions, many=True)
            return Response(serializer.data)

    # POST create (only list endpoint)
    def post(self, request):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT update
    def put(self, request, pk):
        position = self.get_object(pk)
        if not position:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PositionSerializer(position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH partial update
    def patch(self, request, pk):
        position = self.get_object(pk)
        if not position:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PositionSerializer(position, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    def delete(self, request, pk):
        position = self.get_object(pk)
        if not position:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------
# ShipType CRUD (Admin only)
# ----------------------------
class ShipTypeAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        try:
            return ShipType.objects.get(pk=pk)
        except ShipType.DoesNotExist:
            return None

    # GET all or detail
    def get(self, request, pk=None):
        if pk:
            ship_type = self.get_object(pk)
            if not ship_type:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ShipTypeSerializer(ship_type)
            return Response(serializer.data)
        else:
            ship_types = ShipType.objects.all()
            serializer = ShipTypeSerializer(ship_types, many=True)
            return Response(serializer.data)

    # POST create (only for list endpoint)
    def post(self, request):
        serializer = ShipTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT update
    def put(self, request, pk):
        ship_type = self.get_object(pk)
        if not ship_type:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShipTypeSerializer(ship_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH partial update
    def patch(self, request, pk):
        ship_type = self.get_object(pk)
        if not ship_type:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShipTypeSerializer(ship_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    def delete(self, request, pk):
        ship_type = self.get_object(pk)
        if not ship_type:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        ship_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------
# Admin: User CRUD
# ----------------------------
class UserAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    # GET all or detail
    def get(self, request, pk=None):
        if pk:
            user = self.get_object(pk)
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            # Fetch only employees
            users = User.objects.filter(role='employee')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

    # POST: Create user
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT: Update full user info
    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserCreateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH: Partial update
    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Remove user
    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ----------------------------
# Employee: Own Profile
# ----------------------------
class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
