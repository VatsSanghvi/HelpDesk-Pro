from django import forms
from registration.models import User
from .models import Ticket, Category, Subcategory, Detail


def _person_label(user):
    """People are chosen by name; the model's own label is the email address."""
    return user.get_full_name() or user.email


def _name_choices(form):
    """Readable placeholders and labels for the priority and people dropdowns."""
    if 'priority' in form.fields:
        form.fields['priority'].choices = [('', 'Choose a priority')] + list(Ticket.priority_choice)
        form.fields['priority'].error_messages['required'] = 'Choose a priority.'
    if 'assigned_to' in form.fields:
        form.fields['assigned_to'].empty_label = 'Choose a manager'
        form.fields['assigned_to'].label_from_instance = _person_label
        form.fields['assigned_to'].error_messages['required'] = 'Choose a manager.'
    if 'created_by' in form.fields:
        form.fields['created_by'].label_from_instance = _person_label

class TicketForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("category", "subcategory", "detail", "title","problem_descp")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional in the database (emailed tickets), required on the form.
        self.fields['category'].required = True
        self.fields['subcategory'].required = True
        self.fields['detail'].required = False
        self.fields['detail'].empty_label = 'None'
        self.fields['category'].empty_label = 'Choose a category'
        self.fields['subcategory'].empty_label = 'Choose a subcategory'
        self.fields['category'].error_messages['required'] = 'Choose a category.'
        self.fields['subcategory'].error_messages['required'] = 'Choose a subcategory.'
        self.fields['title'].error_messages['required'] = 'Give the ticket a short title.'
        self.fields['problem_descp'].error_messages['required'] = 'Describe the problem so IT can act on it.'

class TicketApproveForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("category", "subcategory", "detail", "priority", "assigned_to")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Triage is where an emailed ticket gets its category, and where a
        # wrong one can be corrected.
        self.fields['category'].required = True
        self.fields['subcategory'].required = True
        self.fields['category'].empty_label = 'Choose a category'
        self.fields['subcategory'].empty_label = 'Choose a subcategory'
        self.fields['detail'].required = False
        self.fields['detail'].empty_label = 'None'
        self.fields['category'].error_messages['required'] = 'Choose a category.'
        self.fields['subcategory'].error_messages['required'] = 'Choose a subcategory.'
        self.fields['priority'].required = True
        self.fields['assigned_to'].required = True
        _name_choices(self)

class TicketRejectForm(forms.ModelForm):
    
    comments = forms.CharField(widget=forms.Textarea, max_length=150, required=True)
    
    class Meta:
        model = Ticket
        fields = ("priority",)
    
class TicketUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("category","subcategory", "detail", "title","problem_descp","created_by","status","assigned_to","priority")
    
    def __init__(self, *args, **kwargs):
        super(TicketUpdateForm,self).__init__(*args, **kwargs)
        self.fields['category'].disabled = True
        self.fields['subcategory'].disabled = True
        self.fields['detail'].disabled = True
        self.fields['title'].disabled = True
        self.fields['problem_descp'].disabled = True
        self.fields['created_by'].disabled = True
        self.fields['status'].disabled = True
        self.fields['assigned_to'].required = True
        self.fields['priority'].required = True
        _name_choices(self)

class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = ("name",)
        
class SubcategoryForm(forms.ModelForm):
    
    class Meta:
        model = Subcategory
        fields = ("category", "name")


class TicketTransferForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        label="Transfer to", queryset=User.objects.none(), empty_label="Choose a manager",
        error_messages={'required': 'Choose who takes the ticket.'},
    )
    reason = forms.CharField(
        label="Reason (optional)", required=False, max_length=300,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, ticket=None, **kwargs):
        super().__init__(*args, **kwargs)
        managers = User.objects.filter(role='Manager', is_active=True)
        if ticket and ticket.assigned_to_id:
            managers = managers.exclude(pk=ticket.assigned_to_id)
        self.fields['assigned_to'].queryset = managers
        self.fields['assigned_to'].label_from_instance = _person_label


class DetailForm(forms.ModelForm):

    class Meta:
        model = Detail
        fields = ("name",)
