from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomTokenObtainPairSerializer, UserManagementSerializer
from .models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.families.models import Family
from apps.members.models import Member
import pandas as pd
from django.http import HttpResponse
import io

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
        user = request.user
        
        # Base Querysets
        families = Family.objects.filter(is_deleted=False)
        members = Member.objects.filter(is_deleted=False)
        
        # Role-based restriction sync with list views
        if user.role != 'super_admin':
            if user.community:
                families = families.filter(community=user.community)
                members = members.filter(family__community=user.community)
            
            if user.location:
                loc_type = user.location.type
                valid_fields = ['state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward']
                if loc_type in valid_fields:
                    families = families.filter(**{loc_type: user.location})
                    members = members.filter(**{f"family__{loc_type}": user.location})
        
        # Apply filters from query params
        state_id = request.query_params.get('state')
        district_id = request.query_params.get('district')
        ward_id = request.query_params.get('ward')
        profession = request.query_params.get('profession')
        education = request.query_params.get('education')
        gender = request.query_params.get('gender')
        status = request.query_params.get('status') # active/inactive
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if state_id: families = families.filter(state_id=state_id)
        if district_id: families = families.filter(district_id=district_id)
        if ward_id: families = families.filter(ward_id=ward_id)
        
        # Members filter based on families if family-level filters applied
        if any([state_id, district_id, ward_id]):
            members = members.filter(family__in=families)

        if profession: members = members.filter(profession=profession)
        if education: members = members.filter(education=education)
        if gender: members = members.filter(gender=gender)
        if status:
            is_active = status.lower() == 'active'
            members = members.filter(is_active=is_active)
            families = families.filter(is_active=is_active)

        if date_from:
            families = families.filter(created_at__gte=date_from)
            members = members.filter(created_at__gte=date_from)
        if date_to:
            families = families.filter(created_at__lte=date_to)
            members = members.filter(created_at__lte=date_to)

        # 1. KPI Metrics
        total_families = families.count()
        total_members = members.count()
        active_members = members.filter(is_active=True).count()
        inactive_members = total_members - active_members
        
        # Growth Today, 7 days, 30 days
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        new_today = members.filter(created_at__gte=today_start).count()
        new_week = members.filter(created_at__gte=week_ago).count()
        new_month = members.filter(created_at__gte=month_ago).count()

        # 2. Charts Data
        # Profession Distribution
        prof_dist = members.values('profession').annotate(count=Count('id')).order_by('-count')[:8]
        
        # Gender Distribution
        gender_dist = members.values('gender').annotate(count=Count('id'))
        
        # Growth Chart (Last 30 days)
        growth_chart = []
        for i in range(30, -1, -1):
            date = (now - timedelta(days=i)).date()
            count = members.filter(created_at__date=date).count()
            growth_chart.append({"date": date.strftime('%Y-%m-%d'), "count": count})
            
        # Location-wise (Focus on Wards if too many, or Districts)
        loc_dist = families.values('district__name').annotate(count=Count('id')).order_by('-count')[:10]

        data = {
            "metrics": {
                "totalFamilies": total_families,
                "totalMembers": total_members,
                "activeMembers": active_members,
                "inactiveMembers": inactive_members,
                "newRegistrations": {
                    "today": new_today,
                    "last7Days": new_week,
                    "monthly": new_month
                }
            },
            "charts": {
                "professionDistribution": list(prof_dist),
                "genderDistribution": list(gender_dist),
                "growthTrend": growth_chart,
                "locationDistribution": list(loc_dist)
            },
            "insights": {
                "topProfession": prof_dist[0]['profession'] if prof_dist else "None",
                "mostActiveArea": loc_dist[0]['district__name'] if loc_dist else "None",
            }
        }
        return Response(data)

class ExportReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        type = request.query_params.get('type', 'member') # member or family
        format = request.query_params.get('format', 'excel') # excel or csv
        
        # Base Querysets
        if type == 'family':
            qs = Family.objects.filter(is_deleted=False)
        else:
            qs = Member.objects.filter(is_deleted=False)

        # Apply same role restrictions as Dashboard
        user = request.user
        if user.role != 'super_admin':
            if user.community:
                qs = qs.filter(community=user.community) if type == 'family' else qs.filter(family__community=user.community)
            
            if user.location:
                loc_type = user.location.type
                hier_fields = ['state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward']
                if loc_type in hier_fields:
                    qs = qs.filter(**{loc_type: user.location}) if type == 'family' else qs.filter(**{f"family__{loc_type}": user.location})

        # Apply filters from query params
        f_state = request.query_params.get('state')
        f_sambhag = request.query_params.get('sambhag')
        f_district = request.query_params.get('district')
        f_vidhansabha = request.query_params.get('vidhansabha')
        f_ward = request.query_params.get('ward')
        f_community = request.query_params.get('community')
        f_profession = request.query_params.get('profession')
        f_status = request.query_params.get('status')

        if type == 'family':
            if f_state: qs = qs.filter(state_id=f_state)
            if f_sambhag: qs = qs.filter(sambhag_id=f_sambhag)
            if f_district: qs = qs.filter(district_id=f_district)
            if f_vidhansabha: qs = qs.filter(vidhansabha_id=f_vidhansabha)
            if f_ward: qs = qs.filter(ward_id=f_ward)
            if f_community: qs = qs.filter(community_id=f_community)
        else:
            if f_state: qs = qs.filter(family__state_id=f_state)
            if f_sambhag: qs = qs.filter(family__sambhag_id=f_sambhag)
            if f_district: qs = qs.filter(family__district_id=f_district)
            if f_vidhansabha: qs = qs.filter(family__vidhansabha_id=f_vidhansabha)
            if f_ward: qs = qs.filter(family__ward_id=f_ward)
            if f_community: qs = qs.filter(family__community_id=f_community)
            if f_profession: qs = qs.filter(profession=f_profession)
        
        if f_status:
            qs = qs.filter(is_active=(f_status.lower() == 'active'))

        # Convert to DataFrame
        if type == 'family':
            data = qs.values('family_code', 'name', 'father_or_husband_name', 'mobile', 'gotra', 'pincode', 'state__name', 'district__name', 'ward__name', 'created_at')
        else:
            data = qs.values('name', 'relation', 'gender', 'dob', 'mobile', 'education', 'profession', 'family__family_code', 'is_active', 'created_at')

        df = pd.DataFrame(list(data))
        
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{type}_report.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Report')
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{type}_report.xlsx"'
            return response
