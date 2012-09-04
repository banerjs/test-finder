from django import forms
from django.conf import settings

from myproject.location.models import BaseLocation, WaterBody

# The following forms are for users to modify and add locations to the Database

class LocationForm(forms.Form):
    lat = forms.FloatField(widget=forms.HiddenInput, required=False)
    lng = forms.FloatField(widget=forms.HiddenInput, required=False)
    type = forms.CharField(widget=forms.HiddenInput, required=False)
    input = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))

    class Media:
        js = ('https://maps.googleapis.com/maps/api/js?key='+settings.GOOGLE_API_KEY+'&sensor=false&libraries=places',
              settings.JS_URL + 'geocode.js', )
