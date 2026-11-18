"""
Read the support mailbox and turn new emails into tickets.

    python manage.py fetch_mail              # check once
    python manage.py fetch_mail --every 5    # keep checking every 5 seconds

Needs SUPPORT_IMAP_USER and SUPPORT_IMAP_PASSWORD in .env (for Gmail: turn on
IMAP and use a Google App Password). Each email is marked read once handled,
so it is processed only once.

With --every, one mailbox connection is kept open between checks instead of
logging in each time, so a short interval does not hammer the mail server.
If the connection drops it reconnects on the next check.
"""
import imaplib
import sys
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
        # A Windows console cannot print every character an email subject can
        # hold (emoji, for one). Never let printing a log line stop the run.
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(errors='replace')
            except (AttributeError, ValueError):
                pass

        every = max(options['every'], 0)
        box = None
        try:
            while True:
                try:
                    if box is None:
                        box = self.connect()
                    self.check_once(box)
                except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as error:
                    self.stderr.write(f'Mailbox check failed: {error}')
                    self.close(box)
                    box = None
                    if not every:
                        raise CommandError('Could not read the mailbox.') from error
                if not every:
                    return
                time.sleep(every)
        except KeyboardInterrupt:
            self.stdout.write('Stopped checking the mailbox.')
        finally:
            self.close(box)

    def connect(self):
        box = imaplib.IMAP4_SSL(settings.SUPPORT_IMAP_HOST)
        box.login(settings.SUPPORT_IMAP_USER, settings.SUPPORT_IMAP_PASSWORD)
        self.stdout.write(f'Connected to {settings.SUPPORT_IMAP_USER}.')
        return box

    @staticmethod
    def close(box):
        if box is None:
            return
        try:
            box.logout()
        except Exception:       # noqa: BLE001 - already closing
            pass

    def check_once(self, box):
        # Selecting again on every check refreshes the mailbox, so mail that
        # arrived since the last check is seen on a long-lived connection.
        box.select('INBOX')
        _, data = box.search(None, 'UNSEEN')
        ids = data[0].split()
        for message_id in ids:
            _, parts = box.fetch(message_id, '(RFC822)')
            outcome, thing = process_message(parts[0][1])
            box.store(message_id, '+FLAGS', '\\Seen')
            self.stdout.write(f'  {time.strftime("%H:%M:%S")} {outcome}: {thing or ""}')
        if ids:
            self.stdout.write(f'Checked mailbox: {len(ids)} new email(s).')
