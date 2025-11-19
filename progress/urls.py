from django.urls import path
from .views import UserCourseProgressAPIView, QuizAttemptAPIView

urlpatterns = [
    # User Course Progress
    path('', UserCourseProgressAPIView.as_view(), name='usercourseprogress-list-create'),
    path('<int:pk>/', UserCourseProgressAPIView.as_view(), name='usercourseprogress-detail'),

    # Quiz Attempts
    path('quiz-attempts/', QuizAttemptAPIView.as_view(), name='quizattempt-list-create'),
    path('quiz-attempts/<int:pk>/', QuizAttemptAPIView.as_view(), name='quizattempt-detail'),
]
