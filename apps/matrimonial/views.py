from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from .models import MarriageProfile
from .serializers import MarriageProfileSerializer
from rest_framework.permissions import IsAuthenticated

class MarriageProfileViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = MarriageProfile.objects.all()
    serializer_class = MarriageProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'education', 'profession']

    def get_queryset(self):
        # Additional complex filtering e.g. age can be handled by custom FilterSet if needed
        # For now, relying on standard fields
        return super().get_queryset()
