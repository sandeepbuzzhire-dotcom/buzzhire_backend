from rest_framework import serializers
from .models import User, EmployeeProfile, Attendance
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmployeeProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'email', 'phone', 'address']


class AdminCreateEmployeeSerializer(serializers.ModelSerializer):
    # used by admin to create employee
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UserModel
        fields = ['id', 'email', 'password', 'role']

    def create(self, validated_data):
        # force role to EMPLOYEE for created accounts (admin route)
        validated_data['role'] = 'EMPLOYEE'
        password = validated_data.pop('password')
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        # EmployeeProfile will be auto-created by signal
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    profile = EmployeeProfileSerializer(read_only=True)

    class Meta:
        model = UserModel
        fields = ['id', 'email', 'role', 'profile']
        read_only_fields = ['role', 'email']



class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"