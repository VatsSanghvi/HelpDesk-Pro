"""
Context processors for HelpDesk Pro.

The notification bell lives in base.html, which every page extends, so the
data has to reach every template. Doing that through a context processor
avoids having to add the same three lines to every view in the project.
"""
from .models import Notification, Ticket


def notifications(request):
    """Unread count and recent items for the bell, plus the navigation's open count."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    qs = Notification.objects.filter(recipient=request.user).select_related("ticket", "actor")

    # Open tickets in this person's own scope, for the count beside "Tickets"
    # in the navigation: all of them for an Admin, assigned for a Manager,
    # raised for a Viewer.
    open_tickets = Ticket.objects.filter(status__in=("Pending", "Assigned", "Scoping", "In Progress"))
    if request.user.role == "Manager":
        open_tickets = open_tickets.filter(assigned_to=request.user)
    elif request.user.role != "Admin":
        open_tickets = open_tickets.filter(created_by=request.user)

    return {
        "notif_unread_count": qs.filter(is_read=False).count(),
        # Capped deliberately — the dropdown is a glance, not an archive.
        "notif_recent": qs[:8],
        "nav_open_count": open_tickets.count(),
    }
