"""
Dashboard context, one shape per role.

The dashboard answers "what needs me now" before it shows any totals, so the
lists here are ordered by urgency and built on the server: they are the page,
not a widget that loads afterwards. Only the charts further down the page are
fetched from the analytics API.
"""
from django.db.models import Count
from django.urls import reverse

from registration.models import User
from .models import Ticket

OPEN_STATUSES = ('Pending', 'Assigned', 'Scoping', 'In Progress')
CLOSED_STATUSES = ('Completed', 'Cancelled', 'Rejected')

BOARD_ROWS = 7      # open tickets shown before "All tickets"; keeps the figures row in the first screen
TRIAGE_ROWS = 4     # untriaged tickets shown before "and N more"


def _plural(count, singular, plural=None):
    return singular if count == 1 else (plural or singular + 's')


def _scoped(user):
    base = Ticket.objects.select_related('category', 'subcategory', 'created_by', 'assigned_to')
    if user.role == 'Admin':
        return base
    if user.role == 'Manager':
        return base.filter(assigned_to=user)
    return base.filter(created_by=user)


def _headline(late, soon, untriaged, open_count, mine=False):
    """
    One sentence, worst news first. `mine` words it for a personal queue
    ("2 of your tickets") instead of the whole desk ("2 tickets").
    """
    def subject(count):
        return f"{count} of your tickets" if mine else f"{count} {_plural(count, 'ticket')}"

    if late:
        verb, its = ('is', 'its') if late == 1 else ('are', 'their')
        return f"{subject(late)} {verb} past {its} SLA deadline"
    if untriaged:
        verb = 'is' if untriaged == 1 else 'are'
        return f"{untriaged} new {_plural(untriaged, 'ticket')} {verb} waiting for triage"
    if soon:
        verb, its = ('is', 'its') if soon == 1 else ('are', 'their')
        return f"{subject(soon)} {verb} close to {its} SLA deadline"
    if open_count == 1:
        return "Your one open ticket is on time" if mine else "The one open ticket is on time"
    if open_count:
        return f"All {open_count} of your open tickets are on time" if mine else f"All {open_count} open tickets are on time"
    return "No open tickets"


def build_dashboard(user):
    scoped = _scoped(user)
    open_tickets = list(scoped.filter(status__in=OPEN_STATUSES))

    # Tickets with a running clock, most urgent first. Untriaged tickets have
    # no deadline yet, so they are listed separately rather than sorted last.
    clocked = sorted((t for t in open_tickets if t.due_by), key=lambda t: t.due_by)
    clocks = {t.pk: t.sla_clock for t in clocked}
    late = [t for t in clocked if clocks[t.pk] and clocks[t.pk]['tone'] == 'late']
    soon = [t for t in clocked if clocks[t.pk] and clocks[t.pk]['tone'] == 'soon']
    untriaged = sorted((t for t in open_tickets if t.status == 'Pending'), key=lambda t: t.created_at)

    resolved_hours = [t.resolution_time_hours for t in scoped if t.resolution_time_hours is not None]
    avg_resolution = round(sum(resolved_hours) / len(resolved_hours), 1) if resolved_hours else None

    responded_hours = [t.first_response_time_hours for t in scoped if t.first_response_time_hours is not None]
    ratings = [t.csat_rating for t in scoped if t.csat_rating is not None]

    context = {
        'avg_first_response': round(sum(responded_hours) / len(responded_hours), 1) if responded_hours else None,
        'avg_csat': round(sum(ratings) / len(ratings), 1) if ratings else None,
        'rated_count': len(ratings),
        'board': clocked[:BOARD_ROWS],
        'board_more': max(0, len(clocked) - BOARD_ROWS),
        'open_count': len(open_tickets),
        'late_count': len(late),
        'soon_count': len(soon),
        'untriaged_count': len(untriaged),
        'avg_resolution': avg_resolution,
    }

    if user.role == 'Admin':
        context['headline'] = _headline(len(late), len(soon), len(untriaged), len(open_tickets))
        # The sentences under the headline are also the shortcuts: on a phone
        # the triage panel is a long scroll away, the sentence about it is not.
        parts = []
        if late and untriaged:
            verb = 'is' if len(untriaged) == 1 else 'are'
            parts.append({
                'text': f"{len(untriaged)} new {_plural(len(untriaged), 'ticket')} {verb} waiting for triage.",
                'url': reverse('ticket_list_status', args=['Pending']),
            })
        if open_tickets:
            parts.append({
                'text': f"{len(open_tickets)} {'is' if len(open_tickets) == 1 else 'are'} open in total.",
                'url': reverse('ticket_list'),
            })
        else:
            parts.append({'text': "New tickets appear here as soon as someone raises one."})
        context['lede_parts'] = parts
        context['untriaged'] = untriaged[:TRIAGE_ROWS]
        context['untriaged_more'] = max(0, len(untriaged) - TRIAGE_ROWS)

        team = []
        for manager in User.objects.filter(role='Manager', is_active=True).order_by('first_name'):
            mine = [t for t in open_tickets if t.assigned_to_id == manager.pk]
            team.append({
                'user': manager,
                'open': len(mine),
                'late': sum(1 for t in mine if clocks.get(t.pk) and clocks[t.pk]['tone'] == 'late'),
            })
        busiest = max((m['open'] for m in team), default=0)
        for member in team:
            member['share'] = round(member['open'] / busiest * 100) if busiest else 0
        context['team'] = sorted(team, key=lambda m: -m['open'])

    elif user.role == 'Manager':
        context['headline'] = _headline(len(late), len(soon), 0, len(open_tickets), mine=True)
        if open_tickets:
            context['lede_parts'] = [{
                'text': (
                    f"{len(open_tickets)} {_plural(len(open_tickets), 'ticket')} "
                    f"{'is' if len(open_tickets) == 1 else 'are'} assigned to you and still open."
                ),
                'url': reverse('my_tickets'),
            }]
        else:
            context['lede_parts'] = [{'text': "Tickets appear here when an Admin assigns them to you."}]
        by_status = dict(
            scoped.filter(status__in=OPEN_STATUSES)
                  .values_list('status').annotate(n=Count('id')).values_list('status', 'n')
        )
        context['stages'] = [
            {'status': name, 'count': by_status.get(name, 0)}
            for name in ('Assigned', 'Scoping', 'In Progress')
        ]
        context['resolved_count'] = scoped.filter(status__in=CLOSED_STATUSES).count()

    else:  # Viewer
        mine_open = sorted(open_tickets, key=lambda t: t.created_at, reverse=True)
        count = len(mine_open)
        if count:
            context['headline'] = f"You have {count} open {_plural(count, 'ticket')}"
            context['lede_parts'] = [{'text': "Each one shows where it stands and when it is due. You will get an email when its status changes."}]
        else:
            context['headline'] = "You have no open tickets"
            context['lede_parts'] = [{'text': "Something not working? Raise a ticket and the IT team will pick it up."}]
        context['my_open'] = mine_open
        context['my_closed'] = list(
            scoped.filter(status__in=CLOSED_STATUSES).order_by('-updated_at')[:5]
        )

    return context
