from django import forms
from .models import Ticket, Category, Subcategory

class TicketForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("category", "subcategory", "title","problem_descp")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TicketApproveForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ("priority", "assigned_to")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].required = True
        self.fields['assigned_to'].required = True

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

class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = ("name",)
        
class SubcategoryForm(forms.ModelForm):
    
    class Meta:
        model = Subcategory
        fields = ("category", "name")
