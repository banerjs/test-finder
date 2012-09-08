# Used for generic templates
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.conf import settings

# Global Context Processor

def settings_processor(request):
    return { 'DOMAIN':settings.DOMAIN,
             'LOGIN_URL':settings.LOGIN_URL,
             'LOGOUT_URL':settings.LOGOUT_URL,
             'CSS_URL':settings.CSS_URL,
             'JS_URL':settings.JS_URL,
             'DYNAMIC_JS_URL':settings.DYNAMIC_JS_URL,
           }

# Global Lookup Tables

JSLookup = {
             'geocode.js':
             {
               'fishing_search':
               {
                 'input_name': 'loc',
                 'autocomplete': 1,
                 'field_id': 'geocode',
               },
               'location_baselocation':
               {
                 'field_id': 'id',
                 'disable_submit': 1,
                 'submit_buttons': ['admin_save', 'admin_saveasnew', 'admin_addanother', 'admin_continue'],
                 'input_name': ['city', 'state', 'country'],
             },
           }

# Custom View Definitions

def contactResponse(request):
    if request.method == 'POST' and request.POST.get('name') and request.POST.get('email') and request.POST.get('msg'):
        subject = 'Review for the site'
        from_email = settings.DEFAULT_FROM_EMAIL
        message = 'Name: ' + request.POST.get('name') + '\nEmail: ' + request.POST.get('email')
        message += '\nMessage:\n' + request.POST.get('msg')
        send_mail(subject, message, from_email, ['contact@theguidefinder.com'], fail_silently=True)
        return render(request, 'thanks.html')
    else:
        return redirect('MAIN_contact')

def serveDynamicJS(request, module, file_name, **kwargs):
    global JSLookup
    template_name = 'js/'+file_name
    try:
        return render(request, template_name, JSLookup[file_name][module], content_type="application/javascript")
    except:
        raise Http404
