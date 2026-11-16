"""
Read the support mailbox and turn new emails into tickets.

    python manage.py fetch_mail              # check once
    python manage.py fetch_mail --every 60   # keep checking every 60 seconds

Needs SUPPORT_IMAP_USER and SUPPORT_IMAP_PASSWORD in .env (for Gmail: turn on
IMAP and use a Google App Password). Each email is marked read once handled,
so it is processed only once.
"""
import imaplib
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from vats.inbound import process_message


class Command(BaseCommand):
    help = 'Fetch unread emails from the support mailbox and create tickets from them.'

    def add_arguments(self, parser):
        parser.add_argument('--every', type=int, default=0,
                            help='Keep running and check again every N seconds.')

    def handle(self, *args, **options):
        if not settings.SUPPORT_IMAP_USER or not settings.SUPPORT_IMAP_PASSWORD:
            raise CommandError('Set SUPPORT_IMAP_USER and SUPPORT_IMAP_PASSWORD in .env first.')
        while True:
            try:
                self.check_once()
            except (imaplib.IMAP4.error, OSError) as error:
                self.stderr.write(f'Mailbox check failed: {error}')
                if not options['every']:
                    raise CommandError('Could not read the mailbox.') from error
            if not options['every']:
                return
            time.sleep(options['every'])

    def check_once(self):
        box = imaplib.IMAP4_SSL(settings.SUPPORT_IMAP_HOST)
        try:
            box.login(settings.SUPPORT_IMAP_USER, settings.SUPPORT_IMAP_PASSWORD)
            box.select('INBOX')
            _, data = box.search(None, 'UNSEEN')
            ids = data[0].split()
            for message_id in ids:
                _, parts = box.fetch(message_id, '(RFC822)')
                outcome, thing = process_message(parts[0][1])
                box.store(message_id, '+FLAGS', '\\Seen')
                self.stdout.write(f'  {outcome}: {thing or ""}')
            self.stdout.write(f'Checked mailbox: {len(ids)} new email(s).')
        finally:
            try:
                box.logout()
            except Exception:       # noqa: BLE001 - already closing
                pass
