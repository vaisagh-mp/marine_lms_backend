from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserCourseProgress, QuizAttempt, UserModuleProgress
from courses.models import Module, Course, Quiz
from django.utils import timezone
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


class QuizAttemptAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        quiz_id = request.data.get("quiz")
        user_answers = request.data.get("answers", {})  

        # Validate quiz
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found"}, status=404)

        questions = quiz.questions.all()

        correct_count = 0
        total_questions = questions.count()
        detailed_results = []

        # ---------- VALIDATION ----------
        for q in questions:
            user_answer = user_answers.get(str(q.id))  # user's selected option
            is_correct = (user_answer == q.correct_answer)

            if is_correct:
                correct_count += 1

            detailed_results.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "your_answer": user_answer,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct,
            })

        # quiz passed ONLY if all answers correct
        passed = (correct_count == total_questions)

        # ---------- Save quiz attempt ----------
        attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            score=correct_count,
            passed=passed
        )

        # ---------- Update Module Progress ----------
        module = quiz.module

        if passed:
            UserModuleProgress.objects.update_or_create(
                user=user,
                module=module,
                defaults={
                    "completed": True,
                    "completed_at": timezone.now()
                }
            )
        else:
            # ensure module record exists
            UserModuleProgress.objects.get_or_create(
                user=user,
                module=module
            )

        # ---------- Update Course Progress ----------
        course = module.course
        total_modules = course.modules.count()
        completed_modules = UserModuleProgress.objects.filter(
            user=user, module__course=course, completed=True
        ).count()

        # complete course if all modules done
        if completed_modules == total_modules and passed:
            UserCourseProgress.objects.update_or_create(
                user=user,
                course=course,
                defaults={
                    "status": "completed",
                    "completed_at": timezone.now()
                }
            )
        else:
            # in progress if at least started
            UserCourseProgress.objects.update_or_create(
                user=user,
                course=course,
                defaults={"status": "in_progress"}
            )

        # ---------- Response ----------
        return Response({
            "quiz_id": quiz.id,
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "passed": passed,
            "results": detailed_results   # return correct answers
        }, status=201)



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
