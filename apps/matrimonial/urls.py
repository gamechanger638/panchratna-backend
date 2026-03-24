from django.urls import path
from .views import MarriageProfileViewSet

urlpatterns = [
    path('create', MarriageProfileViewSet.as_view({'post': 'create'}), name='matrimonial-create'),
    path('list', MarriageProfileViewSet.as_view({'get': 'list'}), name='matrimonial-list'),
    path('<uuid:pk>', MarriageProfileViewSet.as_view({'get': 'retrieve'}), name='matrimonial-detail'),
]
