from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Course, Module, Quiz, Question, ModuleFile
from .serializers import CourseSerializer, ModuleSerializer, QuizSerializer, QuestionSerializer


# ----------------------------
# Custom permission
# ----------------------------
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin: full access
    Employee: GET only
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return request.user.is_authenticated
        return request.user.is_staff or request.user.role == 'admin'


# ----------------------------
# Base class for CRUD
# ----------------------------
class BaseAPIView(APIView):
    model = None
    serializer_class = None
    permission_classes = [IsAdminOrReadOnly]

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

        # Filter courses/modules for employees
        if request.user.role == 'employee':
            if hasattr(objs.model, 'positions') and hasattr(objs.model, 'ship_type'):
                objs = objs.filter(
                    positions=request.user.position,
                    ship_type=request.user.ship_type
                )

        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        is_many = isinstance(request.data, list)
        serializer = self.serializer_class(data=request.data, many=is_many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------
# Specific Views
# ----------------------------
class CourseAPIView(BaseAPIView):
    model = Course
    serializer_class = CourseSerializer


class ModuleAPIView(BaseAPIView):
    model = Module
    serializer_class = ModuleSerializer

    def post(self, request):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        # Extract normal module data
        module_data = request.data.copy()
        module_files = request.FILES.getlist("files")  # multiple files

        serializer = self.serializer_class(data=module_data)
        if serializer.is_valid():
            module = serializer.save()

            # Save multiple files
            for file_obj in module_files:
                ModuleFile.objects.create(module=module, file=file_obj)

            return Response(self.serializer_class(module).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        module = self.get_object(pk)
        if not module:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        module_data = request.data.copy()
        module_files = request.FILES.getlist("files")  # multiple files

        serializer = self.serializer_class(module, data=module_data, partial=True)
        if serializer.is_valid():
            module = serializer.save()

            # Add new files (existing files stay)
            for file_obj in module_files:
                ModuleFile.objects.create(module=module, file=file_obj)

            return Response(self.serializer_class(module).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class QuizAPIView(BaseAPIView):
    model = Quiz
    serializer_class = QuizSerializer


class QuestionAPIView(BaseAPIView):
    model = Question
    serializer_class = QuestionSerializer
