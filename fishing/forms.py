from django import forms
from django.conf import settings

from myproject.forms import NamedWidget
from myproject.location.forms import LocationForm

# The following are the forms used by django for everything in the fishing module

class SearchForm(LocationForm):
    input = forms.CharField(widget=NamedWidget('loc', forms.TextInput(attrs={'size':'40'})))
    date = forms.DateField(required=False)

    class Media(LocationForm.Media):
        pass
