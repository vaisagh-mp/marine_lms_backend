from django.urls import path
from .views import UserCourseProgressAPIView, QuizAttemptAPIView, CourseProgressAPIView

urlpatterns = [
    # User Course Progress
    path('', UserCourseProgressAPIView.as_view(), name='usercourseprogress-list-create'),
    path('<int:pk>/', UserCourseProgressAPIView.as_view(), name='usercourseprogress-detail'),

    # Quiz Attempts
    path('quiz-attempts/', QuizAttemptAPIView.as_view(), name='quizattempt-list-create'),
    path('quiz-attempts/<int:pk>/', QuizAttemptAPIView.as_view(), name='quizattempt-detail'),

    path("course/<int:course_id>/", CourseProgressAPIView.as_view(), name="course-progress"),
]
