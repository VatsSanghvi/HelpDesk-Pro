"""
vats/models.py  —  HelpDesk Pro v2
Upgrades from original:
  1. Twilio credentials moved to settings.py (read from .env) — fixes the
     hardcoded API keys that were exposed in your public GitHub repo
  2. Added `due_by`      — SLA deadline auto-set from priority on creation
  3. Added `resolved_at` — timestamp when ticket first hits Completed/Cancelled
  4. Added `is_sla_breached` property — used by dashboard analytics
  5. Added `resolution_time_hours` property — avg resolution time for reports
  6. All existing field names UNCHANGED (problem_descp, priority choices, etc.)
  7. Existing Worknote model UNCHANGED — it already serves as your audit trail
"""
from urllib import request as urllib_request
from django.db import models
from django.forms import Textarea
from django.utils.translation import gettext as _
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import os


class Category(models.Model):

    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")    # fixed typo from "Categorys"

    def __str__(self):
        return self.name


class Subcategory(models.Model):

    category = models.ForeignKey("vats.Category", on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")    # fixed typo from "Subcategorys"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Subcategory_detail", kwargs={"id": self.id})


class Ticket(models.Model):
    # ── Status choices (UNCHANGED) ────────────────────────────────────────────
    status_choice = (
        ("Pending",     "Pending"),
        ("Assigned",    "Assigned"),
        ("Scoping",     "Scoping"),
        ("In Progress", "In Progress"),
        ("Completed",   "Completed"),
        ("Cancelled",   "Cancelled"),
        ("Rejected",    "Rejected"),
    )

    # ── Priority choices (UNCHANGED) ─────────────────────────────────────────
    priority_choice = (
        ("High",     "High"),
        ("Moderate", "Moderate"),
        ("Low",      "Low"),
    )

    # ── Original fields (ALL UNCHANGED) ──────────────────────────────────────
    number       = models.CharField(_("Number"), max_length=50, null=True, blank=True)
    category     = models.ForeignKey("vats.Category", on_delete=models.CASCADE)
    subcategory  = models.ForeignKey("vats.Subcategory", on_delete=models.CASCADE)
    title        = models.CharField(_("Title"), max_length=50)
    problem_descp = models.TextField(_("Problem Description"), max_length=500)
    created_by   = models.ForeignKey(
        "registration.User", related_name=_("Issues"), on_delete=models.CASCADE
    )
    priority     = models.CharField(
        _("Priority"), max_length=50, null=True, blank=True, choices=priority_choice
    )
    created_at   = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at   = models.DateTimeField(_("Updated at"), auto_now=True)
    assigned_to  = models.ForeignKey(
        "registration.User", related_name=_("Tasks"),
        on_delete=models.SET_NULL, null=True, blank=True
    )
    status       = models.CharField(
        _("Status"), max_length=50, choices=status_choice, null=True, blank=True
    )

    # ── NEW fields added in v2 ────────────────────────────────────────────────
    due_by       = models.DateTimeField(
        _("SLA Due By"), null=True, blank=True,
        help_text="Auto-set from priority when ticket is assigned. Shows on dashboard."
    )
    resolved_at  = models.DateTimeField(
        _("Resolved At"), null=True, blank=True,
        help_text="Auto-set when status changes to Completed or Cancelled."
    )

    # ── NEW fields added in v2.2 ──────────────────────────────────────────────
    first_response_at = models.DateTimeField(
        _("First Response At"), null=True, blank=True,
        help_text="Auto-set the first time a Manager moves the ticket past 'Assigned' (Scoping/In Progress/Completed/Cancelled/Rejected)."
    )
    csat_rating  = models.PositiveSmallIntegerField(
        _("CSAT Rating"), null=True, blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="1-5 satisfaction rating, submitted by the ticket creator once the ticket is Completed."
    )
    csat_feedback = models.TextField(
        _("CSAT Feedback"), max_length=500, null=True, blank=True,
        help_text="Optional free-text feedback submitted alongside the CSAT rating."
    )

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return self.number or str(self.id)

    # ── save() — upgraded from original ──────────────────────────────────────
    def save(self, *args, **kwargs):
        # Auto-generate ticket number (UNCHANGED from original)
        if not self.number:
            latest = Ticket.objects.all().order_by('number').last()
            if latest:
                number = int(latest.number[3:]) + 1
            else:
                number = 1
            str_zeros = "0" * (6 - len(str(number)))
            self.number = "TKT" + str_zeros + str(number)

        # ── NEW: auto-set SLA deadline when priority is first assigned ────────
        if self.priority and not self.due_by:
            sla_hours = getattr(settings, 'SLA_HOURS', {
                'High': 4, 'Moderate': 24, 'Low': 72
            })
            hours = sla_hours.get(self.priority, 24)
            self.due_by = timezone.now() + timedelta(hours=hours)

        # ── NEW: stamp resolved_at when ticket is first completed/cancelled ───
        if self.status in ('Completed', 'Cancelled', 'Rejected') and not self.resolved_at:
            self.resolved_at = timezone.now()

        # ── NEW: stamp first_response_at the first time a Manager actually
        #    engages with the ticket (i.e. it leaves Pending/Assigned) ────────
        if self.status not in (None, 'Pending', 'Assigned') and not self.first_response_at:
            self.first_response_at = timezone.now()

        # ── Twilio WhatsApp notification (FIXED: credentials from settings) ───
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token  = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '')
        to_number   = getattr(settings, 'TWILIO_TO_NUMBER', '')

        if account_sid and auth_token and from_number and to_number:
            try:
                from twilio.rest import Client
                client = Client(account_sid, auth_token)
                if self.status == 'Pending':
                    body = 'Your ticket has been generated and the details have been mailed to you.'
                else:
                    body = f'Your ticket {self.number} status has been changed to: {self.status}.'
                client.messages.create(body=body, from_=from_number, to=to_number)
            except Exception as e:
                # Don't crash the save if Twilio fails
                print(f"Twilio notification failed: {e}")

        return super(Ticket, self).save(*args, **kwargs)

    # ── Original helper methods (UNCHANGED) ──────────────────────────────────
    def is_open(self):
        if self.status == 'Completed' or self.status == 'Cancelled':
            return False
        return True

    def get_created_at(self):
        date = self.created_at + timedelta(days=0, hours=5, minutes=30)
        return date

    def get_updated_at(self):
        date = self.updated_at + timedelta(days=0, hours=5, minutes=30)
        return date

    def work_note_list(self):
        return Worknote.objects.filter(ticket=self).order_by('-created_at')

    # ── NEW computed properties for analytics dashboard ───────────────────────
    @property
    def is_sla_breached(self):
        """True if ticket is overdue and not yet resolved. Powers dashboard red badges."""
        if not self.due_by:
            return False
        if self.status in ('Completed', 'Cancelled', 'Rejected'):
            return False
        return timezone.now() > self.due_by

    @property
    def resolution_time_hours(self):
        """Hours from creation to resolution. Used for avg resolution time KPI."""
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.created_at
        return round(delta.total_seconds() / 3600, 2)

    @property
    def age_hours(self):
        """How old this ticket is in hours — useful for 'aging' report."""
        delta = timezone.now() - self.created_at
        return round(delta.total_seconds() / 3600, 2)

    @staticmethod
    def _duration_text(seconds):
        """Format a span as '2h 15m', or '18m' when under an hour."""
        seconds = int(abs(seconds))
        hours, minutes = divmod(seconds // 60, 60)
        if hours >= 24:
            # Hour precision is noise at this scale — nobody triages on
            # "92d 11h" differently than on "92d".
            return f"{hours // 24}d"
        if hours:
            return f"{hours}h {minutes}m" if minutes else f"{hours}h"
        return f"{minutes}m"

    @property
    def sla_state(self):
        """
        Drives the SLA column. One of:
          breached | critical | remaining | met | missed | suspended | no_sla | None

        Open tickets get a live countdown that sharpens as the deadline nears.
        Closed tickets get a verdict instead, because a countdown is
        meaningless on a ticket that is already finished — and Cancelled and
        Rejected are distinguished from "Completed late", since neither is a
        service failure.
        """
        if self.status == 'Rejected':
            return 'no_sla'          # never entered the queue, so never had an SLA
        if self.status == 'Cancelled':
            return 'suspended'       # the clock stopped, nobody failed
        if not self.due_by:
            return None
        if self.status == 'Completed':
            if not self.resolved_at:
                return None
            return 'met' if self.resolved_at <= self.due_by else 'missed'

        seconds_left = (self.due_by - timezone.now()).total_seconds()
        if seconds_left < 0:
            return 'breached'
        return 'critical' if seconds_left <= 3600 else 'remaining'

    @property
    def sla_label(self):
        """Human text for the SLA column, matching the state."""
        state = self.sla_state
        if state is None:
            return ''
        # The column header already says "SLA State", so the cells drop the
        # redundant "SLA" prefix — that word cost ~40px on every row and said
        # nothing the header hadn't. The duration is the part that matters.
        if state == 'no_sla':
            return 'No SLA'
        if state == 'suspended':
            return 'Suspended'
        if state == 'met':
            return 'On time'
        if state == 'missed':
            over = (self.resolved_at - self.due_by).total_seconds()
            return f"Late (+{self._duration_text(over)})"

        seconds_left = (self.due_by - timezone.now()).total_seconds()
        if state == 'breached':
            return f"Breached (+{self._duration_text(seconds_left)})"
        if state == 'critical':
            return f"{self._duration_text(seconds_left)} left"
        return f"{self._duration_text(seconds_left)} remaining"

    @property
    def sla_icon(self):
        return {
            'breached':  'warning',
            'critical':  'alarm',
            'remaining': 'schedule',
            'met':       'check_circle',
            'missed':    'running_with_errors',
            'suspended': 'pause_circle',
            'no_sla':    'block',
        }.get(self.sla_state, 'schedule')

    @property
    def first_response_time_hours(self):
        """Hours from creation to first real Manager engagement. Support teams call this FRT."""
        if not self.first_response_at:
            return None
        delta = self.first_response_at - self.created_at
        return round(delta.total_seconds() / 3600, 2)


class Worknote(models.Model):
    """
    UNCHANGED from original.
    This already works as your audit trail:
      type = "Create"  → ticket was opened
      type = "Comment" → someone added a work note
      type = "Field"   → a field was changed (field_name, old_value, new_value)
    """
    type_choice = (
        ("Create",  "Create"),
        ("Comment", "Comment"),
        ("Field",   "Field"),
    )

    ticket       = models.ForeignKey(
        "vats.Ticket", related_name="Worknotes", on_delete=models.CASCADE
    )
    type         = models.CharField(
        _("Type"), max_length=50, blank=True, null=True, choices=type_choice
    )
    comment      = models.TextField(_("Comments"))
    commented_by = models.ForeignKey("registration.User", on_delete=models.CASCADE)
    created_at   = models.DateTimeField(_("Created Date/Time"), auto_now_add=True)
    field_name   = models.CharField(_("Field name"), max_length=40, blank=True, null=True)
    old_value    = models.CharField(_("Old value"), max_length=40, blank=True, null=True)
    new_value    = models.CharField(_("new value"), max_length=40, blank=True, null=True)

    class Meta:
        verbose_name = _("Worknote")
        verbose_name_plural = _("Worknotes")

    def __str__(self):
        return str(self.ticket.created_by) + " - " + str(self.type)

    def get_absolute_url(self):
        return reverse("Worknote_detail", kwargs={"id": self.id})

    def get_created_at(self):
        date = self.created_at + timedelta(days=0, hours=5, minutes=30)
        return date


class Notification(models.Model):
    """
    In-app notifications for the topbar bell.

    Deliberately created only from real lifecycle events — assignment, status
    change, a new work note. Nothing is seeded, so an empty bell honestly
    means nothing has happened to your tickets yet.
    """
    kind_choice = (
        ("Assigned", "Assigned"),
        ("Status",   "Status"),
        ("Comment",  "Comment"),
        ("SLA",      "SLA"),
    )

    recipient  = models.ForeignKey(
        "registration.User", related_name="notifications", on_delete=models.CASCADE
    )
    actor      = models.ForeignKey(
        "registration.User", related_name="notifications_sent",
        null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Who caused this. Null for system-generated events."
    )
    kind       = models.CharField(_("Kind"), max_length=20, choices=kind_choice, default="Status")
    text       = models.CharField(_("Text"), max_length=200)
    ticket     = models.ForeignKey(
        "vats.Ticket", related_name="notifications",
        null=True, blank=True, on_delete=models.CASCADE
    )
    is_read    = models.BooleanField(_("Read"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} — {self.text[:40]}"

    @property
    def icon(self):
        """Material Symbols name for the bell dropdown."""
        return {
            "Assigned": "assignment_ind",
            "Status":   "sync_alt",
            "Comment":  "chat",
            "SLA":      "warning",
        }.get(self.kind, "notifications")

    def get_created_at(self):
        return self.created_at + timedelta(days=0, hours=5, minutes=30)


def notify(recipient, text, kind="Status", ticket=None, actor=None):
    """
    Create a notification, skipping the case where someone would be told
    about their own action — being notified that you did the thing you just
    did is noise, not information.
    """
    if recipient is None:
        return None
    if actor is not None and recipient == actor:
        return None
    return Notification.objects.create(
        recipient=recipient, actor=actor, kind=kind, text=text, ticket=ticket
    )
