from dataclasses import field
from django.urls import reverse
import importlib
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import  Ticket, Category, Subcategory, Detail, Worknote, Notification, InboundEmail, notify
from .forms import TicketForm, CategoryForm, TicketUpdateForm, SubcategoryForm, TicketApproveForm, TicketRejectForm, TicketTransferForm, DetailForm
from .mailer import send_ticket_mail
from django.utils import timezone
from registration.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from tickit import settings
from django.test import Client

from registration.decorators import adminnotallowed, manager_required, viewer_required, admin_required, viewernotallowed
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Case, When, Value, IntegerField, F
from django.utils.http import url_has_allowed_host_and_scheme

def work_note_update(request, ticket_id, field_name, old_value, new_value):
    work_note = Worknote()
    work_note.type = "Field"
    work_note.commented_by = request.user
    work_note.ticket = Ticket.objects.get(id=ticket_id)
    work_note.field_name = field_name
    work_note.old_value = old_value
    work_note.new_value = new_value
    work_note.save()

@login_required
@viewer_required
def ticket_create(request):
    context = {}
    form = TicketForm()
    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.status = "Pending"
            
            ticket.save()
            
            work_note = Worknote()
            work_note.ticket = ticket
            work_note.type = "Create"
            work_note.commented_by = request.user
            work_note.save()

            # Triage is the Admin's job, so every Admin needs to know a ticket
            # is waiting on them.
            for admin in User.objects.filter(role="Admin", is_active=True):
                notify(
                    admin,
                    f"{request.user.get_full_name()} raised {ticket.number} — awaiting triage",
                    kind="Assigned", ticket=ticket, actor=request.user,
                )
            
            messages.success(request, 'Your ticket has been created successfully.')
            
            send_ticket_mail(ticket, [request.user], 'New Ticket Generated',
                             'Your ticket has been created. An admin will review it and assign it.')

            return redirect('ticket_list')

    context['form'] = form
    return render(request, 'vats/ticket_create.html', context)

def role_scoped_tickets(user):
    """
    The one place role visibility is decided.

    Admin sees everything, Manager sees what is assigned to them, Viewer sees
    what they raised. Previously this branch was copy-pasted into several
    views, which is how visibility rules drift apart.
    """
    base = Ticket.objects.select_related('category', 'subcategory', 'created_by', 'assigned_to')
    if user.role == "Admin":
        return base.all()
    if user.role == "Manager":
        return base.filter(assigned_to=user)
    return base.filter(created_by=user)


def ticket_list_context(request, tickets, status=None, page_title=None, my_view=False):
    """
    Shared context builder for every screen that renders the ticket table:
    status counts for the filter pills, search, the stat strip, pagination.
    """
    search = (request.GET.get('q') or '').strip()
    if search:
        tickets = tickets.filter(
            Q(number__icontains=search)
            | Q(title__icontains=search)
            | Q(problem_descp__icontains=search)
        )

    # Counts come off the role-scoped set before status filtering, so the pills
    # show totals rather than "7" next to the status you already picked.
    scoped = role_scoped_tickets(request.user)
    raw_counts = dict(
        scoped.values_list('status').annotate(n=Count('id')).values_list('status', 'n')
    )
    # Django templates can't resolve a dict key containing a space, so
    # "In Progress" is exposed as "InProgress".
    counts = {(k or '').replace(' ', ''): v for k, v in raw_counts.items()}

    open_statuses   = ('Pending', 'Assigned', 'Scoping', 'In Progress')
    closed_statuses = ('Completed', 'Cancelled', 'Rejected')

    resolved = [t for t in scoped if t.resolution_time_hours is not None]
    responded = [t for t in scoped if t.first_response_time_hours is not None]
    total = scoped.count()
    closed = scoped.filter(status__in=closed_statuses).count()

    # What needs attention next comes first: tickets on the clock by deadline,
    # then untriaged ones longest-waiting first, then closed ones newest first.
    tickets = tickets.annotate(
        urgency=Case(
            When(status__in=closed_statuses, then=Value(2)),
            When(due_by__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).order_by(
        'urgency',
        Case(When(urgency=0, then=F('due_by'))),
        Case(When(urgency=1, then=F('created_at'))),
        '-created_at',
    )
    paginator = Paginator(tickets, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return {
        'tickets': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'status': status,
        'page_title': page_title,
        'my_view': my_view,
        'search': search,
        'status_counts': counts,
        'stats': {
            'unassigned':   scoped.filter(assigned_to__isnull=True).exclude(status__in=closed_statuses).count(),
            'breached':     sum(1 for t in scoped if t.is_sla_breached),
            'avg_response': round(sum(t.first_response_time_hours for t in responded) / len(responded), 1) if responded else None,
            'resolution_rate': round(closed / total * 100, 1) if total else None,
        },
    }


@login_required
def ticket_list(request):
    tickets = role_scoped_tickets(request.user)
    return render(request, 'vats/ticket_list.html', ticket_list_context(request, tickets))
    
@login_required
def notification_open(request, id):
    """
    Mark a notification read and go where it points.

    Read-on-click rather than read-on-view: opening the dropdown to look is
    not the same as having dealt with the thing.
    """
    notification = Notification.objects.filter(id=id, recipient=request.user).first()
    if not notification:
        messages.warning(request, 'That notification is not available.')
        return redirect('home')

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if notification.ticket_id:
        return redirect('ticket_detail', notification.ticket_id)
    return redirect('home')


@login_required
def notifications_mark_all_read(request):
    """Clear the badge in one go, returning the user to where they were."""
    updated = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    messages.success(request, f'{updated} notification(s) marked as read.')

    # Validate the referer before trusting it — an unchecked redirect back to
    # whatever the header says is an open-redirect vector.
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect('home')


@login_required
def my_tickets(request):
    """
    Personal actionable queue — distinct from the full role-wide table above.
    Admin   -> tickets waiting on their own approval decision
    Manager -> tickets assigned to them that are still open
    Viewer  -> tickets they raised that are still open
    """
    closed_statuses = ('Completed', 'Cancelled', 'Rejected')

    if request.user.role == "Admin":
        tickets = Ticket.objects.filter(status='Pending')
        title = 'My Tickets — Pending My Approval'
    else:
        tickets = role_scoped_tickets(request.user).exclude(status__in=closed_statuses)
        title = ('My Tickets — Still Open' if request.user.role == "Viewer"
                 else 'My Tickets — Open & Assigned to Me')

    return render(
        request, 'vats/ticket_list.html',
        ticket_list_context(request, tickets, page_title=title, my_view=True),
    )

@login_required
def ticket_bulk_action(request):
    """
    Shared bulk-action endpoint. Each role can only perform the bulk actions
    it already has permission to do one-at-a-time elsewhere in this file.
    """
    if request.method != 'POST':
        return redirect('ticket_list')

    ticket_ids  = request.POST.getlist('ticket_ids')
    bulk_action = request.POST.get('bulk_action')
    next_view   = request.POST.get('next')
    if next_view not in ('ticket_list', 'my_tickets'):
        next_view = 'ticket_list'

    tickets = Ticket.objects.filter(id__in=ticket_ids)

    if request.user.role == 'Admin' and bulk_action == 'reject':
        # Iterate rather than .update() — a queryset update bypasses
        # Ticket.save(), which is what stamps resolved_at. Using update() here
        # left bulk-rejected tickets with no resolution timestamp and silently
        # skewed the resolution-time metrics.
        count = 0
        for ticket in tickets.filter(status='Pending'):
            ticket.status = 'Rejected'
            ticket.save()
            work_note_update(request, ticket.id, "Status", "Pending", "Rejected")
            notify(
                ticket.created_by,
                f"{ticket.number} was rejected by {request.user.get_full_name()}",
                kind="Status", ticket=ticket, actor=request.user,
            )
            count += 1
        messages.success(request, f'{count} ticket(s) rejected.')

    elif request.user.role == 'Admin' and bulk_action == 'delete':
        count = tickets.count()
        tickets.delete()
        messages.success(request, f'{count} ticket(s) deleted.')

    elif request.user.role == 'Manager' and bulk_action == 'complete':
        count = 0
        for ticket in tickets.filter(assigned_to=request.user, status='In Progress'):
            ticket.status = 'Completed'
            ticket.save()
            work_note_update(request, ticket.id, "Status", "In Progress", "Completed")
            notify(
                ticket.created_by,
                f"{ticket.number} was completed by {request.user.get_full_name()}",
                kind="Status", ticket=ticket, actor=request.user,
            )
            count += 1
        messages.success(request, f'{count} ticket(s) marked Completed.')

    else:
        messages.warning(request, 'No valid bulk action was performed.')

    return redirect(next_view)

@login_required
def ticket_list_status(request, status):
    tickets = role_scoped_tickets(request.user).filter(status=status)
    return render(
        request, 'vats/ticket_list.html',
        ticket_list_context(request, tickets, status=status),
    )

@login_required
def ticket_detail(request, id):
    ticket = Ticket.objects.get(id=id)
    
    if request.method == "POST":
        print("Reached")
        work_note = Worknote()
        work_note.ticket = ticket
        work_note.comment = request.POST['work_note']
        work_note.commented_by = request.user
        work_note.type = "Comment"
        work_note.save()

        # Tell the other side of the conversation. notify() drops the case
        # where the commenter is the recipient, so nobody is told about their
        # own note.
        snippet = work_note.comment[:60] + ("…" if len(work_note.comment) > 60 else "")
        for person in (ticket.created_by, ticket.assigned_to):
            notify(
                person,
                f"{request.user.get_full_name()} commented on {ticket.number}: {snippet}",
                kind="Comment", ticket=ticket, actor=request.user,
            )
        
    user = User.objects.get(email=ticket.created_by)
    if ticket.created_by == request.user or request.user.role == "Admin" or ticket.assigned_to == request.user  :
        my_string = "https://wa.me/91" + str(ticket.created_by.phone_number)
        
        context = {'ticket' : ticket , 'user' : user, "my_string" : my_string}
        return render(request, 'vats/ticket_detail.html', context)
    
    else:
        messages.warning(request, 'You are not allowed to access this page.')
        return redirect('home')

@login_required
@admin_required
def ticket_approve(request, id):
    ticket = Ticket.objects.get(id=id)
    form = TicketApproveForm(instance=ticket)
    form.fields["assigned_to"].queryset = User.objects.filter(role='Manager')
    
    if request.method == 'POST':
        form = TicketApproveForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.status = "Assigned"
            if not ticket.assigned_at:
                ticket.assigned_at = timezone.now()
            ticket.save()
            
            work_note_update(request, id, "Status", "Pending", "Assigned")
            work_note_update(request, id, "Assigned to", "None", ticket.assigned_to.first_name + " " + ticket.assigned_to.last_name)
            work_note_update(request, id, "Priority", "None", ticket.priority)

            notify(
                ticket.assigned_to,
                f"{request.user.get_full_name()} assigned you {ticket.number} ({ticket.priority} priority)",
                kind="Assigned", ticket=ticket, actor=request.user,
            )
            notify(
                ticket.created_by,
                f"{ticket.number} was approved and assigned to {ticket.assigned_to.get_full_name()}",
                kind="Status", ticket=ticket, actor=request.user,
            )
            send_ticket_mail(ticket, [ticket.assigned_to], 'Ticket assigned to you',
                             f"{request.user.get_full_name()} assigned you this ticket with {ticket.priority} priority.")
            send_ticket_mail(ticket, [ticket.created_by], 'Your ticket has been assigned',
                             f"Your ticket is now with {ticket.assigned_to.get_full_name()}, who will work on it.")
            
            return redirect('ticket_list')
    
    context = {}
    context['form'] = form
    context['update_type'] = "Assign"
    return render(request, "vats/ticket_update.html", context)

# @login_required
# @admin_required
# def ticket_reject(request, id):
#     ticket = Ticket.objects.get(id=id)
#     # form = TicketRejectForm(instance=ticket)
#     ticket.status == "Rejected"
#     ticket.save()
#     # context = {}
#     # context['form'] = form
#     # context['update_type'] = "Reject"
#     messages.success(request, 'Ticket rejected successfully.')
            
#     # html_message = render_to_string('vats/email_template.html')
#     message = EmailMessage('Your tickit has been rejected due to lack of information. Kindly provide more information in detail if your problem is still not', request.user.email, ticket.created_by)
#     message.content_subtype = 'html'
#     return render(request, "vats/ticket_list.html")

@login_required
@admin_required
def ticket_reject(request,id):
    ticket = Ticket.objects.get(id=id)
    old_status = ticket.status
    ticket.status = "Rejected"
    ticket.save()
    work_note_update(request, id, "Status", old_status, "Rejected")
    notify(
        ticket.created_by,
        f"{ticket.number} was rejected by {request.user.get_full_name()}",
        kind="Status", ticket=ticket, actor=request.user,
    )
    send_ticket_mail(ticket, [ticket.created_by], 'Your ticket was rejected',
                     'An admin reviewed your ticket and rejected it. Raise a new one with more detail if you still need help.')
    messages.success(request, 'Ticket rejected successfully.')
        
    return redirect("ticket_detail",id)

@login_required
@manager_required
def status_change_email_function(request,id):
    ticket = Ticket.objects.get(id=id)
    ticket.save()
    messages.success(request, 'Your ticket status has changed successfully.')

    # Shared path for Scoping / In Progress / Completed, so the requester gets
    # told about every move without duplicating this in three views.
    notify(
        ticket.created_by,
        f"{ticket.number} moved to {ticket.status}",
        kind="Status", ticket=ticket, actor=request.user,
    )
            
    send_ticket_mail(ticket, [ticket.created_by], f'Ticket status updated: {ticket.status}',
                     f"{request.user.get_full_name()} moved your ticket to {ticket.status}.")
    return (redirect('ticket_list'))


@login_required
@manager_required
def ticket_scoping(request, id):
    ticket = Ticket.objects.get(id=id)
    ticket.status = 'Scoping'
    ticket.save()
    work_note_update(request, id, "Status", "Assigned", "Scoping")
    return status_change_email_function(request, id)

@login_required
@manager_required
def ticket_inprogress(request, id):
    ticket = Ticket.objects.get(id=id)
    ticket.status = 'In Progress'
    ticket.save()
    work_note_update(request, id, "Status", "Scoping", "In Progress")
    return status_change_email_function(request, id)

@login_required
@viewernotallowed
def ticket_update(request, id):

    ticket = Ticket.objects.get(id=id)
    if request.user.role == "Manager" and ticket.assigned_to != request.user:
        messages.warning(request, 'Only the person a ticket is assigned to can edit it.')
        return redirect('home')
    ticket_old_priority = ticket.priority
    ticket_old_assigned_to = ticket.assigned_to

    form = TicketUpdateForm(instance=ticket)
    form.fields["assigned_to"].queryset = User.objects.filter(role='Manager')
    
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            ticket.save()
            
            if ticket_old_priority !=ticket.priority:
                work_note_update(request, id, "Priority", ticket_old_priority, ticket.priority)
            if ticket_old_assigned_to != ticket.assigned_to:
                record_transfer(request, ticket, ticket_old_assigned_to)

            return redirect('ticket_list')
    
    context = {}
    context['form'] = form
    context['update_type'] = 'Update'
    return render(request, "vats/ticket_update.html", context)

def record_transfer(request, ticket, previous, reason=''):
    """History, notifications and emails for a ticket changing hands."""
    old_name = previous.get_full_name() if previous else "None"
    work_note_update(request, ticket.id, "Assigned to", old_name, ticket.assigned_to.get_full_name())
    if reason:
        Worknote.objects.create(ticket=ticket, type="Comment", commented_by=request.user,
                                comment=f"Transfer reason: {reason}")
    notify(ticket.assigned_to, f"{request.user.get_full_name()} transferred {ticket.number} to you",
           kind="Assigned", ticket=ticket, actor=request.user)
    notify(previous, f"{ticket.number} was transferred to {ticket.assigned_to.get_full_name()}",
           kind="Assigned", ticket=ticket, actor=request.user)
    why = f" Reason: {reason}" if reason else ""
    send_ticket_mail(ticket, [ticket.assigned_to], 'Ticket transferred to you',
                     f"{request.user.get_full_name()} transferred this ticket to you.{why}")
    send_ticket_mail(ticket, [ticket.created_by], 'Your ticket has a new owner',
                     f"Your ticket is now with {ticket.assigned_to.get_full_name()}.")


@login_required
def ticket_transfer(request, id):
    """
    Hand a ticket to another Manager. Only the person it is assigned to, or
    an Admin, may do it. Afterwards it leaves the previous person's queue:
    responsibility moves with the ticket.
    """
    ticket = Ticket.objects.get(id=id)
    allowed = request.user.role == "Admin" or (request.user.role == "Manager" and ticket.assigned_to == request.user)
    if not allowed or ticket.status not in ("Assigned", "Scoping", "In Progress"):
        messages.warning(request, 'This ticket cannot be transferred by you right now.')
        return redirect('home')

    form = TicketTransferForm(request.POST or None, ticket=ticket)
    if request.method == "POST" and form.is_valid():
        previous = ticket.assigned_to
        ticket.assigned_to = form.cleaned_data['assigned_to']
        ticket.save()
        record_transfer(request, ticket, previous, form.cleaned_data['reason'].strip())
        messages.success(request, f'{ticket.number} transferred to {ticket.assigned_to.get_full_name()}.')
        return redirect('ticket_detail', id) if request.user.role == "Admin" else redirect('ticket_list')
    return render(request, 'vats/ticket_transfer.html', {'form': form, 'ticket': ticket})


@login_required
@admin_required
def inbound_list(request):
    """Emails to the support mailbox that are waiting for an Admin's decision."""
    return render(request, 'vats/inbound_list.html', {
        'held': InboundEmail.objects.filter(status='Held'),
    })


@login_required
@admin_required
def inbound_decide(request, id):
    if request.method != 'POST':
        return redirect('inbound_list')
    held = InboundEmail.objects.filter(id=id, status='Held').first()
    if not held:
        return redirect('inbound_list')

    if request.POST.get('decision') == 'accept':
        from .inbound import create_ticket_from_email
        user = User.objects.filter(email__iexact=held.sender).first()
        if not user:
            # A new requester: an Employee account they can claim with "Forgot password".
            name = (held.sender_name or held.sender.split('@')[0]).split()
            user = User.objects.create_user(name[0][:30], ' '.join(name[1:])[:30], held.sender, None)
            user.role = 'Viewer'
            user.save()
        held.ticket = create_ticket_from_email(user, held.subject, held.body)
        held.status = 'Accepted'
        held.save()
        messages.success(request, f'{held.ticket.number} created for {held.sender}.')
        return redirect('ticket_detail', held.ticket.id)

    held.status = 'Dismissed'
    held.save()
    messages.success(request, f'Email from {held.sender} dismissed.')
    return redirect('inbound_list')


@login_required
@admin_required
def detail_list(request, id):
    subcategory = Subcategory.objects.get(id=id)
    return render(request, 'vats/detail_list.html', {
        'subcategory': subcategory, 'details': Detail.objects.filter(subcategory=subcategory),
        'form': DetailForm(),
    })


@login_required
@admin_required
def detail_create(request, id):
    subcategory = Subcategory.objects.get(id=id)
    form = DetailForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        detail = form.save(commit=False)
        detail.subcategory = subcategory
        detail.save()
        messages.success(request, f'{detail.name} added under {subcategory.name}.')
    return redirect('detail_list', id)


@login_required
@admin_required
def detail_delete(request, id):
    detail = Detail.objects.get(id=id)
    subcategory_id = detail.subcategory_id
    detail.delete()
    return redirect('detail_list', subcategory_id)


def load_details(request):
    details = Detail.objects.filter(subcategory_id=request.GET.get('subcategory') or None)
    return render(request, 'vats/detail_dropdown_list_options.html', {'details': details})


@login_required
def ticket_rate(request, id):
    ticket = Ticket.objects.get(id=id)

    if ticket.created_by != request.user:
        messages.warning(request, 'You are not allowed to rate this ticket.')
        return redirect('ticket_detail', id)

    if ticket.status != 'Completed':
        messages.warning(request, 'You can only rate a ticket once it is Completed.')
        return redirect('ticket_detail', id)

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('csat_rating'))
        except (TypeError, ValueError):
            rating = None

        if rating in (1, 2, 3, 4, 5):
            ticket.csat_rating = rating
            ticket.csat_feedback = request.POST.get('csat_feedback', '').strip()
            ticket.save()
            messages.success(request, 'Thanks for rating your support experience!')
        else:
            messages.warning(request, 'Please select a rating between 1 and 5.')

    return redirect('ticket_detail', id)

@login_required
@admin_required
def ticket_delete(request, id):
    ticket = Ticket.objects.get(id=id)
    ticket.delete()
    return redirect('ticket_list')

@login_required
@manager_required
def ticket_completed(request,id):
    ticket = Ticket.objects.get(id=id)
    ticket.status = "Completed"
    ticket.save()
    work_note_update(request, id, "Status", "In Progress", "Completed")
    return status_change_email_function(request, id)

@login_required
@adminnotallowed
def ticket_cancel(request,id):
    ticket = Ticket.objects.get(id=id)
    ticket_old_status = ticket.status
    ticket.status = "Cancelled"
    ticket.save()
    work_note_update(request, id, "Status", ticket_old_status, "Cancelled")
    # Whoever was working it needs to know to stop
    notify(
        ticket.assigned_to,
        f"{ticket.number} was cancelled by {request.user.get_full_name()}",
        kind="Status", ticket=ticket, actor=request.user,
    )
    send_ticket_mail(ticket, [p for p in (ticket.created_by, ticket.assigned_to) if p and p != request.user],
                     'Ticket cancelled', f"{request.user.get_full_name()} cancelled this ticket.")
    return redirect('ticket_detail',id)



##########################################################  CATEGORY VIEWS  ##########################################################
@login_required
@admin_required
def category_create(request):
    context = {}
    form = CategoryForm()

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()                     
            messages.success(request, 'Your Category has been created successfully.')
            return redirect('category_list')

    context['form'] = form
    return render(request, 'vats/category_create.html', context)

@login_required
@admin_required
def category_list(request):
    context = {}
    context['categories'] = Category.objects.all()
    return render(request, 'vats/category_list.html', context)

@login_required
@admin_required
def category_delete(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('category_list')

######################################################### SUBCATEGORY VIEWS  #########################################################
@login_required
@admin_required
def subcategory_create(request, id):
    context = {}
    category = Category.objects.get(id=id)
    form = SubcategoryForm()
    form.fields['category'].initial = id

    if request.method == "POST":
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()                     
            messages.success(request, 'Your Subcategory has been created successfully.')
            return redirect('subcategory_list', id)

    context['form'] = form
    return render(request, 'vats/subcategory_create.html', context)

@login_required
@admin_required
def subcategory_list(request, id):
    context = {}
    category = Category.objects.get(id=id)
    context['category'] = category
    context['subcategories'] = Subcategory.objects.filter(category=category)
    return render(request, 'vats/subcategory_list.html', context)

@login_required
@admin_required
def subcategory_delete(request, id):
    subcategory = Subcategory.objects.get(id=id)
    category_id = subcategory.category_id
    subcategory.delete()
    # Back to the list it was deleted from. The route needs the category id;
    # redirecting without it raised NoReverseMatch after every delete.
    return redirect('subcategory_list', category_id)




# @login_required
# @manager_required
# def worknotes_create(request,id):
#     context = {}
#     form = WorkNotesForm()

#     if request.method == "POST":
#         form = WorkNotesForm(request.POST)
#         if form.is_valid():
#             worknotes = form.save(commit=False)
#             worknotes.commented_by = request.user
            
#             worknotes.save()                     
#             messages.success(request, 'Your comment for cancellation of ticket has been created successfully.')
#             return redirect('ticket_list')

    # context['form'] = form
    # return render(request, 'vats/worknotes_create.html', context)

def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = Subcategory.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'vats/subcategory_dropdown_list_options.html', {'subcategories': subcategories})