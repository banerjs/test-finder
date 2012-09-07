import re
from datetime import datetime, timedelta

from django.db.models import Q, F, Max, Min
from django.contrib.localflavor.us import us_states
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, QueryDict
from django.shortcuts import render_to_response, render, redirect
from django.conf import settings

from myproject.custom import GoogleLatLng
from myproject.location.models import BaseLocation, WaterBody
from myproject.fishing.models import FishingCore, Fish, FishingType
from myproject.fishing.forms import SearchForm

# Create your views here.

def searchHome(request, template_name='fishing/search/search.html', **kwargs):
    form = SearchForm(auto_id='geocode_%s')
    return render(request, template_name, { 'form':form })

def locQuery(location, **kwargs):
    query = FishingCore.objects.none()
    lat = kwargs.get('lat')
    lng = kwargs.get('lng')
    rad = kwargs.get('radius', 20)
    if not lat or not lng:
        return query
    lat = float(lat)
    lng = float(lng)
    rad = float(rad)
    # Might not need the following code
    #query = FishingCore.objects.filter(Q(locations__city__iexact=location) |
    #                                   Q(locations__state__iexact=location) |
    #                                   Q(locations__country__name__iexact=location) |
    #                                   Q(locations__country__abbr__iexact=location) |
    #                                   Q(locations__country__abbr3__iexact=location) |
    #                                   Q(waterbodies__name__iexact=location))
    loc = BaseLocation.neighbours.nearby_locations(lat, lng, rad, True).select_related('FishingGuides')
    water = WaterBody.neighbours.nearby_locations(lat, lng, rad, True).select_related('FishingGuides')
    for l in loc:
        query = query | FishingCore.objects.filter(locations=l)
    for w in water:
        query = query | FishingCore.objects.filter(waterbodies=w)
    if not settings.USE_TEST_GUIDES: # If "do not use test guides"
        query = query.exclude(person__user__is_active=False)
    return query

def datQuery(query, date):
    """
    Search for date might take too long. Can be optimized, and should be with location
    """
    return query

def fisQuery(query, **kwargs):
    fish = kwargs.get('fish')
    watertype = kwargs.get('watertype')
    method = kwargs.get('method')
    if fish:
        query = query.filter(Q(fish__name__icontains=fish) |
                             Q(fish__type__icontains=fish) |
                             Q(fish__alternate_name_1__icontains=fish) |
                             Q(fish__alternate_name_2__icontains=fish) |
                             Q(fish__alternate_name_3__icontains=fish))
    if watertype:
        query = query.filter(fish__water_type__iexact=watertype)
    if method:
        query = query.filter(methods__method__icontains=method)
    return query

def groQuery(query, **kwargs):
    boatsize = int(kwargs.get('boatsize', 0))
    partysize = int(kwargs.get('partysize', 0))
    if boatsize:
        query = query.annotate(max_boat=Max('boats__boat_length')).exclude(max_boat__lt=int(boatsize))
        query = query.annotate(min_boat=Min('boats__boat_length')).exclude(min_boat__gt=int(boatsize))
    if partysize:
        query = query.filter(PartyModel__max_party__gte=partysize, PartyModel__min_party__lte=partysize)
    return query

def priQuery(query, **kwargs):
    maxprice = float(kwargs.get('maxprice', 99999999.99))
    query = query.filter(search_price__lte=maxprice)
    minprice = float(kwargs.get('minprice', 0))
    query = query.filter(search_price__gte=minprice)
    return query

def faqQuery(query, **kwargs):
    isnew = kwargs.get('isnew')
    cf = kwargs.get('child_friendly')
    al = kwargs.get('alcohol_allowed')
    fp = kwargs.get('food_provided')
    cr = kwargs.get('capture_release')
    sc = kwargs.get('state_certified')
    cg = kwargs.get('CG_certified')
    hf = kwargs.get('handicap_friendly')
    pe = kwargs.get('personal_equipment')
    lt = kwargs.get('lost_tackle')
    fs = kwargs.get('fillet_services')
    ts = kwargs.get('taxidermy_services')
    ai = kwargs.get('allow_international')
    if isnew:
        isnew = False if isnew == 'False' else True
        query = query.filter(is_new=isnew)
    if cf:
        cf = False if cf == 'False' else True
        query = query.filter(FAQ__child_friendly=cf)
    if al:
        al = False if al == 'False' else True
        query = query.filter(FAQ__alcohol_allowed=al)
    if fp:
        fp = False if fp == 'False' else True
        query = query.filter(FAQ__food_provided=fp)
    if cr:
        cr = False if cr == 'False' else True
        query = query.filter(FAQ__capture_release=cr)
    if sc:
        sc = False if sc == 'False' else True
        query = query.filter(FAQ__state_certified=sc)
    if cg:
        cg = False if cg == 'False' else True
        query = query.filter(FAQ__CG_certified=cg)
    if hf:
        hf = False if hf == 'False' else True
        query = query.filter(FAQ__handicap_friendly=hf)
    if pe:
        pe = False if pe == 'False' else True
        query = query.filter(FAQ__personal_equipment=pe)
    if lt:
        lt = False if lt == 'False' else True
        query = query.filter(FAQ__lost_tackle=lt)
    if fs:
        fs = False if fs == 'False' else True
        query = query.filter(FAQ__fillet_services=fs)
    if ts:
        ts = False if ts == 'False' else True
        query = query.filter(FAQ__taxidermy_services=ts)
    if ai:
        ai = False if ai == 'False' else True
        query = query.filter(FAQ__allow_international=ai)
    return query

def retQuery(location, day, **kwargs):
    query = locQuery(location, **kwargs)  # Filter based on Location
    if query.exists():
        query = datQuery(query, day)      # Filter based on Date
        query = fisQuery(query, **kwargs) # Filter based on Fish, WaterType and FishingMethod
        query = groQuery(query, **kwargs) # Filter based on BoatSize and Number of People
        query = priQuery(query, **kwargs) # Filter based on Price
        query = faqQuery(query, **kwargs) # Filter based on FAQ's (including new)
    return query.distinct()

def ordQuery(query, ordering):
    sort = ['full_day_price', '-profile__num_recommends', '-experience', 'person__first_name', 'person__last_name', '-PartyModel__avg_party']
    if not ordering or ordering == 'price':
        new_sort = sort
    if ordering == 'recommend':
        new_sort = list(sort.pop(1))
        new_sort.extend(sort)
    if ordering == 'experience':
        new_sort = list(sort.pop(2))
        new_sort.extend(sort)
    if ordering == 'alpha':
        new_sort = [sort.pop(3), sort.pop(4)]
        new_sort.extend(sort)
    if ordering == 'party' or ordering == 'boat':
        new_sort = list(sort.pop(5))
        new_sort.extend(sort)
        if ordering == 'boat':
            return query.annotate(max_length=Max('boats__boat_length')).order_by('-max_length', *new_sort)
    return query.order_by(*new_sort)

def parQuery(location, day, **kwargs):
    query = ordQuery(retQuery(location, day, **kwargs), kwargs.get('ordering'))
    return query

def searchDisplay(request, template_name='fishing/search/display.html', debug=False, disposable=False, **kwargs):
    # debug is for testSearch when debugging search from the shell
    # disp is for use by the disposable site only. Delete it in the production code
    request.GET = request.GET.copy()                  # Make the Dict mutable so that functions can act on it

    # This should be deleted:
    if disposable:
        s = request.GET.get('other')
        if s:
            q = QueryDict(s)
            request.GET.update(q)
    # End part that should be deleted

    form = SearchForm(request.GET, auto_id='geocode_%s')

    if form.is_valid():
        location = form.cleaned_data.get('loc')
        day = form.cleaned_data.get('date')
        
        if location == '':
            if debug:
                return ('NULL Location', [])
            if template_name == 'fishing/search/display.html':
                red = request.META.get('HTTP_REFERER', settings.DOMAIN)
                return redirect(request, red)
            else:
                return render(request, template_name, { 'guides_list':[] })
        # Get the remaining dictionary
        diction = dict(request.GET.items())
        # Process the search terms
        guides = parQuery(location, day, **diction)
        if debug:
            return ('Guides: ', guides)
        return render(request, template_name, { 'form': form, 'guides_list': list(guides)[:50] })
    else:
        red = request.META.get('HTTP_REFERER', settings.DOMAIN)
        return redirect(request, red)

def testSearch(**kwargs):
    req = HttpRequest()
    req.GET = kwargs
    return searchDisplay(req, debug=True, **kwargs)

def XMLfish(request):
    if request.method == 'GET':
        name = request.GET.get('fish', ' ')
        q = Fish.objects.filter(Q(type__istartswith=name) |
                                Q(name__istartswith=name) |
                                Q(alternate_name_1__istartswith=name) |
                                Q(alternate_name_2__istartswith=name) |
                                Q(alternate_name_3__istartswith=name)).order_by('type','name','alternate_name_1')
        message = ""
        if q:
            for a in q:
                message += a.name + ', '
    else:
        message = ""
    return HttpResponse(message)

def XMLlocation(request):
    if request.method == 'GET':
        message = ""
        location = request.GET.get('loc', ' ')
        # Filter and get possibilites for cities
        q = BaseLocation.objects.filter(city__istartswith=location)
        for a in q:
            message += a.city + ', ' + a.state.key + ', ' + a.country.abbr + ';'
        # Filter and get possibilies for states
        q = BaseLocation.objects.filter(Q(state__key__istartswith=location) |
                                        Q(state__name__istartswith=location))
        for a in q:
            message += a.state.name + ', ' + a.country.abbr + ';'
        # Filter and get possibilities for countries
        q = BaseLocation.objects.filter(Q(country__name__istartswith=location) |
                                        Q(country__abbr__istartswith=location))
        for a in q:
            message += a.country.name + ';'
        # Filter and sort by potential waterbodies
        q = WaterBody.objects.filter(name__istartswith=location)
        for a in q:
            message += a.name + ';'
    else:
        message = ""
    return HttpResponse(message)

def XMLmethod(request):
    if request.method == "GET":
        type = request.GET.get('method', ' ')
        message = ""
        q = FishingType.objects.filter(method__istartswith=type)
        for a in q:
            message += a.method + ';'
    else:
        message = ""
    return HttpResponse(message)
