from django.conf.urls.defaults import *
from django.views.generic import TemplateView, RedirectView
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'back.views.home', name='home'),
    # url(r'^back/', include('back.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^messages/', include('messages.urls')),
    url(r'^', include('social_auth.urls')),
    url(r'^', include('registration.urls')),
    url(r'^fishing/', include('myproject.fishing.urls')),
    url(r'^customer/', include('myproject.customer.urls')),
    url(r'^$', RedirectView.as_view(url='/fishing/', permanent=True, query_string=True), name='MAIN_home'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='MAIN_about'),
    url(r'^contact/$', TemplateView.as_view(template_name="contact.html"), name='MAIN_contact'),
)

urlpatterns += patterns('myproject.views',
                        url('^thanks/$', 'contactResponse', name='MAIN_thanks'),
)
