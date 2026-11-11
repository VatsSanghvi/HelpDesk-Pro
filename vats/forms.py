from django import forms
from .models import Ticket, Category, Subcategory


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
        fields = ("category", "subcategory", "title","problem_descp")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Choose a category'
        self.fields['subcategory'].empty_label = 'Choose a subcategory'
        self.fields['category'].error_messages['required'] = 'Choose a category.'
        self.fields['subcategory'].error_messages['required'] = 'Choose a subcategory.'
        self.fields['title'].error_messages['required'] = 'Give the ticket a short title.'
        self.fields['problem_descp'].error_messages['required'] = 'Describe the problem so IT can act on it.'

class TicketApproveForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("priority", "assigned_to")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        fields = ("category","subcategory", "title","problem_descp","created_by","status","assigned_to","priority")
    
    def __init__(self, *args, **kwargs):
        super(TicketUpdateForm,self).__init__(*args, **kwargs)
        self.fields['category'].disabled = True
        self.fields['subcategory'].disabled = True
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
