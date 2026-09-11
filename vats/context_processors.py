"""
Context processors for HelpDesk Pro.

The notification bell lives in base.html, which every page extends, so the
data has to reach every template. Doing that through a context processor
avoids having to add the same three lines to every view in the project.
"""
from .models import Notification


def notifications(request):
    """Unread count + the most recent items, for the topbar bell."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    qs = Notification.objects.filter(recipient=request.user).select_related("ticket", "actor")

    return {
        "notif_unread_count": qs.filter(is_read=False).count(),
        # Capped deliberately — the dropdown is a glance, not an archive.
        "notif_recent": qs[:8],
    }
