import os, sys
import Image
import random
from Image import ANTIALIAS

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from myproject.custom import resize_image
from myproject.customer.models import CustomerProfile, CustomerCore, Photograph, PictureGallery
from myproject.customer.models import new_image

# The signals for the models in customer.models are defined here

@receiver(post_save, sender=CustomerCore)
def make_gallery(sender, created=False, instance=None, **kwargs):
    if created and instance and not instance.profile.Galleries.all():
        gallery = PictureGallery()
        gallery.owner_profile = instance.profile
        gallery.save(force_insert=True)

@receiver(new_image, sender=Photograph)
def order_images(sender, instance=None,**kwargs):
    if instance:
        max_size = settings.PROFILE_PHOTOS_MAX_SIZE
        t_size = settings.PROFILE_PHOTOS_MAX_THUMB
        old_thumb = instance.thumb
        old_path = instance.image
        gallery_root = instance.gallery.get_gallery_root()
        name = str(instance.image).split('/')[-1]
        temp = name.split('.')
        name = temp[0][:20] + '.' + temp[1]
        im = Image.open(settings.MEDIA_ROOT + str(instance.image))
        im.thumbnail(max_size, ANTIALIAS)
        try:
            os.makedirs(settings.MEDIA_ROOT + gallery_root)
        except OSError, IOError:
            pass
        while os.path.exists(settings.MEDIA_ROOT + gallery_root + name):
            splice = name.split('.')
            name = splice[0] + str(random.randint(0,9)) + '.' + splice[-1]
        instance.image = gallery_root + name
        im.save(settings.MEDIA_ROOT + str(instance.image), "JPEG")
        im.thumbnail(t_size, ANTIALIAS)
        name = name.split('.')[0] + '.thumbnail'
        instance.thumb = gallery_root + name
        im.save(settings.MEDIA_ROOT + str(instance.thumb), "JPEG")
        os.remove(settings.MEDIA_ROOT + str(old_path))
        try:
            os.remove(settings.MEDIA_ROOT + str(old_thumb))
        except:
            pass
        super(Photograph, instance).save(force_update=True)

@receiver(post_save, sender=User)
def make_customer(sender, created=False, instance=None, **kwargs):
    if created and instance:
        customer = CustomerCore(user=instance)
        if instance.first_name: customer.first_name = instance.first_name
        else: customer.first_name = 'New'
        if instance.last_name: customer.last_name = instance.last_name
        else: customer.last_name = 'User'
        customer.save(force_insert=True)

@receiver(post_save, sender=CustomerCore)
def update_name(sender, created=False, instance=None, **kwargs):
    if instance:
        instance.user.first_name = instance.first_name
        instance.user.last_name = instance.last_name
        instance.user.save(force_update=True)
