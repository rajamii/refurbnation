from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, AdminCreateOfficeUserSerializer, ServiceSerializer, AppointmentSlotSerializer, BookingSerializer, BookingLogSerializer
from .models import Service, AppointmentSlot, Booking, BookingLog
from rest_framework.response import Response
from .permissions import IsAdminUserRole, IsAdminOrOffice, IsAdminOfficeOrReadOnly

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


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    # Anyone authenticated can view, only Office/Admin can create/edit
    permission_classes = [permissions.IsAuthenticated, IsAdminOfficeOrReadOnly]

class AppointmentSlotViewSet(viewsets.ModelViewSet):
    queryset = AppointmentSlot.objects.filter(is_active=True)
    serializer_class = AppointmentSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOfficeOrReadOnly]

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Office and Admin see all bookings
        if user.role in ['ADMIN', 'OFFICE']:
            return Booking.objects.all().order_by('-created_at')
        # Standard users only see their own bookings
        return Booking.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically assign the logged-in user to the booking
        serializer.save(user=self.request.user)

    # Custom action for Office/Admin to update booking status
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrOffice])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Booking.BookingStatus.choices):
            booking.status = new_status
            booking.save()
            return Response({'status': 'Booking status updated'})
        return Response({'error': 'Invalid status'}, status=400)


class AdminAuditLogListView(generics.ListAPIView):
    queryset = BookingLog.objects.all()
    serializer_class = BookingLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]


class BookingViewSet(viewsets.ModelViewSet):
    # ... your existing properties ...

    def _log_action(self, booking, actor):
        BookingLog.objects.create(
            booking_id=booking.id,
            client_email=booking.user.email,
            service_name=booking.service.name,
            action_by=actor.email,
            status_changed_to=booking.status
        )

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        self._log_action(booking, self.request.user) # Logs initial creation by user

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrOffice])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')
        new_timeline = request.data.get('estimated_delivery_timeline')
        
        if new_status:
            booking.status = new_status
        if new_timeline:
            booking.estimated_delivery_timeline = new_timeline
            
        booking.save()
        self._log_action(booking, request.user) # Logs handling action taken by staff/admin
        return Response({'status': 'Booking updated'})