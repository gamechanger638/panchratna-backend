from rest_framework import viewsets
from .models import Location
from .serializers import LocationSerializer
from .permissions import IsSuperAdminOrReadOnly

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filterset_fields = ['type', 'parent', 'community']
