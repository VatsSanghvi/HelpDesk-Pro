"""
Small presentation helpers for the templates.
"""
from django import template

register = template.Library()

# Eight tinted pairs, all readable against their own background.
AVATAR_BUCKETS = 8


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
