from rest_framework import viewsets, permissions
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from .serializers import (
    AdminCreateEmployeeSerializer,
    EmployeeSerializer,
    EmployeeProfileSerializer
)
from .models import EmployeeProfile
from .permissions import IsAdmin, IsSelfOrAdmin

User = get_user_model()


# =====================================================
# ADMIN VIEWSET (List, Create, Retrieve, Update)
# =====================================================
class AdminEmployeeViewSet(viewsets.ModelViewSet):
    """
    Admin can:
    - list all employees
    - create an employee
    - retrieve an employee
    - update an employee
    """
    permission_classes = [IsAdmin]
    queryset = User.objects.filter(role="EMPLOYEE")

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateEmployeeSerializer
        return EmployeeSerializer


# =====================================================
# EMPLOYEE SELF PROFILE VIEWSET
# =====================================================
class MyProfileViewSet(viewsets.ViewSet):
    """
    Employee can:
    - view own profile
    - update own profile
    """
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_object(self):
        return EmployeeProfile.objects.get(user=self.request.user)

    def retrieve(self, request):
        profile = self.get_object()
        serializer = EmployeeProfileSerializer(profile)
        return Response(serializer.data)

    def update(self, request):
        profile = self.get_object()
        serializer = EmployeeProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
