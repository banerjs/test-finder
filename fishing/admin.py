from django.contrib import admin
from myproject.fishing.models import Fish, FishingType, BoatBrand, FishingFAQ, ShadowGuide
from myproject.fishing.models import LureBrand, RodBrand, ReelBrand, LineBrand, BaitBrand, FishingExtraDetails
from myproject.fishing.models import GuideBoat, EngineBrand, FishingPayment, FishingParty, FishingProfile, FishingCore

class FishAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'water_type', 'verified')
    list_editable = ('verified',)

class FishingTypeAdmin(admin.ModelAdmin):
    list_display = ('method', 'verified')
    list_editable = ('verified',)

class ShadowGuideAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'phone_number', 'email')
    list_editable = ('phone_number', 'email')

class FishingFAQAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'child_friendly', 'alcohol_allowed', 'food_provided', 'capture_release',
                    'state_certified', 'CG_certified', 'handicap_friendly', 'personal_equipment',
                    'lost_tackle', 'fillet_services', 'taxidermy_services', 'allow_international')

class FishingExtraDetailsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'good_attitude')

class BrandAdmin(admin.ModelAdmin):
    filter_horizontal = ('guide',)

class FishingCoreAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'company')
    filter_horizontal = ('locations', 'fish', 'methods', 'waterbodies')

#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == "person":
#            kwargs["queryset"] = CustomerCore.objects.filter(is_guide=False)
#        return super(GuideCoreAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class FishingPaymentAdmin(admin.ModelAdmin):
    list_display = ('guide', 'start_time', 'end_time')
    ordering = ('guide', '-start_time')

class FishingPartyAdmin(admin.ModelAdmin):
    list_display = ('guide', 'avg_party', 'max_party', 'min_party')

admin.site.register(FishingCore, FishingCoreAdmin)
admin.site.register(FishingPayment, FishingPaymentAdmin)
admin.site.register(FishingParty, FishingPartyAdmin)
admin.site.register(Fish, FishAdmin)
admin.site.register(FishingType, FishingTypeAdmin)
admin.site.register(ShadowGuide, ShadowGuideAdmin)
admin.site.register(FishingFAQ, FishingFAQAdmin)
admin.site.register(FishingExtraDetails, FishingExtraDetailsAdmin)
admin.site.register([LureBrand, RodBrand, ReelBrand, LineBrand, BaitBrand, EngineBrand, BoatBrand], BrandAdmin)
admin.site.register([GuideBoat, FishingProfile])
