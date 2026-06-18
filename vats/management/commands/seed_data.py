"""
vats/management/commands/seed_data.py

Populates the database with realistic Manulife IT Helpdesk data.

Run with:
    python manage.py seed_data

Creates:
  - 5 Categories with subcategories
  - 3 Manager users + 5 Viewer users (employees)
  - 30 tickets across all statuses and priorities
  - Worknotes and audit trail on each ticket
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from registration.models import User
from vats.models import Category, Subcategory, Ticket, Worknote


class Command(BaseCommand):
    help = 'Seeds the database with Manulife IT Helpdesk sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('\n🏢  Manulife IT HelpDesk — Seeding sample data...\n')

        self.create_categories()
        self.create_users()
        self.create_tickets()

        self.stdout.write(self.style.SUCCESS('\n✅  Done! Database seeded successfully.\n'))
        self.stdout.write('Login credentials:\n')
        self.stdout.write('  Admin   → admin@manulife.com       / Manulife@123\n')
        self.stdout.write('  Manager → sarah.chen@manulife.com  / Manulife@123\n')
        self.stdout.write('  Viewer  → james.wilson@manulife.com/ Manulife@123\n')

    # ── Categories ────────────────────────────────────────────────

    def create_categories(self):
        self.stdout.write('📁  Creating categories...')

        data = {
            'Hardware': [
                'Laptop & Desktop',
                'Printers & Scanners',
                'Mobile Devices',
                'Monitors & Peripherals',
                'Trading Terminals',
            ],
            'Software & Applications': [
                'Microsoft Office 365',
                'Bloomberg Terminal',
                'Salesforce CRM',
                'SAP Finance',
                'Internal Portals',
            ],
            'Network & Connectivity': [
                'VPN & Remote Access',
                'WiFi & LAN',
                'Email & Outlook',
                'Video Conferencing',
                'Internet Access',
            ],
            'Security & Access': [
                'Password Reset',
                'Account Lockout',
                'New User Provisioning',
                'MFA & Token Setup',
                'Data Access Permissions',
            ],
            'Data & Reporting': [
                'Power BI & Reports',
                'Excel & Macros',
                'Database Access',
                'Data Export Requests',
                'SharePoint & OneDrive',
            ],
        }

        self.categories = {}
        self.subcategories = {}

        for cat_name, subs in data.items():
            cat, created = Category.objects.get_or_create(name=cat_name)
            self.categories[cat_name] = cat
            self.subcategories[cat_name] = []
            for sub_name in subs:
                sub, _ = Subcategory.objects.get_or_create(category=cat, name=sub_name)
                self.subcategories[cat_name].append(sub)
            self.stdout.write(f'   ✓ {cat_name} ({len(subs)} subcategories)')

    # ── Users ─────────────────────────────────────────────────────

    def create_users(self):
        self.stdout.write('👥  Creating users...')

        managers_data = [
            {'email': 'sarah.chen@manulife.com',    'first_name': 'Sarah',   'last_name': 'Chen',     'phone_number': '4161234567'},
            {'email': 'michael.ross@manulife.com',  'first_name': 'Michael', 'last_name': 'Ross',     'phone_number': '4162345678'},
            {'email': 'priya.nair@manulife.com',    'first_name': 'Priya',   'last_name': 'Nair',     'phone_number': '4163456789'},
        ]

        viewers_data = [
            {'email': 'james.wilson@manulife.com',  'first_name': 'James',   'last_name': 'Wilson',   'phone_number': '4164567890'},
            {'email': 'emily.zhang@manulife.com',   'first_name': 'Emily',   'last_name': 'Zhang',    'phone_number': '4165678901'},
            {'email': 'robert.patel@manulife.com',  'first_name': 'Robert',  'last_name': 'Patel',    'phone_number': '4166789012'},
            {'email': 'jessica.kim@manulife.com',   'first_name': 'Jessica', 'last_name': 'Kim',      'phone_number': '4167890123'},
            {'email': 'david.nguyen@manulife.com',  'first_name': 'David',   'last_name': 'Nguyen',   'phone_number': '4168901234'},
        ]

        # Admin
        if not User.objects.filter(email='admin@manulife.com').exists():
            User.objects.create_superuser(
                email='admin@manulife.com',
                password='Manulife@123',
                first_name='Alex',
                last_name='Thompson',
            )
            # Set role to Admin
            u = User.objects.get(email='admin@manulife.com')
            u.role = 'Admin'
            u.save()
            self.stdout.write('   ✓ Admin: admin@manulife.com')

        self.managers = []
        for m in managers_data:
            if not User.objects.filter(email=m['email']).exists():
                u = User.objects.create_user(
                    email=m['email'],
                    password='Manulife@123',
                    first_name=m['first_name'],
                    last_name=m['last_name'],
                    phone_number=m['phone_number'],
                    role='Manager',
                )
            else:
                u = User.objects.get(email=m['email'])
            self.managers.append(u)
            self.stdout.write(f'   ✓ Manager: {m["email"]}')

        self.viewers = []
        for v in viewers_data:
            if not User.objects.filter(email=v['email']).exists():
                u = User.objects.create_user(
                    email=v['email'],
                    password='Manulife@123',
                    first_name=v['first_name'],
                    last_name=v['last_name'],
                    phone_number=v['phone_number'],
                    role='Viewer',
                )
            else:
                u = User.objects.get(email=v['email'])
            self.viewers.append(u)
            self.stdout.write(f'   ✓ Viewer:  {v["email"]}')

    # ── Tickets ───────────────────────────────────────────────────

    def create_tickets(self):
        self.stdout.write('🎫  Creating tickets...')

        admin = User.objects.get(email='admin@manulife.com')

        tickets_data = [

            # ── Hardware tickets ───────────────────────────────────
            {
                'cat': 'Hardware', 'sub': 'Laptop & Desktop',
                'title': 'Laptop not turning on after Windows update',
                'problem_descp': 'My Dell laptop (Asset #MNL-4821) stopped booting after the automatic Windows update last night. Screen stays black after pressing power button. I have a client presentation in 2 hours and urgently need this resolved.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 0, 'manager': 0,
                'notes': [
                    ('Field', 'Checked power adapter and battery — both functional. Likely update corruption.'),
                    ('Comment', 'Rolled back Windows update KB5034441. Laptop boots normally now. User confirmed resolution.'),
                ]
            },
            {
                'cat': 'Hardware', 'sub': 'Printers & Scanners',
                'title': 'Floor 12 shared printer showing offline',
                'problem_descp': 'The Canon printer on floor 12 (near the boardroom) is showing as offline on all workstations. Multiple employees are unable to print policy documents. This is affecting about 15 staff members.',
                'priority': 'Moderate', 'status': 'In Progress',
                'viewer': 1, 'manager': 1,
                'notes': [
                    ('Field', 'Restarted print spooler service — issue persisted. Checking network connectivity.'),
                    ('Comment', 'Found the printer IP had changed after network maintenance. Updating printer port on all affected workstations.'),
                ]
            },
            {
                'cat': 'Hardware', 'sub': 'Mobile Devices',
                'title': 'Company iPhone not receiving MFA codes',
                'problem_descp': 'My company-issued iPhone 14 (Asset #MNL-MB-0392) is not receiving SMS verification codes for MFA login. I cannot access my email or any internal systems. This started this morning.',
                'priority': 'High', 'status': 'Assigned',
                'viewer': 2, 'manager': 2,
                'notes': [
                    ('Field', 'Ticket assigned to Priya Nair for investigation.'),
                ]
            },
            {
                'cat': 'Hardware', 'sub': 'Monitors & Peripherals',
                'title': 'Second monitor not detected after desk move',
                'problem_descp': 'After moving to my new desk on floor 8, my second monitor is not being detected. I tried reconnecting the DisplayPort cable but it still shows as not connected. I need dual screens for my daily work.',
                'priority': 'Low', 'status': 'Completed',
                'viewer': 3, 'manager': 0,
                'notes': [
                    ('Comment', 'Replaced DisplayPort cable with a new one from IT stock. Second monitor now detected and configured.'),
                ]
            },
            {
                'cat': 'Hardware', 'sub': 'Trading Terminals',
                'title': 'Bloomberg Terminal freezing during market hours',
                'problem_descp': 'The Bloomberg Terminal on workstation INV-07 has been freezing every 20-30 minutes during peak trading hours between 9:30 AM and 11:00 AM. This is critically impacting our investment team\'s ability to execute trades.',
                'priority': 'High', 'status': 'In Progress',
                'viewer': 4, 'manager': 1,
                'notes': [
                    ('Field', 'Priority escalated to High due to trading impact.'),
                    ('Comment', 'Identified memory leak in Bloomberg version 3.75.1. Coordinating with Bloomberg support for emergency patch.'),
                ]
            },

            # ── Software tickets ───────────────────────────────────
            {
                'cat': 'Software & Applications', 'sub': 'Microsoft Office 365',
                'title': 'Outlook keeps crashing when opening attachments',
                'problem_descp': 'Microsoft Outlook crashes every time I try to open a PDF or Excel attachment in emails. I get a "Microsoft Outlook has stopped working" error. This has been happening since yesterday afternoon. I have tried restarting the computer.',
                'priority': 'Moderate', 'status': 'Completed',
                'viewer': 0, 'manager': 2,
                'notes': [
                    ('Comment', 'Ran Office repair tool. Issue was with a corrupted add-in. Disabled the Adobe PDF add-in and Outlook is now stable.'),
                ]
            },
            {
                'cat': 'Software & Applications', 'sub': 'Salesforce CRM',
                'title': 'Unable to generate Q4 client reports in Salesforce',
                'problem_descp': 'When trying to run the Q4 Client Portfolio report in Salesforce, I get an error: "Report timeout: query exceeded 10 minutes." The same report ran fine last quarter. I need this for the executive review meeting tomorrow at 9 AM.',
                'priority': 'High', 'status': 'Scoping',
                'viewer': 1, 'manager': 0,
                'notes': [
                    ('Field', 'Status moved to Scoping. Checking Salesforce report query performance.'),
                    ('Comment', 'Report query is hitting a data volume limit due to Q4 data growth. Working on optimizing the report filters.'),
                ]
            },
            {
                'cat': 'Software & Applications', 'sub': 'SAP Finance',
                'title': 'Cannot post journal entries in SAP — authorization error',
                'problem_descp': 'I am getting "Authorization object F_BKPF_BUK" error when trying to post journal entries in SAP for the December month-end close. This is blocking the entire month-end process for the finance team.',
                'priority': 'High', 'status': 'Assigned',
                'viewer': 2, 'manager': 1,
                'notes': [
                    ('Field', 'Assigned to Michael Ross. Month-end impact flagged.'),
                ]
            },
            {
                'cat': 'Software & Applications', 'sub': 'Internal Portals',
                'title': 'HR Self-Service portal not loading — white screen',
                'problem_descp': 'The Manulife HR Self-Service portal (hrss.manulife.internal) shows a blank white screen after login. I need to submit my timesheet by end of day today. This is happening on both Chrome and Edge browsers.',
                'priority': 'Moderate', 'status': 'Completed',
                'viewer': 3, 'manager': 2,
                'notes': [
                    ('Comment', 'Cleared browser cache and cookies. Portal loads correctly now. Issue was with cached session data from last week\'s maintenance window.'),
                ]
            },
            {
                'cat': 'Software & Applications', 'sub': 'Bloomberg Terminal',
                'title': 'Bloomberg license expired — cannot log in',
                'problem_descp': 'Receiving "License expired or invalid" message when logging into Bloomberg Terminal. Our whole fixed income desk is locked out. License renewal was supposed to be handled by procurement last month.',
                'priority': 'High', 'status': 'Pending',
                'viewer': 4, 'manager': None,
                'notes': []
            },

            # ── Network tickets ────────────────────────────────────
            {
                'cat': 'Network & Connectivity', 'sub': 'VPN & Remote Access',
                'title': 'Cisco AnyConnect VPN dropping connection every hour',
                'problem_descp': 'The Cisco AnyConnect VPN disconnects automatically approximately every 60 minutes while working from home. I have to manually reconnect which interrupts active work. This started after the VPN client was updated last Tuesday.',
                'priority': 'Moderate', 'status': 'In Progress',
                'viewer': 0, 'manager': 0,
                'notes': [
                    ('Comment', 'Identified session timeout setting was incorrectly configured during the update. Pushing corrected VPN profile to affected users.'),
                ]
            },
            {
                'cat': 'Network & Connectivity', 'sub': 'Email & Outlook',
                'title': 'Emails delayed by 2-3 hours — entire actuarial team affected',
                'problem_descp': 'The entire actuarial team on floor 6 is experiencing email delays of 2-3 hours. Time-sensitive client communications and trade confirmations are being delayed. This started around 8 AM today.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 1, 'manager': 1,
                'notes': [
                    ('Field', 'Escalated — affects 25+ users and client communications.'),
                    ('Comment', 'Found mail flow rule misconfiguration causing messages to queue. Corrected the rule and processed the queued messages. All delayed emails delivered.'),
                ]
            },
            {
                'cat': 'Network & Connectivity', 'sub': 'Video Conferencing',
                'title': 'Microsoft Teams camera not working in boardroom A',
                'problem_descp': 'The camera in Boardroom A (Floor 3) is not working in Microsoft Teams meetings. Remote participants cannot see the room. We have an important client video call in 45 minutes. The microphone and speakers are working fine.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 2, 'manager': 2,
                'notes': [
                    ('Comment', 'Camera driver was corrupted after Windows update. Reinstalled Logitech driver v9.8.2. Camera now works in Teams. Tested with a call — confirmed resolution.'),
                ]
            },
            {
                'cat': 'Network & Connectivity', 'sub': 'WiFi & LAN',
                'title': 'WiFi very slow on floor 9 — connectivity issues',
                'problem_descp': 'WiFi speeds on floor 9 have been very slow for the past 3 days. Pages take 30-40 seconds to load and video calls keep dropping. Speed test shows only 2 Mbps when it should be 100 Mbps. Affects all 20 people on this floor.',
                'priority': 'Moderate', 'status': 'Scoping',
                'viewer': 3, 'manager': 0,
                'notes': [
                    ('Field', 'Wireless site survey scheduled for Thursday.'),
                    ('Comment', 'Preliminary check shows one of the two access points on Floor 9 is malfunctioning. Ordering replacement unit.'),
                ]
            },
            {
                'cat': 'Network & Connectivity', 'sub': 'Internet Access',
                'title': 'Unable to access client portal — firewall blocking',
                'problem_descp': 'I cannot access the client portal at https://advisor.clientportal.ca. The page shows "Access Denied — Blocked by firewall policy." I need this for daily client account management. Other advisors can access it fine.',
                'priority': 'Low', 'status': 'Pending',
                'viewer': 4, 'manager': None,
                'notes': []
            },

            # ── Security tickets ───────────────────────────────────
            {
                'cat': 'Security & Access', 'sub': 'Account Lockout',
                'title': 'Account locked out — cannot access any systems',
                'problem_descp': 'My Active Directory account has been locked out. I cannot log into my computer, email, or any Manulife systems. I believe this happened because I entered my password incorrectly too many times after the forced password change yesterday.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 0, 'manager': 2,
                'notes': [
                    ('Comment', 'Account unlocked in Active Directory. User identity verified via employee ID and manager confirmation. User advised to update saved passwords in browser.'),
                ]
            },
            {
                'cat': 'Security & Access', 'sub': 'New User Provisioning',
                'title': 'New hire Aisha Malik needs system access by Monday',
                'problem_descp': 'We have a new analyst joining our Investment Analytics team on Monday, January 15. Employee ID: MNL-2024-0891. She needs access to: Active Directory, Outlook, Bloomberg Terminal, SharePoint (Investment Analytics site), Power BI, and the shared L: drive.',
                'priority': 'Moderate', 'status': 'In Progress',
                'viewer': 1, 'manager': 0,
                'notes': [
                    ('Field', 'AD account created. Email provisioned.'),
                    ('Comment', 'Bloomberg license requested from procurement. SharePoint and Power BI access granted. L: drive mapping configured. Pending Bloomberg activation.'),
                ]
            },
            {
                'cat': 'Security & Access', 'sub': 'MFA & Token Setup',
                'title': 'MFA authenticator app lost — phone replaced',
                'problem_descp': 'I got a new phone and I no longer have access to my Microsoft Authenticator app with my Manulife account set up. I cannot log in to any systems that require MFA. I have my employee ID MNL-1847 and can verify my identity.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 2, 'manager': 1,
                'notes': [
                    ('Comment', 'Identity verified with employee ID and HR confirmation. Temporary access bypass granted for 24 hours. User set up new Authenticator app on replacement iPhone. MFA working correctly.'),
                ]
            },
            {
                'cat': 'Security & Access', 'sub': 'Data Access Permissions',
                'title': 'Need read access to Actuarial pricing models folder',
                'problem_descp': 'As part of my new project assignment on the Pricing Optimization team, I need read-only access to the Actuarial pricing models on SharePoint (site: sp.manulife.internal/actuarial/pricing). My manager David Park has approved this request.',
                'priority': 'Low', 'status': 'Assigned',
                'viewer': 3, 'manager': 2,
                'notes': [
                    ('Field', 'Manager approval confirmed via email. Requesting SharePoint admin to grant access.'),
                ]
            },
            {
                'cat': 'Security & Access', 'sub': 'Password Reset',
                'title': 'Forgot password — locked out of email and VPN',
                'problem_descp': 'I have forgotten my Windows password after being on vacation for 3 weeks. I am locked out of my laptop, email, and VPN. I am working from home today and need to join a critical call at 2 PM EST.',
                'priority': 'Moderate', 'status': 'Completed',
                'viewer': 4, 'manager': 0,
                'notes': [
                    ('Comment', 'Identity verified via security questions and employee badge number. Temporary password issued via personal email. User successfully logged in and changed password. VPN access confirmed working.'),
                ]
            },

            # ── Data & Reporting tickets ───────────────────────────
            {
                'cat': 'Data & Reporting', 'sub': 'Power BI & Reports',
                'title': 'Power BI dashboard not refreshing — stale data',
                'problem_descp': 'The "Manulife Sales Performance Dashboard" in Power BI has not refreshed since yesterday at 6 PM. It should refresh every 4 hours automatically. The sales leadership team uses this daily for meetings and the data is now 16 hours stale.',
                'priority': 'High', 'status': 'Completed',
                'viewer': 0, 'manager': 1,
                'notes': [
                    ('Comment', 'Gateway connection to the SQL Server data source had timed out. Restarted the on-premises data gateway and triggered a manual refresh. Dashboard now shows current data. Monitoring automatic refresh schedule.'),
                ]
            },
            {
                'cat': 'Data & Reporting', 'sub': 'Excel & Macros',
                'title': 'Excel macro not running — security policy blocking it',
                'problem_descp': 'The monthly premium reconciliation macro in our Excel workbook (Premium_Recon_v4.xlsm) is being blocked by a security policy error: "Macros have been disabled." This macro runs our month-end reconciliation and is critical for regulatory reporting.',
                'priority': 'High', 'status': 'Scoping',
                'viewer': 1, 'manager': 2,
                'notes': [
                    ('Field', 'Checked macro trust center settings. Group Policy is blocking unsigned macros.'),
                    ('Comment', 'Working with security team to add the finance reconciliation workbook to the trusted locations list under the new GPO.'),
                ]
            },
            {
                'cat': 'Data & Reporting', 'sub': 'Database Access',
                'title': 'Request for read access to Policy Admin database',
                'problem_descp': 'I am an analyst on the Customer Analytics team and require read-only access to the Policy Administration database (POLDB01) for a 3-month analytics project approved by VP Analytics, Jennifer Cho. Project code: CUST-ANLX-2024-Q1.',
                'priority': 'Moderate', 'status': 'Pending',
                'viewer': 2, 'manager': None,
                'notes': []
            },
            {
                'cat': 'Data & Reporting', 'sub': 'Data Export Requests',
                'title': 'Need 5-year historical claims data export for actuarial review',
                'problem_descp': 'The actuarial team requires a full export of 5 years of Group Benefits claims data (2019-2023) in CSV format for our annual reserve review. This has been approved by the Chief Actuary. Expected file size is approximately 2GB.',
                'priority': 'Moderate', 'status': 'In Progress',
                'viewer': 3, 'manager': 0,
                'notes': [
                    ('Comment', 'Query written and tested in UAT environment. Running on production — estimated completion in 3 hours due to data volume. Will deliver via secure file transfer.'),
                ]
            },
            {
                'cat': 'Data & Reporting', 'sub': 'SharePoint & OneDrive',
                'title': 'OneDrive sync stopped — 5GB of files not syncing',
                'problem_descp': 'My OneDrive stopped syncing 3 days ago. It shows "Processing changes" but never completes. I have about 5GB of project files that are not backed up to the cloud. I am concerned about data loss if something happens to my laptop.',
                'priority': 'Low', 'status': 'Assigned',
                'viewer': 4, 'manager': 1,
                'notes': [
                    ('Field', 'OneDrive sync issue logged. Checking for file path length issues.'),
                ]
            },

            # ── Additional mixed tickets ───────────────────────────
            {
                'cat': 'Hardware', 'sub': 'Laptop & Desktop',
                'title': 'Laptop fan making loud noise — overheating warnings',
                'problem_descp': 'My laptop fan has been making a loud grinding noise for the past 2 days and I am getting thermal warnings saying the CPU is overheating. The laptop shuts down automatically during heavy tasks. Asset tag: MNL-LT-7723.',
                'priority': 'Moderate', 'status': 'Completed',
                'viewer': 1, 'manager': 2,
                'notes': [
                    ('Comment', 'Laptop fan replaced. Thermal paste reapplied. Temperature now running at normal levels (45-55°C under load). No more overheating warnings.'),
                ]
            },
            {
                'cat': 'Network & Connectivity', 'sub': 'VPN & Remote Access',
                'title': 'New employee cannot connect to VPN — certificate error',
                'problem_descp': 'Our new team member, Carlos Rivera (started Monday), cannot connect to the Manulife VPN. He gets a certificate error: "The server certificate received is not trusted." His laptop was set up by IT but VPN was not configured.',
                'priority': 'Moderate', 'status': 'Pending',
                'viewer': 0, 'manager': None,
                'notes': []
            },
            {
                'cat': 'Software & Applications', 'sub': 'Microsoft Office 365',
                'title': 'SharePoint site permissions — team cannot access project site',
                'problem_descp': 'Our new project site "Project Phoenix" on SharePoint is not accessible to 8 team members. They get a "Access Denied" message. I created the site last week and added them as members but the permissions do not seem to have saved properly.',
                'priority': 'Low', 'status': 'Completed',
                'viewer': 2, 'manager': 0,
                'notes': [
                    ('Comment', 'SharePoint permissions were set at group level but users were added individually. Corrected by adding users to the Members group. All 8 team members confirmed access.'),
                ]
            },
            {
                'cat': 'Security & Access', 'sub': 'Account Lockout',
                'title': 'Service account for automated reports locked out',
                'problem_descp': 'The service account "svc_reports@manulife.com" used to run our automated daily reports has been locked out. 15 scheduled reports failed to run overnight including the daily risk report sent to executive leadership.',
                'priority': 'High', 'status': 'Cancelled',
                'viewer': 3, 'manager': 1,
                'notes': [
                    ('Field', 'Urgent — executive reports failed.'),
                    ('Comment', 'Account unlocked. Investigation showed an expired password caused repeated login failures. Password updated and account configured for extended expiry per service account policy.'),
                    ('Comment', 'User confirmed reports ran successfully tonight. Closing ticket.'),
                ]
            },
            {
                'cat': 'Data & Reporting', 'sub': 'Power BI & Reports',
                'title': 'Request for new KPI dashboard — Claims Processing team',
                'problem_descp': 'The Claims Processing team would like a new Power BI dashboard showing: daily claims volume by type, average processing time per claim, SLA compliance rate, and team productivity metrics. We have the data in SQL Server table CLAIMS_DAILY_SUMMARY.',
                'priority': 'Low', 'status': 'Pending',
                'viewer': 4, 'manager': None,
                'notes': []
            },
            {
                'cat': 'Hardware', 'sub': 'Mobile Devices',
                'title': 'Company tablet battery draining in 2 hours',
                'problem_descp': 'My company iPad (Asset #MNL-TAB-0156) battery drains from 100% to 0% in under 2 hours. It used to last all day. This is a problem as I use it for client meetings and field visits. It is constantly showing low battery warnings.',
                'priority': 'Low', 'status': 'Rejected',
                'viewer': 0, 'manager': None,
                'notes': []
            },
        ]

        created_count = 0
        for i, t in enumerate(tickets_data):
            cat    = self.categories[t['cat']]
            sub    = next(s for s in self.subcategories[t['cat']] if s.name == t['sub'])
            viewer = self.viewers[t['viewer']]
            manager = self.managers[t['manager']] if t['manager'] is not None else None
            admin  = User.objects.get(email='admin@manulife.com')

            # Check if ticket already exists
            if Ticket.objects.filter(title=t['title']).exists():
                continue

            # Create ticket — bypass save() signals by using update() after
            ticket = Ticket(
                category=cat,
                subcategory=sub,
                title=t['title'],
                problem_descp=t['problem_descp'],
                created_by=viewer,
                priority=t['priority'] if t['status'] != 'Pending' else None,
                status=t['status'],
                assigned_to=manager,
            )
            # Override save to skip Twilio in seeding
            Ticket.save = _silent_save
            ticket.save()
            Ticket.save = _original_save

            # Set realistic timestamps
            days_ago = random.randint(1, 30)
            created = timezone.now() - timedelta(days=days_ago)
            Ticket.objects.filter(pk=ticket.pk).update(created_at=created)

            # Set due_by if priority set
            if ticket.priority:
                sla_map = {'High': 4, 'Moderate': 24, 'Low': 72}
                hours = sla_map.get(ticket.priority, 24)
                due = created + timedelta(hours=hours)
                Ticket.objects.filter(pk=ticket.pk).update(due_by=due)

            # Set resolved_at for closed tickets
            if t['status'] in ('Completed', 'Cancelled', 'Rejected'):
                resolved = created + timedelta(hours=random.randint(2, 48))
                Ticket.objects.filter(pk=ticket.pk).update(resolved_at=resolved)

            # Create opening worknote
            Worknote.objects.create(
                ticket=ticket,
                type='Create',
                comment='',
                commented_by=viewer,
            )

            # Create assignment worknote if assigned
            if manager and t['status'] != 'Pending':
                Worknote.objects.create(
                    ticket=ticket,
                    type='Field',
                    comment='',
                    field_name='Status',
                    old_value='Pending',
                    new_value='Assigned',
                    commented_by=admin,
                )
                Worknote.objects.create(
                    ticket=ticket,
                    type='Field',
                    comment='',
                    field_name='Assigned to',
                    old_value='None',
                    new_value=manager.get_full_name(),
                    commented_by=admin,
                )

            # Add worknotes from data
            for note_type, note_text in t['notes']:
                author = manager if manager else admin
                Worknote.objects.create(
                    ticket=ticket,
                    type='Comment' if note_type == 'Comment' else 'Field',
                    comment=note_text,
                    field_name='Note' if note_type == 'Field' else '',
                    commented_by=author,
                )

            created_count += 1
            self.stdout.write(f'   ✓ [{ticket.number}] {t["title"][:55]}...' if len(t["title"]) > 55 else f'   ✓ [{ticket.number}] {t["title"]}')

        self.stdout.write(f'\n   Created {created_count} tickets total.')


# ── Helpers to bypass Twilio during seeding ──────────────────────

_original_save = Ticket.save

def _silent_save(self, *args, **kwargs):
    """Skip Twilio notifications during data seeding."""
    if not self.number:
        latest = Ticket.objects.all().order_by('id').last()
        next_id = (latest.id + 1) if latest else 1
        str_zeros = "0" * (6 - len(str(next_id)))
        self.number = "TKT" + str_zeros + str(next_id)

    from django.utils import timezone
    from datetime import timedelta
    from django.conf import settings

    if self.priority and not self.due_by:
        sla_hours = getattr(settings, 'SLA_HOURS', {'High': 4, 'Moderate': 24, 'Low': 72})
        hours = sla_hours.get(self.priority, 24)
        self.due_by = timezone.now() + timedelta(hours=hours)

    if self.status in ('Completed', 'Cancelled', 'Rejected') and not self.resolved_at:
        self.resolved_at = timezone.now()

    # Call the base Model save directly — skips our custom save()
    from django.db.models import Model
    Model.save(self, *args, **kwargs)
