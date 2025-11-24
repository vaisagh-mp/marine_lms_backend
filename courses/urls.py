from django.urls import path
from .views import CourseAPIView, ModuleAPIView, QuizAPIView, QuestionAPIView, LearnerCourseDetailAPIView

urlpatterns = [
    # Courses
    path('', CourseAPIView.as_view(), name="course-list-create"),
    path('<int:pk>/', CourseAPIView.as_view(), name="course-detail"),
    path('learner/<int:course_id>/', LearnerCourseDetailAPIView.as_view(), name='learner-course-detail'),

    # Modules
    path('modules/', ModuleAPIView.as_view(), name="module-list-create"),
    path('modules/<int:pk>/', ModuleAPIView.as_view(), name="module-detail"),

    # Quizzes
    path('quizzes/', QuizAPIView.as_view(), name="quiz-list-create"),
    path('quizzes/<int:pk>/', QuizAPIView.as_view(), name="quiz-detail"),

    # Questions
    path('questions/', QuestionAPIView.as_view(), name="question-list-create"),
    path('questions/<int:pk>/', QuestionAPIView.as_view(), name="question-detail"),
]
