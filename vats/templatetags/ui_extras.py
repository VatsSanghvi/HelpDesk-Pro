"""
Small presentation helpers for the templates.
"""
from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()

# Six tinted pairs, all readable against their own background.
AVATAR_BUCKETS = 6

# Triage rank shown inside the priority square. The number carries the rank
# independently of the colour, so it survives colour blindness and print.
PRIORITY_RANK = {"High": 1, "Moderate": 2, "Low": 3}

# The linear part of the lifecycle. Cancelled and Rejected are exits, not steps.
LIFECYCLE = ("Pending", "Assigned", "Scoping", "In Progress", "Completed")


@register.filter
def avatar_class(user):
    """
    Deterministic avatar colour for a user.

    Hashing the email means a given person is always the same colour, on every
    page and every session — which is what makes an avatar useful for scanning
    a column rather than just decorative. Using the email rather than the
    display name keeps the colour stable if someone is renamed.
    """
    if not user:
        return "av-0"
    key = (getattr(user, "email", "") or str(user)).lower()
    return f"av-{sum(key.encode()) % AVATAR_BUCKETS}"


@register.simple_tag
def icon(name, extra=""):
    """Inline reference to a symbol in the sprite (templates/partials/icons.html)."""
    classes = f"i {extra}".strip()
    return format_html(
        '<svg class="{}" aria-hidden="true" focusable="false"><use href="#i-{}"/></svg>',
        classes, name,
    )


@register.filter
def initials(user):
    if not user:
        return ""
    first = (getattr(user, "first_name", "") or "")[:1]
    last = (getattr(user, "last_name", "") or "")[:1]
    return (first + last).upper()


@register.filter
def display_name(user):
    """'Sarah Chen' from stored names of any casing."""
    if not user:
        return ""
    first = (getattr(user, "first_name", "") or "").strip()
    last = (getattr(user, "last_name", "") or "").strip()
    return " ".join(part[:1].upper() + part[1:] for part in (first, last) if part)


@register.filter
def priority_rank(priority):
    return PRIORITY_RANK.get(priority, "")


@register.filter
def slug_status(status):
    """'In Progress' -> 'in-progress', for class names."""
    return (status or "").lower().replace(" ", "-")


@register.simple_tag
def lifecycle(ticket):
    """
    The five lifecycle steps with a state each: done, current or todo.
    A Cancelled or Rejected ticket keeps the steps it reached before it left.
    """
    status = ticket.status
    if status in LIFECYCLE:
        at = LIFECYCLE.index(status)
    elif status == "Rejected":
        at = 0          # rejected at triage, never left Pending
    else:
        # Cancelled: it was at least Assigned if someone owned it.
        at = 1 if ticket.assigned_to_id else 0
    closed_early = status in ("Cancelled", "Rejected")
    steps = []
    for index, name in enumerate(LIFECYCLE):
        if status == "Completed" or index < at:
            state = "done"
        elif index == at:
            state = "stopped" if closed_early else "current"
        else:
            state = "todo"
        steps.append({"name": name, "state": state})
    return steps


@register.simple_tag
def sla_windows():
    """Hours allowed per priority, for explaining what a priority commits to."""
    hours = getattr(settings, "SLA_HOURS", {"High": 4, "Moderate": 24, "Low": 72})
    return [
        {"priority": name, "rank": PRIORITY_RANK[name], "hours": hours.get(name)}
        for name in ("High", "Moderate", "Low")
    ]


@register.simple_tag
def query_with(request, **changes):
    """Current query string with some keys replaced; empty values drop the key."""
    query = request.GET.copy()
    for key, value in changes.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else "?"


NAV_SECTIONS = {
    "dashboard": {"home"},
    "tickets": {
        "ticket_list", "ticket_list_status", "my_tickets", "ticket_detail",
        "ticket_create", "ticket_update", "ticket_approve",
    },
    "users": {"user_list", "user_list_role", "user_detail", "user_create", "user_update"},
    "categories": {"category_list", "category_create", "subcategory_list", "subcategory_create"},
}


@register.simple_tag
def nav_section(request):
    """Which top-level navigation item the current page belongs to."""
    match = getattr(request, "resolver_match", None)
    name = getattr(match, "url_name", "") or ""
    for section, names in NAV_SECTIONS.items():
        if name in names:
            return section
    return ""


@register.filter
def ago(moment):
    """Compact age: '35 min ago', '2 h ago', '3 days ago'. One unit, no more."""
    if not moment:
        return ""
    from django.utils import timezone
    seconds = max(0, (timezone.now() - moment).total_seconds())
    if seconds < 90:
        return "just now"
    minutes = seconds / 60
    if minutes < 60:
        return f"{round(minutes)}\u00a0min ago"
    hours = minutes / 60
    if hours < 24:
        return f"{round(hours)}\u00a0h ago"
    days = round(hours / 24)
    return "yesterday" if days == 1 else f"{days}\u00a0days ago"
