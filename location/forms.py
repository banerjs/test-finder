from django import forms
from django.conf import settings

from myproject.location.models import BaseLocation, WaterBody

# The following forms are for users to modify and add locations to the Database

class LocationForm(forms.ModelForm): # Do NOT under any circumstance use this on it's own
    class Meta:
        widgets = { 'lat': forms.HiddenInput,
                    'lng': forms.HiddenInput }

    class Media:
        js = (settings.JS_URL + 'geocode.js',)

class BaseLocationForm(LocationForm):
    class Meta(LocationForm.Meta):
        model = BaseLocation

    class Media(LocationForm.Media):
        pass

class WaterBodyForm(LocationForm):
    class Meta(LocationForm.Meta):
        model = WaterBody

    class Media(LocationForm.Media):
        pass
