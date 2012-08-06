import os

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from django.conf import settings

from myproject.custom import resize_image
from myproject.customer.models import CustomerCore
from myproject.fishing.models import *

# The following are signal handlers for fishing.

# These are the handlers for classes in supplement.py

# For the signal handlers below, I don't need to worry about infinite recursion because the model is not being
# updated

@receiver(post_save, sender=Fish)
def fish_thumbnail(sender, created=False, instance=None, **kwargs):
    if instance:
        max_size = settings.FISH_PHOTOS_MAX_SIZE
        resize_image(instance.image, max_size)

@receiver(post_save, sender=FishingType)
def type_thumbnail(sender, created=False, instance=None, **kwargs):
    if instance:
        max_size = settings.BRAND_PHOTOS_MAX_SIZE
        resize_image(instance.image, max_size)

@receiver(make_thumbnail, sender='BaseBrand')
def brand_thumbnail(sender, instance=None, max_size=None, **kwargs):
    if instance and max_size:
        resize_image(instance.image, max_size)

# This is a snippet of code that can prevent infinite save loops in the future
#    if instance:
#        if hasattr(instance, '_already_saving'):
#            del instance._already_saving
#            return
#        instance._already_saving = True
#        #... Do something ...#
#        instance.save()

# These are the signal handlers for guide.py

def update_price(obj, **kwargs):
    dict = obj.guide.PaymentModels.aggregate(sum=Sum('amount'), min=Min('amount'), count=Count('id'))
    if not dict['count']:
        dict['min'] = 0
        dict['sum'] = 0
    obj.guide.full_day_price = dict['sum']
    obj.guide.search_price = dict['min']
    obj.guide.save(force_update=True)

@receiver(post_save, sender=FishingPayment)
def new_price_handler(sender, created=False, instance=None, **kwargs):
    if created and instance:
        update_price(instance, **kwargs)

@receiver(post_delete, sender=FishingPayment)
def change_price_handler(sender, instance=None, **kwargs):
    if instance:
        update_price(instance, **kwargs)

@receiver(post_save, sender=FishingCore)
def create_profile(sender, created=False, instance=False, **kwargs):
    if created and instance:
        party = FishingParty.objects.get_or_create(guide=instance, defaults={'guide':instance})
        FAQ = FishingFAQ.objects.get_or_create(guide=instance, defaults={'guide':instance})
        details = FishingExtraDetails.objects.get_or_create(guide=instance, defaults={'guide':instance})

@receiver(post_save, sender=CustomerCore)
def check_guide(sender, created=False, instance=None, **kwargs):
    if instance and instance.is_fishing_guide:
        newguide, created = FishingCore.objects.get_or_create(person=instance,
                                                              defaults={'person':instance})
