from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet, 
    AppointmentSlotViewSet, 
    BookingViewSet, 
    ConfigurationViewSet, 
    AdminDashboardViewSet,
    RegisterView,
    CustomTokenObtainPairView
)
from rest_framework_simplejwt.views import TokenRefreshView

# Initialize DRF Router Engine
router = DefaultRouter()

# 1. Main Operation Business Pipeline Endpoints
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'slots', AppointmentSlotViewSet, basename='slots')
router.register(r'bookings', BookingViewSet, basename='bookings')

# 2. Dynamic Configurations Master Lookup Endpoint
router.register(r'config', ConfigurationViewSet, basename='config')

# 3. Custom Admin Command Console Workspace Router Endpoint
router.register(r'admin', AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    # Router endpoints interface mapping
    path('', include(router.urls)),
    
    # Consolidated Token Security Gateway Core Mappings
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
]