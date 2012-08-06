from django import forms
from django.conf import settings

# These are generic forms for The Site

class ContactUsForm(forms.Form):
    name = forms.CharField(max_length=100, min_length=1)
    email = forms.EmailField()
    message = forms.CharField(min_length=10, widget=forms.Textarea)

class SearchForm(forms.Form):
    loc = forms.CharField(max_length=300, initial=settings.FISHING_INITIAL_WELCOME)
    lat = forms.CharField(widget=forms.HiddenInput)
    lng = forms.CharField(widget=forms.HiddenInput)

    class Media:
        js = (settings.JS_URL + 'geocode.js',)
