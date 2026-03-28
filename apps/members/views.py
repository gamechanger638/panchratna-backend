from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Member
from .serializers import MemberSerializer
from rest_framework.permissions import IsAuthenticated

class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'gender': ['exact'],
        'profession': ['icontains', 'exact'],
        'family__community': ['exact'],
        'family__state': ['exact'],
        'family__sambhag': ['exact'],
        'family__loksabha': ['exact'],
        'family__district': ['exact'],
        'family__vidhansabha': ['exact'],
        'family__ward': ['exact'],
    }
    search_fields = ['name', 'mobile', 'profession']

    def get_queryset(self):
        user = self.request.user
        queryset = Member.objects.filter(family__is_deleted=False)
        
        if user.role != 'super_admin' and user.community:
            queryset = queryset.filter(family__community=user.community)
            
        if user.role == 'super_admin':
            return queryset
            
        if not user.location:
            return queryset.none()
            
        location_type = user.location.type
        valid_family_fields = ['state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward']
        
        if location_type in valid_family_fields:
            filter_kwargs = {f"family__{location_type}": user.location}
            return queryset.filter(**filter_kwargs)
            
        return queryset.none()
