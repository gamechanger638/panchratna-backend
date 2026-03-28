from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')), # This now includes auth AND user management
    path('api/', include('apps.locations.urls')),
    path('api/', include('apps.families.urls')),
    path('api/', include('apps.members.urls')),
    path('api/matrimonial/', include('apps.matrimonial.urls')),
    path('api/community/', include('apps.community.urls')),
    path('api/', include('apps.payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

