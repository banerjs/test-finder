# Used for generic templates
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings

def settings_processor(request):
    return { 'DOMAIN':settings.DOMAIN,
             'LOGIN_URL':settings.LOGIN_URL,
             'LOGOUT_URL':settings.LOGOUT_URL,
             'CSS_URL':settings.CSS_URL,
             'JS_URL':settings.JS_URL,
           }

def contactResponse(request):
    if request.method == 'POST' and request.POST.get('name') and request.POST.get('email') and request.POST.get('msg'):
        subject = 'Review for the site'
        from_email = settings.DEFAULT_FROM_EMAIL
        message = 'Name: ' + request.POST.get('name') + '\nEmail: ' + request.POST.get('email')
        message += '\nMessage:\n' + request.POST.get('msg')
        send_mail(subject, message, from_email, ['contact@theguidefinder.com'], fail_silently=True)
        return render(request, 'thanks.html')
    else:
        return redirect(settings.DOMAIN+'contact/')
