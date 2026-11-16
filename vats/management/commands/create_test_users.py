"""
Create the five accounts used to test the whole workflow with real inboxes:
one Admin, three Managers and one Viewer.

    python manage.py create_test_users --password "ChooseOne#2026"

Use only addresses you have created yourself: the app sends real email to
them. Pass different ones with --admin, --managers (comma-separated) and
--viewer. Running it again updates the same accounts instead of adding more.
"""
from django.core.management.base import BaseCommand

from registration.models import User


class Command(BaseCommand):
    help = 'Create or update the Admin, three Manager and Viewer test accounts.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='Password for all five accounts.')
        parser.add_argument('--admin', default='yatinadmin@gmail.com')
        parser.add_argument('--managers', default='yatinmanager1@gmail.com,yatinmanager2@gmail.com,yatinmanager3@gmail.com')
        parser.add_argument('--viewer', default='yatinviewer@gmail.com')

    def handle(self, *args, **options):
        people = [(options['admin'], 'Admin', 'Yatin', 'Admin')]
        for number, address in enumerate([m.strip() for m in options['managers'].split(',') if m.strip()], start=1):
            people.append((address, 'Manager', 'Yatin', f'Manager {number}'))
        people.append((options['viewer'], 'Viewer', 'Yatin', 'Viewer'))

        for address, role, first, last in people:
            user = User.objects.filter(email__iexact=address).first()
            created = user is None
            if created:
                user = User.objects.create_user(first, last, address.lower(), options['password'])
            user.first_name, user.last_name, user.role, user.is_active = first, last, role, True
            user.set_password(options['password'])
            user.save()
            self.stdout.write(f"  {'created' if created else 'updated'}  {role:<8} {address}")
        self.stdout.write(self.style.SUCCESS('Done. Sign in with any of these addresses and the password you gave.'))
