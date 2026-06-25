from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Service, ServicePriceMatrix, AppointmentSlot, Booking, BookingLog, VehicleCategoryMaster, BookingStatusMaster

User = get_user_model()

# ==========================================
# 1. IDENTITY & PRIVILEGE SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source='role.code', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'role_code', 'role_name', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        # Relies on CustomUserManager to bind the default 'USER' role object
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# ==========================================
# 2. MASTER TABLE DEFINITION SERIALIZERS
# ==========================================

class VehicleCategoryMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCategoryMaster
        fields = '__all__'


class BookingStatusMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatusMaster
        fields = '__all__'

# ==========================================
# 3. WORKSHOP TREATMENT MATRIX SERIALIZERS
# ==========================================

class ServicePriceMatrixSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = ServicePriceMatrix
        fields = ('category_code', 'category_name', 'price_in_rupees')


class ServiceSerializer(serializers.ModelSerializer):
    # Overridden to accept custom nested matrix writes from the custom admin form dashboard
    prices = ServicePriceMatrixSerializer(many=True, required=False)

    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'estimated_duration_hours', 'prices')

    def create(self, validated_data):
        # Pop standard request data out
        prices_data = self.context['request'].data.get('prices', [])
        service = Service.objects.create(**validated_data)
        
        # Iteratively write pricing matrix parameters for each vehicle class category
        for price_item in prices_data:
            category_instance = VehicleCategoryMaster.objects.get(code=price_item['category'])
            ServicePriceMatrix.objects.create(
                service=service,
                category=category_instance,
                price_in_rupees=price_item['price_in_rupees']
            )
        return service


class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = '__all__'

# ==========================================
# 4. INTAKE TRACKING & AUDIT LOG SERIALIZERS
# ==========================================

class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    vehicle_category_name = serializers.CharField(source='vehicle_category.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    status_ui_color = serializers.CharField(source='status.ui_color_class', read_only=True)
    
    # Nested inline appointment properties exposed upon office confirmation
    slot_date = serializers.CharField(source='slot.date', read_only=True)
    slot_start_time = serializers.CharField(source='slot.start_time', read_only=True)
    slot_end_time = serializers.CharField(source='slot.end_time', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'status', 'slot', 'estimated_delivery_timeline', 'final_price')


class BookingLogSerializer(serializers.ModelSerializer):
    """Serializes core audit trail metrics direct to custom admin workspace logs view"""
    class Meta:
        model = BookingLog
        fields = '__all__'