from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, UserManagementViewSet, RegisterView, DashboardInsightsView, ExportReportView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('dashboard/insights/', DashboardInsightsView.as_view(), name='dashboard_insights'),
    path('dashboard/export/', ExportReportView.as_view(), name='dashboard_export'),
    path('', include(router.urls)),
]
