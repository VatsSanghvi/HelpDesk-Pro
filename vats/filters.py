"""
vats/filters.py  —  HelpDesk Pro v2
FilterSet uses the ACTUAL field names and choice values from your models.
"""
import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    # Match the exact choice values from the model ("Pending", "High", etc.)
    STATUS_CHOICES = (
        ("Pending",     "Pending"),
        ("Assigned",    "Assigned"),
        ("Scoping",     "Scoping"),
        ("In Progress", "In Progress"),
        ("Completed",   "Completed"),
        ("Cancelled",   "Cancelled"),
        ("Rejected",    "Rejected"),
    )
    PRIORITY_CHOICES = (
        ("High",     "High"),
        ("Moderate", "Moderate"),
        ("Low",      "Low"),
    )

    status      = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    priority    = django_filters.ChoiceFilter(choices=PRIORITY_CHOICES)
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')
    created_by  = django_filters.NumberFilter(field_name='created_by__id')
    category    = django_filters.NumberFilter(field_name='category__id')
    subcategory = django_filters.NumberFilter(field_name='subcategory__id')

    created_after  = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    resolved_after  = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='gte')
    resolved_before = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='lte')

    sla_breached = django_filters.BooleanFilter(method='filter_sla_breached')

    def filter_sla_breached(self, queryset, name, value):
        from django.utils import timezone
        now = timezone.now()
        if value:
            return queryset.exclude(
                status__in=['Completed', 'Cancelled', 'Rejected']
            ).filter(due_by__lt=now)
        return queryset

    class Meta:
        model  = Ticket
        fields = ['status', 'priority', 'assigned_to', 'created_by', 'category', 'subcategory']
