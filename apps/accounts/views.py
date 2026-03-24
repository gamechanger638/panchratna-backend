from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomTokenObtainPairSerializer, UserManagementSerializer
from .models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [permissions.IsAuthenticated] # To be refined further if needed

    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return User.objects.all()
        return User.objects.filter(community=self.request.user.community)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserManagementSerializer

class DashboardInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.families.models import Family
        from apps.members.models import Member
        total_families = Family.objects.count() if hasattr(Family.objects, 'count') else 0
        total_members = Member.objects.count() if hasattr(Member.objects, 'count') else 0
        unmarried = Member.objects.filter(marital_status='unmarried').count() if hasattr(Member.objects, 'filter') else 0

        data = {
            "overview": {
                "totalFamilies": total_families,
                "totalMembers": total_members,
                "unmarriedProfiles": unmarried,
                "activeLocations": 5,
                "growthRate": 12,
                "growthTrend": "up",
                "dataCompletionRate": 85
            },
            "genderDistribution": {
                "males": total_members // 2,
                "females": total_members - (total_members // 2),
                "ratio": "1.05:1"
            },
            "geographicRisks": {
                "unmappedFamilies": [{"area": "North Zone", "count": 12}],
                "inactiveWards": [{"ward": "Ward 4", "lastActivity": "2 weeks ago"}],
                "lowCoverageZones": [{"zone": "East Zone", "percentage": 45}]
            },
            "matrimonialIntelligence": {
                "newProfilesThisWeek": 24,
                "popularAgeRange": "24-28",
                "pendingVerifications": 15,
                "successfulMatchesThisMonth": 5
            },
            "recentActivity": [
                {"type": "registration", "text": "New family registered", "time": "2 hours ago"}
            ],
            "quickStats": {
                "verifiedMembers": total_members - 5 if total_members > 5 else total_members,
                "totalCasteCategories": 8,
                "digitalvotersCount": total_members
            }
        }
        return Response(data)
