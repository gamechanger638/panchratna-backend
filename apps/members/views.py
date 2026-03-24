from rest_framework import viewsets
from .models import Member
from .serializers import MemberSerializer
from rest_framework.permissions import IsAuthenticated

class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['family_id']

    def get_queryset(self):
        user = self.request.user
        queryset = Member.objects.filter(family__is_deleted=False)
        
        if user.role != 'super_admin' and user.community:
            queryset = queryset.filter(family__community=user.community)
            
        if user.role == 'super_admin':
            return queryset
        elif user.role == 'state_admin':
            return queryset.filter(family__state=user.location)
        elif user.role == 'district_admin':
            return queryset.filter(family__district=user.location)
        elif user.role == 'vidhansabha_admin':
            return queryset.filter(family__vidhansabha=user.location)
        elif user.role == 'ward_volunteer':
            return queryset.filter(family__ward=user.location)
            
        return queryset
