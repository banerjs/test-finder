from datetime import datetime, timedelta

from django import forms
from django.conf import settings

from myproject.forms import NamedWidget, GeocodeForm

# The following are the forms used by django for everything in the fishing module

class SearchForm(GeocodeForm):
    loc = forms.CharField(label="Location", widget=forms.TextInput(attrs={ 'size': '40',
                                                                           'placeholder': settings.FISHING_INITIAL_WELCOME }))
    date = forms.DateField(required=False)

    class Media(GeocodeForm.Media):
        js = (settings.DYNAMIC_JS_URL + 'fishing_search/geocode.js', )
 
    def clean(self):
        cleaned_data = self.cleaned_data
        location = cleaned_data.get('loc')
        date = cleaned_data.get('date')

        if not location or (settings.FISHING_INITIAL_WELCOME in location):
            self.cleaned_data['loc'] = ''
            raise forms.ValidationError("Empty Location Detected!")

        if not date:
            date = datetime.today()+timedelta(1)
            cleaned_data['date'] = date

        return cleaned_data
