from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('myproject.fishing.views',
                       url(r'^$', TemplateView.as_view(template_name='fishing/search/search.html'),
                           name='fishing_home'),
                       url(r'^search/$', 'searchDisplay', { 'disp': True }, name='fishing_search'),
                       url(r'^xmlhttp/search/$', 'searchDisplay',
                           { 'template_name':'fishing/search/results.html' },
                           name='fishing_search_XML'),
                       url(r'^xmlhttp/fish/$', 'XMLfish', name='fishing_fishnames_XML'),
                       url(r'^profiles/(?P<id>\d+)/(?P<name>[A-Za-z_-]*)/$', 'showProfile',
                           name='fishing_profile'),
)
