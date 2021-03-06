from django import forms
from django.conf import settings

# Custom Widget to name form fields

def NamedWidget(input_name, widget=forms.TextInput, **kwargs):
    if isinstance(widget, type):
        widget = widget()

    render = widget.render
    widget.render = lambda name, value, attrs=None: \
                    render(input_name, value, attrs)

    return widget

# These are generic forms for The Site

class ContactUsForm(forms.Form):
    name = forms.CharField(max_length=100, min_length=1)
    email = forms.EmailField()
    message = forms.CharField(min_length=10, widget=forms.Textarea)

class GeocodeForm(forms.Form):
    lat = forms.FloatField(widget=forms.HiddenInput, required=False)
    lng = forms.FloatField(widget=forms.HiddenInput, required=False)
    type = forms.CharField(widget=forms.HiddenInput, required=False)

    class Media:
        js = ( 'https://maps.googleapis.com/maps/api/js?key='+settings.GOOGLE_API_KEY+'&sensor=false&libraries=places', )
