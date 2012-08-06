from django.contrib import admin
from myproject.prefill.models import BaseLocation, WaterBody

admin.site.register([WaterBody, BaseLocation])
