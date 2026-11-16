from django.db import migrations


def backfill(apps, schema_editor):
    """Give existing tickets an assignment time: the moment the audit trail
    recorded their first assignment, or their creation time if it has none."""
    Ticket = apps.get_model('vats', 'Ticket')
    Worknote = apps.get_model('vats', 'Worknote')
    for ticket in Ticket.objects.filter(assigned_at__isnull=True, assigned_to__isnull=False):
        note = (Worknote.objects.filter(ticket=ticket, field_name='Assigned to')
                .order_by('created_at').first())
        ticket.assigned_at = note.created_at if note else ticket.created_at
        ticket.save(update_fields=['assigned_at'])


class Migration(migrations.Migration):
    dependencies = [('vats', '0004_ticket_assigned_at_ticket_source_and_more')]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
