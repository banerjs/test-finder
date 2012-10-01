from django import forms
from django.conf import settings

from myproject.location.models import BaseLocation, WaterBody

# The following forms are for users to modify and add locations to the Database

class BaseLocationForm(forms.ModelForm):
    type = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = BaseLocation
        widgets = { 'lat': forms.HiddenInput,
                    'lng': forms.HiddenInput, }

    class Media:
        js = ( 'https://maps.googleapis.com/maps/api/js?key='+settings.GOOGLE_API_KEY+'&sensor=false&libraries=places',
               settings.DYNAMIC_JS_URL + 'location_baselocation/geocode.js', )

class BaseLocationFormAdmin(BaseLocationForm):

    class Meta(BaseLocationForm.Meta):
        fields = ('country', 'state', 'city', 'lat', 'lng')
        widgets = { 'lat': forms.TextInput,
                    'lng': forms.TextInput, }

    class Media(BaseLocationForm.Media):
        pass

class WaterBodyForm(forms.ModelForm):
    pass

# Definition of BaseLocationForm as an inherited form from GeocodeForm. Cannot use this due to
# Admin site requirements
# class BaseLocationForm(GeocodeForm):
#     city = forms.CharField(label='Location', widget=forms.TextInput(attrs={ 'size': '40' }))
#     state = forms.CharField(label='State', required=False)
#     country = forms.ChoiceField(choices=COUNTRIES_TWO)

#     class Media(GeocodeForm.Media):
#         js = (settings.DYNAMIC_JS_URL + 'location_baselocation/geocode.js', )

#     def clean(self, *args, **kwargs):
#         cleaned_data = self.cleaned_data
#         if kwargs.get('save'):
#             try:
#                 self.save()
#             except:
#                 raise forms.ValidationError('Form cannot be saved')
#         return cleaned_data

#     def save(self, *args, **kwargs):
#         base = BaseLocation(city=self.cleaned_data.get('city'),
#                             state=self.cleaned_data.get('state'),
#                             lat=self.cleaned_data.get('lat'),
#                             lng=self.cleaned_data.get('lng'))
#         try:
#             country = Country.objects.get(pk=self.cleaned_data.get('country'))
#         except:
#             raise forms.ValidationError('Invalid Country')
#         base.country = country
#         base.save(*args, **kwargs)
