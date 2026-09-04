from dataclasses import field
from django.urls import reverse
import importlib
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import  Ticket, Category, Subcategory, Worknote
from .forms import TicketForm, CategoryForm, TicketUpdateForm, SubcategoryForm, TicketApproveForm, TicketRejectForm
from registration.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from tickit import settings
from django.test import Client

from registration.decorators import adminnotallowed, manager_required, viewer_required, admin_required, viewernotallowed
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            
            messages.success(request, 'Your tickit has been created successfully.')
            
            html_message = render_to_string('vats/email_template.html', {'context': ticket})
            message = EmailMessage('New Ticket Generated', html_message, settings.EMAIL_HOST_USER, [request.user.email])
            message.content_subtype = 'html'
            try:
                message.send()
            except Exception as e:
                print("Error",e)
        
            return redirect('ticket_list')

    context['form'] = form
    return render(request, 'vats/ticket_create.html', context)

@login_required
def ticket_list(request):
    context = {}
    if request.user.role == "Admin":
        context['tickets'] = Ticket.objects.all()
    elif request.user.role == "Viewer":
        context['tickets'] = Ticket.objects.filter(created_by = request.user)
    else :
        request.user.role == "Manager"
        context['tickets'] = Ticket.objects.filter(assigned_to=request.user)
    return render(request, 'vats/ticket_list.html', context)
    
@login_required
def my_tickets(request):
    """
    Personal actionable queue — distinct from the full role-wide table above.
    Admin   -> tickets waiting on their own approval decision
    Manager -> tickets assigned to them that are still open
    Viewer  -> tickets they raised that are still open
    """
    context = {}
    closed_statuses = ('Completed', 'Cancelled', 'Rejected')

    if request.user.role == "Admin":
        context['tickets'] = Ticket.objects.filter(status='Pending')
        context['page_title'] = 'My Tickets — Pending My Approval'
    elif request.user.role == "Viewer":
        context['tickets'] = Ticket.objects.filter(
            created_by=request.user
        ).exclude(status__in=closed_statuses)
        context['page_title'] = 'My Tickets — Still Open'
    else:
        context['tickets'] = Ticket.objects.filter(
            assigned_to=request.user
        ).exclude(status__in=closed_statuses)
        context['page_title'] = 'My Tickets — Open & Assigned to Me'

    context['my_view'] = True
    return render(request, 'vats/ticket_list.html', context)

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
        count = tickets.filter(status='Pending').update(status='Rejected')
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
            count += 1
        messages.success(request, f'{count} ticket(s) marked Completed.')

    else:
        messages.warning(request, 'No valid bulk action was performed.')

    return redirect(next_view)

@login_required
def ticket_list_status(request, status):
    context = {}
    context['status'] = status
    if request.user.role == "Admin":
        context['tickets'] = Ticket.objects.filter(status=status)
    elif request.user.role == "Viewer":
        context['tickets'] = Ticket.objects.filter(created_by=request.user , status=status)
    else :
        request.user.role == "Manager"
        context['tickets'] = Ticket.objects.filter(assigned_to=request.user, status=status)

    return render(request, 'vats/ticket_list.html', context)

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
            ticket.save()
            
            work_note_update(request, id, "Status", "Pending", "Assigned")
            work_note_update(request, id, "Assigned to", "None", ticket.assigned_to.first_name + " " + ticket.assigned_to.last_name)
            work_note_update(request, id, "Priority", "None", ticket.priority)
            
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
    ticket.status = "Rejected"
    ticket.save()
    messages.success(request, 'Ticket rejected successfully.')
        
    return redirect("ticket_detail",id)

@login_required
@manager_required
def status_change_email_function(request,id):
    ticket = Ticket.objects.get(id=id)
    ticket.save()
    messages.success(request, 'Your tickit status has changed successfully.')
            
    html_message = render_to_string('vats/status_change_email_template.html', {'context': ticket})
    message = EmailMessage('Ticket status updated', html_message, settings.EMAIL_HOST_USER, [ticket.created_by])
    message.content_subtype = 'html'
   
    try:
        message.send()
    except Exception as e:
        print("Error",e)
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
            if ticket_old_assigned_to.email != ticket.assigned_to.email:
                work_note_update(request, id, "Assigned to", ticket_old_assigned_to.first_name + " " + ticket_old_assigned_to.last_name, ticket.assigned_to.first_name + " " + ticket.assigned_to.last_name)
            
            return redirect('ticket_list')
    
    context = {}
    context['form'] = form
    context['update_type'] = 'Update'
    return render(request, "vats/ticket_update.html", context)

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
            messages.success(request, 'Your Subategory has been created successfully.')
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
    subcategory.delete()
    return redirect('subcategory_list')




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