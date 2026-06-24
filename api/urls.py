# api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, AdminCreateOfficeUserView, AdminListClientUsersView

urlpatterns = [
    # Auth Endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Admin Endpoints
    path('admin/create-office/', AdminCreateOfficeUserView.as_view(), name='create-office'),
    path('admin/clients/', AdminListClientUsersView.as_view(), name='admin-clients'),
]