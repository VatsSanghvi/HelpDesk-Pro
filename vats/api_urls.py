"""
vats/api_urls.py  —  HelpDesk Pro v2
All API URL patterns. Included in tickit/urls.py at /api/v1/.

UPDATED: added the Power BI feed endpoint at the bottom.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api_views import (
    CategoryViewSet,
    CurrentUserView,
    DashboardAnalyticsView,
    ManagerListView,
    ReportAnalyticsView,
    TicketViewSet,
)
from .powerbi_views import powerbi_tickets_feed

router = DefaultRouter()
router.register(r'tickets',    TicketViewSet,   basename='ticket')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),

    # Analytics
    path('analytics/dashboard/', DashboardAnalyticsView.as_view(), name='analytics-dashboard'),
    path('analytics/report/',    ReportAnalyticsView.as_view(),    name='analytics-report'),

    # User helpers
    path('users/managers/', ManagerListView.as_view(),   name='user-managers'),
    path('users/me/',       CurrentUserView.as_view(),   name='user-me'),

    # ── Power BI feed (new) ────────────────────────────────────────
    path('powerbi/tickets/', powerbi_tickets_feed, name='powerbi-tickets-feed'),
]
