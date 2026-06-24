from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, RegisterView, 
    AdminUserListView, AdminCreateOfficeUserView
)

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/office/', AdminCreateOfficeUserView.as_view(), name='admin_create_office_user'),
]