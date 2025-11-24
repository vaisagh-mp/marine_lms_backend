from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Course, Module, Quiz, Question, ModuleFile
from .serializers import CourseSerializer, ModuleSerializer, QuizSerializer, QuestionSerializer,CourseDetailSerializer


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

    def get(self, request, pk=None):
       # If single module by ID
       if pk:
           module = self.get_object(pk)
           if not module:
               return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
           serializer = self.serializer_class(module)
           return Response(serializer.data)

       # If course id is passed as query param → filter
       course_id = request.query_params.get("course")
       if course_id:
           modules = Module.objects.filter(course_id=course_id)
       else:
           modules = Module.objects.all()

       serializer = self.serializer_class(modules, many=True)
       return Response(serializer.data)

    # FULL OVERRIDE of BaseAPIView.post (BaseAPIView.post is ignored now)
    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.role == 'admin'):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        # Prevent many=True error
        if isinstance(request.data, list):
            return Response(
                {"detail": "List upload is not allowed for modules."},
                status=status.HTTP_400_BAD_REQUEST
            )

        module_data = request.data.copy()
        module_files = request.FILES.getlist("files")

        serializer = self.serializer_class(data=module_data)

        if serializer.is_valid():
            module = serializer.save()

            # Save files
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

    def get(self, request, pk=None):
        # If specific quiz requested
        if pk:
            quiz = self.get_object(pk)
            if not quiz:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(quiz)
            return Response(serializer.data)

        # Filter quizzes by course ID
        course_id = request.query_params.get("course")
        if course_id:
            quizzes = Quiz.objects.filter(module__course_id=course_id)
        else:
            quizzes = Quiz.objects.all()

        serializer = self.serializer_class(quizzes, many=True)
        return Response(serializer.data)



class QuestionAPIView(BaseAPIView):
    model = Question
    serializer_class = QuestionSerializer

    def get(self, request, pk=None):
        # If single question requested
        if pk:
            question = self.get_object(pk)
            if not question:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(question)
            return Response(serializer.data)

        # Filter questions by course ID
        course_id = request.query_params.get("course")
        if course_id:
            questions = Question.objects.filter(quiz__module__course_id=course_id)
        else:
            questions = Question.objects.all()

        serializer = self.serializer_class(questions, many=True)
        return Response(serializer.data)


class LearnerCourseDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        user = request.user

        # Ensure learner is eligible for this course (role=employee only)
        try:
            course = Course.objects.get(
                id=course_id,
                ship_type=user.ship_type,
                positions=user.position
            )
        except Course.DoesNotExist:
            return Response(
                {"detail": "You do not have access to this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)