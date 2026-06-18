"""
tickit/urls.py  —  HelpDesk Pro v2
Added: /api/v1/ block for the REST API.
Existing web view paths are completely unchanged.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Existing web views (UNCHANGED) ─────────────────────────────────────────
    path('', include('registration.urls')),
    path('', include('vats.urls')),

    # ── New REST API (v2 addition) ─────────────────────────────────────────────
    path('api/v1/', include('vats.api_urls')),

    # Browsable API login (useful for manual testing at /api-auth/login/)
    path('api-auth/', include('rest_framework.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
