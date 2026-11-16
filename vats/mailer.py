"""
Every email the helpdesk sends about a ticket goes through here, so the
subject format, the content and the failure handling are the same everywhere.

The subject always carries the ticket number in square brackets. That is what
lets a reply to any of these emails find its way back to the ticket.
"""
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def ticket_subject(ticket, headline):
    return f"[{ticket.number}] {headline}"


def send_ticket_mail(ticket, recipients, headline, message):
    """
    Email `message` about `ticket` to each recipient (users or addresses).
    Never raises: a mail server problem must not stop the ticket action that
    triggered it. Returns the number of emails handed to the mail server.
    """
    addresses = []
    for recipient in recipients:
        address = getattr(recipient, 'email', recipient)
        if address and address not in addresses:
            addresses.append(address)
    if not addresses:
        return 0

    html = render_to_string('vats/email_ticket.html', {
        'ticket': ticket, 'headline': headline, 'message': message,
    })
    sent = 0
    for address in addresses:
        mail = EmailMessage(ticket_subject(ticket, headline), html, settings.EMAIL_HOST_USER or None, [address])
        mail.content_subtype = 'html'
        try:
            sent += mail.send()
        except Exception as error:      # noqa: BLE001 - see docstring
            print(f"Email to {address} about {ticket.number} failed: {error}")
    return sent
