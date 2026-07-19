"""
vats/powerbi_views.py

A dedicated, flattened data endpoint built specifically for Power BI.

Why this exists separately from /api/v1/tickets/:
  - The main API uses session-based authentication (cookies), which Power BI's
    Web connector cannot use interactively when you click "Refresh."
  - Power BI needs a URL it can hit repeatedly with a simple, stable credential.
  - This endpoint uses a single secret key (from .env) passed as a query
    parameter instead — simple, and good enough for a portfolio/demo project.
  - It also flattens all foreign keys (category, assigned_to, etc.) into
    plain strings, since Power BI's JSON parser handles flat objects far
    more easily than nested ones.

Usage from Power BI:
  Get Data > Web > paste this URL:
  http://127.0.0.1:8000/api/v1/powerbi/tickets/?key=YOUR_SECRET_KEY

Security note: this is intended for local/demo use only. If you ever deploy
this publicly, treat POWERBI_API_KEY exactly like a password.
"""
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import Ticket


@csrf_exempt
@require_GET
def powerbi_tickets_feed(request):
    """
    GET /api/v1/powerbi/tickets/?key=<POWERBI_API_KEY>

    Returns ALL tickets (no role filtering — this is a reporting feed,
    not a user-facing endpoint) as a flat JSON array, ready for Power BI's
    Web connector to turn straight into a table.
    """
    provided_key = request.GET.get('key', '')
    expected_key = getattr(settings, 'POWERBI_API_KEY', '')

    if not expected_key or provided_key != expected_key:
        return JsonResponse({'error': 'Invalid or missing API key'}, status=403)

    tickets = Ticket.objects.select_related(
        'category', 'subcategory', 'created_by', 'assigned_to'
    ).all()

    data = []
    for t in tickets:
        data.append({
            'ticket_number':        t.number,
            'title':                t.title,
            'category':             t.category.name if t.category else None,
            'subcategory':          t.subcategory.name if t.subcategory else None,
            'priority':             t.priority,
            'status':               t.status,
            'created_by':           t.created_by.get_full_name() if t.created_by else None,
            'assigned_to':          t.assigned_to.get_full_name() if t.assigned_to else 'Unassigned',
            'assigned_to_role':     t.assigned_to.role if t.assigned_to else None,
            'created_at':           t.created_at.isoformat() if t.created_at else None,
            'updated_at':           t.updated_at.isoformat() if t.updated_at else None,
            'due_by':               t.due_by.isoformat() if t.due_by else None,
            'resolved_at':          t.resolved_at.isoformat() if t.resolved_at else None,
            'resolution_time_hours': t.resolution_time_hours,
            'age_hours':            t.age_hours,
            'is_sla_breached':      t.is_sla_breached,
            'is_open':              t.is_open(),
        })

    return JsonResponse(data, safe=False)
