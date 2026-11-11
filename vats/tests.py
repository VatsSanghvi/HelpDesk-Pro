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
