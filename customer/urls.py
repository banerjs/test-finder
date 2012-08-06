from django.conf.urls.defaults import *

urlpatterns = patterns('myproject.customer.views',
                       url(r'^$', 'displayHome', name='customer_home'),
                       #url(r'dashboard/$', 'displayDash', name='customer_dashboard'),
                       url(r'address_change/$', 'changeAddress', name='customer_address_change'),
)
