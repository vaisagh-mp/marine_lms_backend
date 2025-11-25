from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserCourseProgress, QuizAttempt, UserModuleProgress
from courses.models import Module, Course, Quiz
from .serializers import UserCourseProgressSerializer, QuizAttemptSerializer

# ----------------------------
# Base API for common CRUD
# ----------------------------
class BaseAPIView(APIView):
    model = None
    serializer_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(obj)
            return Response(serializer.data)
        objs = self.model.objects.all()
        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------
# Specific Views
# ----------------------------
class UserCourseProgressAPIView(BaseAPIView):
    model = UserCourseProgress
    serializer_class = UserCourseProgressSerializer


class QuizAttemptAPIView(BaseAPIView):
    model = QuizAttempt
    serializer_class = QuizAttemptSerializer



class CourseProgressAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        user = request.user

        total_modules = Module.objects.filter(course_id=course_id).count()
        completed_modules = UserModuleProgress.objects.filter(
            user=user, module__course_id=course_id, completed=True
        ).count()

        percentage = 0
        if total_modules > 0:
            percentage = round((completed_modules / total_modules) * 100, 2)

        return Response({
            "course_id": course_id,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "progress_percentage": percentage
        })
