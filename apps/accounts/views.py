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
        user = self.request.user
        if user.role == 'super_admin':
            return User.objects.all()
        
        queryset = User.objects.filter(community=user.community)
        
        if user.location:
            descendant_ids = user.location.get_all_descendant_ids(include_self=True)
            queryset = queryset.filter(location_id__in=descendant_ids)
            
        return queryset

    def perform_create(self, serializer):
        self.validate_access(serializer.validated_data)
        serializer.save()

    def perform_update(self, serializer):
        self.validate_access(serializer.validated_data)
        serializer.save()

    def validate_access(self, data):
        requester = self.request.user
        if requester.role == 'super_admin':
            return

        target_role = data.get('role')
        target_location = data.get('location')

        # Define role hierarchy
        role_priority = {
            'super_admin': 100,
            'state_admin': 80,
            'district_admin': 60,
            'zone_admin': 40,
            'vidhansabha_admin': 20,
            'ward_volunteer': 0
        }

        # 1. Check Role: Cannot create equal or higher role
        if role_priority.get(target_role, 0) >= role_priority.get(requester.role, 0):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You cannot create/update a user with a role equal to or higher than yours.")

        # 2. Check Geographic Scope: Must be within descendants
        if requester.location and target_location:
            descendant_ids = requester.location.get_all_descendant_ids(include_self=True)
            if target_location.id not in descendant_ids:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You cannot create/update a user outside your geographic jurisdiction.")

        # 3. Community must match
        if requester.community and data.get('community') != requester.community:
             from rest_framework.exceptions import PermissionDenied
             raise PermissionDenied("User must belong to the same community.")

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
