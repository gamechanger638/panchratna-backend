from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')), # This now includes auth AND user management
    path('api/', include('apps.locations.urls')),
    path('api/', include('apps.families.urls')),
    path('api/', include('apps.members.urls')),
    path('api/matrimonial/', include('apps.matrimonial.urls')),
    path('api/community/', include('apps.community.urls')),
]
