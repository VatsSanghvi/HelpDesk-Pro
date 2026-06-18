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
