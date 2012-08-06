from django.shortcuts import render
from django.http import Http404

from myproject.fishing.models import FishingCore

# Create your views here.

def showProfile(request, id, name, template='fishing/profile/public.html'):
    try:
        id = int(id)
        guide = FishingCore.objects.select_related('person',
                                                   'profile',
                                                   'person__profile',
                                                   'waterbodies',
                                                   'fish',
                                                   'locations',
                                                   'methods',
                                                   'PartyModel',
                                                   'PaymentModels',
                                                   'Fans',
                                                   'FAQ', 'ExtraDetails').get(person__id=id)
    except:
        raise Http404
    return render(request, template, { 'guide':guide })
