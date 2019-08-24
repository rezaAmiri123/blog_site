from django import forms
from django.contrib.auth import get_user_model
from .helpers import DateInput

User = get_user_model()


class SearchForm(forms.Form):
    query = forms.CharField(label="Full-text Search Query", required=False)
    title = forms.CharField(label='Title', required=False)
    body = forms.CharField(label='body', widget=forms.Textarea(), required=False)
    users = forms.ModelMultipleChoiceField(
        label='Users',
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    created_from = forms.DateField(
        label='Created from',
        required=False,
        widget=DateInput(),
    )
    created_till = forms.DateField(
        label='Created till',
        required=False,
        widget=DateInput(),
    )
