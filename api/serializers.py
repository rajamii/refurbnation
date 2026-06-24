from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'date_joined')
        read_only_fields = ('id', 'role', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        # Default registration is for standard 'USER'
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Roles.USER
        )
        return user

class AdminCreateOfficeUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Roles.OFFICE
        )
        return user