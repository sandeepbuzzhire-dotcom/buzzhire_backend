from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminEmployeeViewSet, MyProfileViewSet, PunchInView, PunchOutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

# Admin employee management
router.register(r'api/admin/employees', AdminEmployeeViewSet, basename='admin-employees')

# Employee self profile (single-object viewset)
my_profile = MyProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    # JWT Auth
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ViewSets
    path('', include(router.urls)),

    # Self-profile endpoints
    path('api/employee/profile/', my_profile, name='my_profile'),
    
    # Attendence
    path("api/attendance/punch-in/", PunchInView.as_view(), name="punch-in"),
    path("api/attendance/punch-out/", PunchOutView.as_view(), name="punch-out"),
]
