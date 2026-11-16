"""
Turning an email sent to the support mailbox into a ticket.

One message goes one of four ways:
  note      a reply about an existing ticket (its number is in the subject)
            from someone on that ticket: added to the ticket as a work note
  ticket    from a known user in an allowed domain: a new Pending ticket
  held      from anyone else: kept for an Admin to accept or dismiss
  skipped   an automatic message, a duplicate, or our own outgoing mail

The mailbox reader (management command fetch_mail) only fetches; all the
decisions are here so they can be tested without a mail server.
"""
import email
import re
from email import policy
from email.utils import parseaddr

from django.conf import settings

from registration.models import User
from .mailer import send_ticket_mail
from .models import Category, Detail, InboundEmail, Subcategory, Ticket, Worknote, notify

TICKET_NUMBER = re.compile(r'\bTKT\d{6,}\b', re.IGNORECASE)
REPLY_PREFIX = re.compile(r'^\s*((re|fw|fwd)\s*:\s*)+', re.IGNORECASE)
# Where a quoted earlier message usually starts in a reply.
QUOTE_START = re.compile(r'^\s*(On .+ wrote:|-----Original Message-----|From: .+)\s*$', re.MULTILINE)


def _body_text(message):
    part = message.get_body(preferencelist=('plain', 'html'))
    if part is None:
        return ''
    text = part.get_content()
    if part.get_content_type() == 'text/html':
        text = re.sub(r'<(br|/p|/div)[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def _without_quote(text):
    """A reply's own words, without the earlier message quoted under it."""
    match = QUOTE_START.search(text)
    if match:
        text = text[:match.start()]
    lines = [line for line in text.splitlines() if not line.lstrip().startswith('>')]
    return '\n'.join(lines).strip()


def guess_category(text):
    """
    Read the category off the email's own words: the most specific level that
    is named wins (a detail implies its subcategory and category). Returns
    (category, subcategory, detail), any of which may be None. Nothing named
    means nothing guessed; the Admin sets it at triage.
    """
    lowered = text.lower()

    def named(name):
        return re.search(r'(?<![a-z0-9])' + re.escape(name.lower()) + r'(?![a-z0-9])', lowered)

    for detail in sorted(Detail.objects.select_related('subcategory__category'), key=lambda d: -len(d.name)):
        if named(detail.name) and named(detail.subcategory.name):
            return detail.subcategory.category, detail.subcategory, detail
    for sub in sorted(Subcategory.objects.select_related('category'), key=lambda s: -len(s.name)):
        if named(sub.name):
            return sub.category, sub, None
    for category in sorted(Category.objects.all(), key=lambda c: -len(c.name)):
        if named(category.name):
            return category, None, None
    return None, None, None


def _domain_allowed(address):
    allowed = getattr(settings, 'SUPPORT_ALLOWED_DOMAINS', [])
    return not allowed or address.rsplit('@', 1)[-1].lower() in allowed


def create_ticket_from_email(user, subject, body):
    """Shared by direct intake and by an Admin accepting a held email."""
    title = REPLY_PREFIX.sub('', subject).strip() or '(no subject)'
    category, subcategory, detail = guess_category(f"{title}\n{body}")
    ticket = Ticket.objects.create(
        title=title[:150], problem_descp=body or title, created_by=user, status='Pending',
        category=category, subcategory=subcategory, detail=detail, source='Email',
    )
    Worknote.objects.create(ticket=ticket, type='Create', comment='', commented_by=user)
    for admin in User.objects.filter(role='Admin', is_active=True):
        notify(admin, f"{user.get_full_name()} emailed in {ticket.number} — awaiting triage",
               kind='Assigned', ticket=ticket, actor=user)
    send_ticket_mail(ticket, [user], 'New Ticket Generated',
                     'We received your email and created a ticket. An admin will review it and assign it.')
    return ticket


def process_message(raw):
    """Handle one raw email (bytes). Returns (outcome, object_or_None)."""
    message = email.message_from_bytes(raw, policy=policy.default)
    sender_name, sender = parseaddr(str(message.get('From', '')))
    sender = sender.lower()
    subject = str(message.get('Subject', '')).strip()
    message_id = str(message.get('Message-ID', '')).strip() or f"{sender}:{subject}:{message.get('Date', '')}"

    own = {a.lower() for a in (settings.EMAIL_HOST_USER, getattr(settings, 'SUPPORT_IMAP_USER', '')) if a}
    automatic = str(message.get('Auto-Submitted', 'no')).lower() != 'no' or message.get('X-Autoreply')
    if not sender or sender in own or automatic:
        return 'skipped', None
    if InboundEmail.objects.filter(message_id=message_id[:255]).exists():
        return 'skipped', None

    body = _body_text(message)
    user = User.objects.filter(email__iexact=sender, is_active=True).first()

    # A reply about an existing ticket, from someone who is on it
    found = TICKET_NUMBER.search(subject)
    if found and user:
        ticket = Ticket.objects.filter(number__iexact=found.group(0)).first()
        if ticket and (user in (ticket.created_by, ticket.assigned_to) or user.role == 'Admin'):
            words = _without_quote(body)
            if words:
                Worknote.objects.create(ticket=ticket, type='Comment', comment=words, commented_by=user)
                for person in (ticket.created_by, ticket.assigned_to):
                    notify(person, f"{user.get_full_name()} replied by email on {ticket.number}",
                           kind='Comment', ticket=ticket, actor=user)
            InboundEmail.objects.create(message_id=message_id[:255], sender=sender, sender_name=sender_name[:100],
                                        subject=subject[:255], body=body, status='Accepted', ticket=ticket,
                                        reason='Reply added to ticket')
            return 'note', ticket

    if user and _domain_allowed(sender):
        ticket = create_ticket_from_email(user, subject, body)
        InboundEmail.objects.create(message_id=message_id[:255], sender=sender, sender_name=sender_name[:100],
                                    subject=subject[:255], body=body, status='Accepted', ticket=ticket)
        return 'ticket', ticket

    reason = 'Sender is outside the company domain' if not _domain_allowed(sender) else 'Sender has no account'
    held = InboundEmail.objects.create(message_id=message_id[:255], sender=sender, sender_name=sender_name[:100],
                                       subject=subject[:255], body=body, reason=reason)
    for admin in User.objects.filter(role='Admin', is_active=True):
        notify(admin, f"Email from {sender} is waiting for review", kind='Assigned')
    return 'held', held
