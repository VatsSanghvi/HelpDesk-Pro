"""
Tests for the screens and for the two calculations the interface rests on:
the SLA clock and the dashboard summary.

Run with:  python manage.py test
"""
import re
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from registration.models import User
from vats.dashboard import build_dashboard
from vats.models import Category, Subcategory, Ticket, Worknote
from vats.templatetags.ui_extras import ago, lifecycle

PASSWORD = "Sup3r-secret-pass"

# Anything a browser would fetch from another host: src/href/url() pointing
# at http(s) or a protocol-relative address. An SVG xmlns is not a request.
OUTSIDE_REQUEST = re.compile(r'''(?:src|href)=["\']?(?:https?:)?//|url\((?:["\']?)(?:https?:)?//''')


def make_user(email, role, first="Test", last="Person"):
    user = User.objects.create_user(first, last, email, PASSWORD)
    user.role = role
    user.save()
    return user


class Fixture(TestCase):
    """One category, three people, and a helper that builds dated tickets."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Hardware")
        cls.subcategory = Subcategory.objects.create(category=cls.category, name="Laptop & Desktop")
        cls.admin = make_user("admin@example.com", "Admin", "Alex", "Admin")
        cls.manager = make_user("manager@example.com", "Manager", "Sarah", "Chen")
        cls.viewer = make_user("viewer@example.com", "Viewer", "James", "Wilson")

    def ticket(self, title, status="Assigned", priority="High", used=0.5, manager=None):
        """
        A ticket whose SLA window is `used` consumed: 0.5 is halfway through,
        1.2 is 20% past the deadline. Pending tickets get no priority or clock.
        """
        pending = status == "Pending"
        ticket = Ticket.objects.create(
            category=self.category, subcategory=self.subcategory, title=title,
            problem_descp="It stopped working.", created_by=self.viewer,
            status=status, priority=None if pending else priority,
            assigned_to=None if pending else (manager or self.manager),
        )
        Worknote.objects.create(ticket=ticket, type="Create", comment="", commented_by=self.viewer)
        if not pending:
            window = timedelta(hours={"High": 4, "Moderate": 24, "Low": 72}[priority])
            created = timezone.now() - window * used
            Ticket.objects.filter(pk=ticket.pk).update(created_at=created, due_by=created + window)
            ticket.refresh_from_db()
        return ticket


class SlaClockTests(Fixture):

    def test_halfway_is_on_time(self):
        clock = self.ticket("Halfway", used=0.5).sla_clock
        self.assertEqual(clock["tone"], "ok")
        self.assertEqual(clock["used"], 50)
        # The track spans the window plus a third, so halfway sits at 37.5%.
        self.assertAlmostEqual(clock["pct"], 37.5, delta=0.5)

    def test_last_quarter_of_the_window_warns(self):
        self.assertEqual(self.ticket("Late stage", priority="Low", used=0.8).sla_clock["tone"], "soon")

    def test_last_hour_warns_even_early_in_a_short_window(self):
        # A 4-hour ticket with 50 minutes left has used ~79% of its window.
        self.assertEqual(self.ticket("Nearly due", used=0.79).sla_clock["tone"], "soon")

    def test_past_the_deadline_is_late_and_the_marker_stays_on_the_track(self):
        clock = self.ticket("Overdue", used=3.0).sla_clock
        self.assertEqual(clock["tone"], "late")
        self.assertEqual(clock["pct"], 100.0)

    def test_untriaged_and_closed_tickets_have_no_running_clock(self):
        self.assertIsNone(self.ticket("New", status="Pending").sla_clock)
        self.assertIsNone(self.ticket("Done", status="Completed").sla_clock)

    def test_due_time_uses_the_same_display_offset_as_created(self):
        ticket = self.ticket("Offsets")
        self.assertEqual(ticket.get_due_by() - ticket.due_by, ticket.get_created_at() - ticket.created_at)


class DashboardTests(Fixture):

    def test_admin_headline_leads_with_late_tickets(self):
        self.ticket("Overdue", used=1.5)
        self.ticket("Fine", used=0.2)
        self.ticket("New", status="Pending")
        context = build_dashboard(self.admin)
        self.assertEqual(context["headline"], "1 ticket is past its SLA deadline")
        self.assertEqual(context["late_count"], 1)
        self.assertEqual(context["untriaged_count"], 1)
        self.assertEqual(context["open_count"], 3)
        # Most urgent first.
        self.assertEqual([t.title for t in context["board"]], ["Overdue", "Fine"])

    def test_admin_headline_falls_back_to_triage_then_to_all_clear(self):
        self.ticket("New", status="Pending")
        self.assertEqual(build_dashboard(self.admin)["headline"], "1 new ticket is waiting for triage")
        Ticket.objects.all().delete()
        self.assertEqual(build_dashboard(self.admin)["headline"], "No open tickets")

    def test_team_workload_counts_open_and_late_per_manager(self):
        other = make_user("other@example.com", "Manager", "Priya", "Nair")
        self.ticket("Overdue", used=1.5)
        self.ticket("Fine", used=0.2)
        self.ticket("Theirs", used=0.2, manager=other)
        team = {m["user"].email: m for m in build_dashboard(self.admin)["team"]}
        self.assertEqual((team["manager@example.com"]["open"], team["manager@example.com"]["late"]), (2, 1))
        self.assertEqual((team["other@example.com"]["open"], team["other@example.com"]["late"]), (1, 0))

    def test_manager_sees_only_their_own_tickets(self):
        other = make_user("other@example.com", "Manager", "Priya", "Nair")
        self.ticket("Mine", used=0.2)
        self.ticket("Theirs", used=1.5, manager=other)
        context = build_dashboard(self.manager)
        self.assertEqual([t.title for t in context["board"]], ["Mine"])
        self.assertEqual(context["headline"], "Your one open ticket is on time")

    def test_manager_headline_reads_correctly_for_one_late_ticket(self):
        self.ticket("Overdue", used=1.5)
        self.ticket("Fine", used=0.2)
        self.assertEqual(build_dashboard(self.manager)["headline"], "1 of your tickets is past its SLA deadline")

    def test_admin_sentences_link_to_the_queues_they_describe(self):
        self.ticket("Overdue", used=1.5)
        self.ticket("New", status="Pending")
        urls = [part.get("url") for part in build_dashboard(self.admin)["lede_parts"]]
        self.assertEqual(urls, [reverse("ticket_list_status", args=["Pending"]), reverse("ticket_list")])

    def test_viewer_sees_their_open_tickets(self):
        self.ticket("Mine", used=0.2)
        context = build_dashboard(self.viewer)
        self.assertEqual(context["headline"], "You have 1 open ticket")
        self.assertEqual([t.title for t in context["my_open"]], ["Mine"])


class HelperTests(Fixture):

    def test_lifecycle_marks_done_current_and_todo(self):
        states = [step["state"] for step in lifecycle(self.ticket("Working", status="Scoping"))]
        self.assertEqual(states, ["done", "done", "current", "todo", "todo"])

    def test_lifecycle_of_a_rejected_ticket_stops_at_pending(self):
        ticket = self.ticket("No", status="Pending")
        ticket.status = "Rejected"
        self.assertEqual(lifecycle(ticket)[0]["state"], "stopped")

    def test_ago_uses_one_unit(self):
        now = timezone.now()
        self.assertEqual(ago(now - timedelta(seconds=20)), "just now")
        self.assertEqual(ago(now - timedelta(minutes=35)), "35 min ago")
        self.assertEqual(ago(now - timedelta(hours=3)), "3 h ago")
        self.assertEqual(ago(now - timedelta(days=4)), "4 days ago")


class ScreenTests(Fixture):
    """Every screen renders for the roles allowed to open it."""

    def setUp(self):
        self.open = self.ticket("Open ticket", status="In Progress", used=0.9)
        self.new = self.ticket("New ticket", status="Pending")
        self.done = self.ticket("Done ticket", status="Completed", used=0.4)

    def assert_ok(self, user, names_and_args):
        self.client.force_login(user)
        for name, args in names_and_args:
            with self.subTest(role=user.role, screen=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)

    def test_sign_in_page(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Sign In")
        self.assertIsNone(OUTSIDE_REQUEST.search(response.content.decode()))

    def test_admin_screens(self):
        self.assert_ok(self.admin, [
            ("home", []), ("ticket_list", []), ("my_tickets", []),
            ("ticket_list_status", ["Pending"]), ("ticket_detail", [self.open.id]),
            ("ticket_detail", [self.new.id]), ("ticket_approve", [self.new.id]),
            ("user_list", []), ("user_list_role", ["Manager"]), ("user_create", []),
            ("user_detail", [self.manager.id]), ("profile", [self.admin.id]),
            ("category_list", []), ("category_create", []),
            ("subcategory_list", [self.category.id]), ("subcategory_create", [self.category.id]),
            ("password_change", []),
        ])

    def test_manager_screens(self):
        self.assert_ok(self.manager, [
            ("home", []), ("ticket_list", []), ("my_tickets", []),
            ("ticket_detail", [self.open.id]), ("ticket_update", [self.open.id]),
            ("profile", [self.manager.id]),
        ])

    def test_viewer_screens(self):
        self.assert_ok(self.viewer, [
            ("home", []), ("ticket_list", []), ("my_tickets", []), ("ticket_create", []),
            ("ticket_detail", [self.open.id]), ("ticket_detail", [self.done.id]),
            ("profile", [self.viewer.id]),
        ])

    def test_pages_load_nothing_from_outside(self):
        """Fonts, icons, styles and scripts all ship with the app."""
        self.client.force_login(self.admin)
        for name in ("home", "ticket_list"):
            html = self.client.get(reverse(name)).content.decode()
            found = OUTSIDE_REQUEST.search(html)
            self.assertIsNone(found, f"{name} loads something from outside: {found.group(0) if found else ''}")

    def test_only_viewers_are_offered_raise_ticket(self):
        self.client.force_login(self.admin)
        self.assertNotContains(self.client.get(reverse("home")), reverse("ticket_create"))
        self.client.force_login(self.viewer)
        self.assertContains(self.client.get(reverse("home")), reverse("ticket_create"))

    def test_dashboard_shows_the_clock_for_an_open_ticket(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "clock-soon")
        self.assertContains(response, "Open ticket")
        self.assertContains(response, "waiting for triage")

    def test_ticket_list_puts_what_needs_attention_first(self):
        self.ticket("Due later", status="Assigned", priority="Low", used=0.1)
        self.ticket("Overdue", status="Assigned", used=1.5)
        self.client.force_login(self.admin)
        titles = [t.title for t in self.client.get(reverse("ticket_list")).context["tickets"]]
        # On the clock by deadline, then untriaged, then closed.
        self.assertEqual(titles, ["Overdue", "Open ticket", "Due later", "New ticket", "Done ticket"])

    def test_employee_dashboard_shows_when_a_ticket_is_due(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="clock clock-soon"')
        self.assertContains(response, "Its deadline is set then.")

    def test_triage_form_says_what_to_choose(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("ticket_approve", args=[self.new.id]), {})
        self.assertContains(response, "Choose a priority.")
        self.assertContains(response, "Choose a manager.")

    def test_deleting_a_subcategory_returns_to_its_list(self):
        spare = Subcategory.objects.create(category=self.category, name="Spare")
        self.client.force_login(self.admin)
        response = self.client.get(reverse("subcategory_delete", args=[spare.id]))
        self.assertRedirects(response, reverse("subcategory_list", args=[self.category.id]))


# ── Assignment emails, transfer, turnaround time, email-to-ticket ─────────
from datetime import datetime, timezone as dt_timezone
from email.message import EmailMessage as RawEmail

from django.core import mail
from django.test import override_settings

from vats.inbound import guess_category, process_message
from vats.models import Detail, InboundEmail
from vats.worktime import duration_text, working_seconds


def utc(day, hour, minute=0):
    """A UTC time in November 2026. The working day (09:00-18:00 at +5:30) is 03:30-12:30 UTC."""
    return datetime(2026, 11, day, hour, minute, tzinfo=dt_timezone.utc)


class WorkingTimeTests(TestCase):

    def test_ten_minutes_inside_the_working_day(self):
        self.assertEqual(working_seconds(utc(16, 4, 0), utc(16, 4, 10)), 600)   # Monday

    def test_overnight_counts_only_working_hours(self):
        # Monday 17:50 local to Tuesday 09:10 local: 10 minutes + 10 minutes.
        self.assertEqual(working_seconds(utc(16, 12, 20), utc(17, 3, 40)), 1200)

    def test_weekend_is_not_counted(self):
        # Friday 17:00 local to Monday 10:00 local: 1 hour + 1 hour.
        self.assertEqual(working_seconds(utc(13, 11, 30), utc(16, 4, 30)), 7200)

    def test_duration_reads_in_minutes_and_hours(self):
        self.assertEqual(duration_text(600), '10 min')
        self.assertEqual(duration_text(8100), '2 h 15 min')
        self.assertEqual(duration_text(20), 'under 1 min')


class AssignmentAndTransferTests(Fixture):

    def setUp(self):
        self.other = make_user("other@example.com", "Manager", "Priya", "Nair")
        self.new = self.ticket("Printer jam", status="Pending")
        mail.outbox = []

    def approve(self):
        self.client.force_login(self.admin)
        return self.client.post(reverse("ticket_approve", args=[self.new.id]), {
            "category": self.category.id, "subcategory": self.subcategory.id,
            "priority": "High", "assigned_to": self.manager.id,
        })

    def test_assignment_emails_the_assignee_and_the_requester(self):
        self.approve()
        self.new.refresh_from_db()
        self.assertIsNotNone(self.new.assigned_at)
        sent = {(m.to[0], m.subject) for m in mail.outbox}
        self.assertIn(("manager@example.com", f"[{self.new.number}] Ticket assigned to you"), sent)
        self.assertIn(("viewer@example.com", f"[{self.new.number}] Your ticket has been assigned"), sent)

    def test_transfer_moves_the_ticket_and_tells_everyone(self):
        self.approve()
        mail.outbox = []
        self.client.force_login(self.manager)
        self.client.post(reverse("ticket_transfer", args=[self.new.id]),
                         {"assigned_to": self.other.id, "reason": "Needs network access"})
        self.new.refresh_from_db()
        self.assertEqual(self.new.assigned_to, self.other)
        self.assertEqual({m.to[0] for m in mail.outbox}, {"other@example.com", "viewer@example.com"})
        notes = list(self.new.Worknotes.values_list("field_name", "old_value", "new_value", "comment"))
        self.assertIn(("Assigned to", "Sarah Chen", "Priya Nair", ""), notes)
        self.assertTrue(any("Needs network access" in n[3] for n in notes))
        # The previous owner no longer has the ticket in their queue.
        self.assertNotContains(self.client.get(reverse("ticket_list")), "Printer jam")

    def test_only_the_owner_or_an_admin_can_transfer_or_edit(self):
        self.approve()
        self.client.force_login(self.other)
        self.client.post(reverse("ticket_transfer", args=[self.new.id]), {"assigned_to": self.other.id})
        self.new.refresh_from_db()
        self.assertEqual(self.new.assigned_to, self.manager)
        self.assertEqual(self.client.get(reverse("ticket_update", args=[self.new.id])).status_code, 302)

    def test_rejection_is_recorded_and_emailed(self):
        self.client.force_login(self.admin)
        self.client.get(reverse("ticket_reject", args=[self.new.id]))
        self.assertTrue(self.new.Worknotes.filter(field_name="Status", new_value="Rejected").exists())
        self.assertEqual(mail.outbox[-1].to, ["viewer@example.com"])

    def test_turnaround_runs_from_assignment_to_completion(self):
        ticket = self.ticket("Done", status="Completed")
        Ticket.objects.filter(pk=ticket.pk).update(assigned_at=utc(16, 4, 5), resolved_at=utc(16, 4, 15))
        ticket.refresh_from_db()
        self.assertEqual(ticket.turnaround_text, "10 min")


def raw_email(sender, subject, body, message_id="<m1@mail>", **headers):
    message = RawEmail()
    message["From"], message["To"], message["Subject"], message["Message-ID"] = sender, "support@example.com", subject, message_id
    for key, value in headers.items():
        message[key.replace("_", "-")] = value
    message.set_content(body)
    return message.as_bytes()


class EmailToTicketTests(Fixture):

    def setUp(self):
        mail.outbox = []

    def test_email_from_a_known_user_becomes_a_ticket_and_is_confirmed(self):
        outcome, ticket = process_message(raw_email("James <viewer@example.com>", "Laptop & Desktop will not start", "It is dead."))
        self.assertEqual(outcome, "ticket")
        self.assertEqual((ticket.title, ticket.status, ticket.source), ("Laptop & Desktop will not start", "Pending", "Email"))
        # The category was read from the wording.
        self.assertEqual((ticket.category, ticket.subcategory), (self.category, self.subcategory))
        self.assertEqual(mail.outbox[0].to, ["viewer@example.com"])
        self.assertIn(ticket.number, mail.outbox[0].subject)

    def test_email_that_names_no_category_is_left_for_triage(self):
        _, ticket = process_message(raw_email("viewer@example.com", "Something is wrong", "Please help."))
        self.assertIsNone(ticket.category)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("ticket_detail", args=[ticket.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_reply_with_the_ticket_number_adds_a_note_without_the_quote(self):
        ticket = self.ticket("Existing")
        body = "Still broken today.\n\nOn Mon, someone wrote:\n> earlier text"
        outcome, _ = process_message(raw_email("viewer@example.com", f"Re: [{ticket.number}] Ticket status updated", body))
        self.assertEqual(outcome, "note")
        self.assertEqual(ticket.Worknotes.filter(type="Comment").last().comment, "Still broken today.")

    def test_unknown_sender_waits_for_an_admin_who_can_accept(self):
        outcome, held = process_message(raw_email("New Person <stranger@elsewhere.com>", "Need help", "Hello."))
        self.assertEqual((outcome, held.status), ("held", "Held"))
        self.assertEqual(Ticket.objects.count(), 0)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("inbound_list")), "stranger@elsewhere.com")
        self.client.post(reverse("inbound_decide", args=[held.id]), {"decision": "accept"})
        ticket = Ticket.objects.get()
        self.assertEqual((ticket.created_by.email, ticket.created_by.role), ("stranger@elsewhere.com", "Viewer"))

    @override_settings(SUPPORT_ALLOWED_DOMAINS=["company.com"])
    def test_sender_outside_the_company_domain_is_held(self):
        outcome, held = process_message(raw_email("viewer@example.com", "Need help", "Hello."))
        self.assertEqual((outcome, held.reason), ("held", "Sender is outside the company domain"))

    def test_automatic_and_duplicate_emails_are_skipped(self):
        self.assertEqual(process_message(raw_email("viewer@example.com", "Out of office", "Away.", Auto_Submitted="auto-replied"))[0], "skipped")
        process_message(raw_email("viewer@example.com", "One", "Body", message_id="<dup@mail>"))
        self.assertEqual(process_message(raw_email("viewer@example.com", "One", "Body", message_id="<dup@mail>"))[0], "skipped")

    def test_the_most_specific_category_level_wins(self):
        detail = Detail.objects.create(subcategory=self.subcategory, name="Docking station")
        self.assertEqual(guess_category("My laptop & desktop docking station is dead")[2], detail)
        self.assertEqual(guess_category("General hardware question"), (self.category, None, None))
        self.assertEqual(guess_category("Nothing relevant"), (None, None, None))
