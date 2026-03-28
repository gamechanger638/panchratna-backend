from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Family
from .serializers import FamilySerializer, FamilyListSerializer
from .permissions import RoleBasedFamilyPermission
from rest_framework.response import Response

class FamilyViewSet(viewsets.ModelViewSet):
    permission_classes = [RoleBasedFamilyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward', 'community']
    search_fields = ['name', 'mobile', 'family_code']

    def get_serializer_class(self):
        if self.action == 'list':
            return FamilyListSerializer
        return FamilySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Family.objects.filter(is_deleted=False).prefetch_related('members')
        
        # Core restriction: All non-super_admins are restricted to their assigned community
        if user.role != 'super_admin' and user.community:
            queryset = queryset.filter(community=user.community)
            
        if user.role == 'super_admin':
            return queryset
            
        if not user.location:
            return queryset.none()
            
        location_type = user.location.type
        valid_family_fields = ['state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward']
        
        if location_type in valid_family_fields:
            filter_kwargs = {location_type: user.location}
            return queryset.filter(**filter_kwargs)
            
        return queryset.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
