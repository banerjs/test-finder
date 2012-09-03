from django.contrib import admin
from myproject.location.models import BaseLocation, Country, WaterBody, GeoRelations

def update_water(modeladmin, request, queryset):
    for obj in queryset:
        for w in obj.WaterBodies.all():
            w.associate_locations()
update_water.short_description = "Update Water Bodies"

class BaseLocationAdmin(admin.ModelAdmin):
    actions = [update_water]
    list_display = ('city', 'state', 'country')
    list_editable = ('state',)
    ordering = ('country', 'state', 'city')
    #form = BaseLocationForm

def update_locations(modeladmin, request, queryset):
    for obj in queryset:
        obj.associate_locations()
update_locations.short_description = "Reassociate locations"

class WaterBodyAdmin(admin.ModelAdmin):
    actions = [update_locations]
    list_display = ('__unicode__', 'state', 'country')
    #form = WaterBodyForm

class GeoRelationsAdmin(admin.ModelAdmin):
    list_display = ('location', 'water', 'verified')
    list_editable = ('verified',)
    list_display_links = ('location', 'water')

#admin.site.register(WaterBody, WaterBodyAdmin)
admin.site.register(GeoRelations, GeoRelationsAdmin)
#admin.site.register(BaseLocation, BaseLocationAdmin)
admin.site.register(Country)
