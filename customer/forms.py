from django import forms
from django.conf import settings

from myproject.location.forms import LocationForm
from myproject.customer.models import ContactInfo

# These are forms to deal with changing profiles, etc.

class ContactInfoForm(LocationForm):
    class Meta(LocationForm.Meta):
        model = ContactInfo

    class Media(LocationForm.Media):
        pass
