from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    PositionAPIView,
    ShipTypeAPIView,
    UserAPIView,
    UserProfileAPIView,
    AdminDashboardAPIView,
    LearnerDashboardAPIView
)

urlpatterns = [
    # ----------------------------
    # JWT Authentication
    # ----------------------------
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('dashboard/admin/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    path('dashboard/learner/', LearnerDashboardAPIView.as_view(), name='learner-dashboard'),

    # ----------------------------
    # Position CRUD (Admin only)
    # ----------------------------
    path('positions/', PositionAPIView.as_view(), name='position-list-create'),
    path('positions/<int:pk>/', PositionAPIView.as_view(), name='position-detail'),

    # ----------------------------
    # ShipType CRUD (Admin only)
    # ----------------------------
    path('ship-types/', ShipTypeAPIView.as_view(), name='shiptype-list-create'),
    path('ship-types/<int:pk>/', ShipTypeAPIView.as_view(), name='shiptype-detail'),

    # ----------------------------
    # User CRUD (Admin only)
    # ----------------------------
    path('users/', UserAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserAPIView.as_view(), name='user-detail'),

    # ----------------------------
    # Employee Profile
    # ----------------------------
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
]
