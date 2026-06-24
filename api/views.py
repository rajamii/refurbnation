from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, AdminCreateOfficeUserSerializer
from .permissions import IsAdminUserRole

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role # Include role in JWT payload
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['email'] = self.user.email
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# --- ADMIN VIEWS ---

class AdminUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get_queryset(self):
        role_filter = self.request.query_params.get('role', None)
        if role_filter in ['USER', 'OFFICE']:
            return User.objects.filter(role=role_filter)
        return User.objects.exclude(role='ADMIN')

class AdminCreateOfficeUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUserRole]
    serializer_class = AdminCreateOfficeUserSerializer