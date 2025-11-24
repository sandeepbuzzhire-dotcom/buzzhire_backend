from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from .utils import calculate_distance
from .constants import COMPANY_LAT, COMPANY_LON, PUNCH_RADIUS



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





# class PunchInView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user

#         # Read user location
#         user_lat = float(request.data.get("latitude"))
#         user_lon = float(request.data.get("longitude"))

#         # Calculate distance
#         distance = calculate_distance(user_lat, user_lon, COMPANY_LAT, COMPANY_LON)

#         if distance > PUNCH_RADIUS:
#             return Response({
#                 "status": "failed",
#                 "message": "You are out of range",
#                 "distance": round(distance, 2)
#             }, status=400)

#         # Create attendance entry
#         attendance = Attendance.objects.create(
#             user=user,
#             punch_in_time=timezone.now(),
#             punch_in_lat=user_lat,
#             punch_in_lon=user_lon
#         )

#         return Response({
#             "status": "success",
#             "message": "Punch in successful",
#             "distance": round(distance, 2),
#             "data": AttendanceSerializer(attendance).data
#         })
        




class PunchInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 0️⃣ Validate input
        if "latitude" not in request.data or "longitude" not in request.data:
            return Response(
                {"status": "failed", "message": "latitude & longitude are required"},
                status=400
            )

        user_lat = float(request.data.get("latitude"))
        user_lon = float(request.data.get("longitude"))

        # 1️⃣ Check if already punched in today (and not punched out)
        existing = Attendance.objects.filter(
            user=user,
            punch_out_time__isnull=True,
            punch_in_time__date=timezone.localdate()
        ).first()

        if existing:
            return Response({
                "status": "failed",
                "message": "You are already punched in today"
            }, status=400)

        # 2️⃣ Calculate distance
        distance = calculate_distance(user_lat, user_lon, COMPANY_LAT, COMPANY_LON)

        if distance > PUNCH_RADIUS:
            return Response({
                "status": "failed",
                "message": "You are out of range",
                "distance": round(distance, 2)
            }, status=400)

        # 3️⃣ Create attendance entry
        attendance = Attendance.objects.create(
            user=user,
            punch_in_time=timezone.now(),
            punch_in_lat=user_lat,
            punch_in_lon=user_lon
        )

        return Response({
            "status": "success",
            "message": "Punch in successful",
            "distance": round(distance, 2),
            "data": AttendanceSerializer(attendance).data
        }, status=201)





# class PunchOutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         user_lat = float(request.data.get("latitude"))
#         user_lon = float(request.data.get("longitude"))

#         # Get last punch-in record
#         try:
#             attendance = Attendance.objects.filter(user=user, punch_out_time__isnull=True).latest("punch_in_time")
#         except Attendance.DoesNotExist:
#             return Response({"message": "No active punch-in found"}, status=400)

#         # Update punch-out
#         attendance.punch_out_time = timezone.now()
#         attendance.punch_out_lat = user_lat
#         attendance.punch_out_lon = user_lon
#         attendance.save()

#         return Response({
#             "status": "success",
#             "message": "Punch out successful",
#             "data": AttendanceSerializer(attendance).data
#         })





class PunchOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if "latitude" not in request.data or "longitude" not in request.data:
            return Response(
                {"status": "failed", "message": "latitude & longitude are required"},
                status=400
            )

        user_lat = float(request.data.get("latitude"))
        user_lon = float(request.data.get("longitude"))

        # 1️⃣ Get active punch in
        attendance = Attendance.objects.filter(
            user=user,
            punch_out_time__isnull=True
        ).order_by("-punch_in_time").first()

        if not attendance:
            return Response({
                "status": "failed",
                "message": "You have not punched in"
            }, status=400)

        # 2️⃣ Update punch-out
        attendance.punch_out_time = timezone.now()
        attendance.punch_out_lat = user_lat
        attendance.punch_out_lon = user_lon
        attendance.save()

        return Response({
            "status": "success",
            "message": "Punch out successful",
            "data": AttendanceSerializer(attendance).data
        }, status=200)
