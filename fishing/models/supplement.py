import sys
import math
import pycurl, urllib

from django.utils import simplejson as json
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, transaction
from django.db.models.signals import post_save
from django.dispatch import Signal

from myproject.custom import GoogleLatLng, resize_image
from myproject.location.models import BaseLocation, WaterBody, WATER_TYPES
from myproject.customer.models import CustomerCore

# Create your models here.

make_thumbnail = Signal(providing_args={'instance', 'max_size'})

class Fish(models.Model):
    name = models.CharField("Name of Fish", max_length=30)
    type = models.CharField("Type of Fish", max_length=30)
    water_type = models.CharField("Water Habitat of Fish", max_length=2, choices=WATER_TYPES)
    alternate_name_1 = models.CharField(max_length=30, blank=True, null=True)
    alternate_name_2 = models.CharField(max_length=30, blank=True, null=True)
    alternate_name_3 = models.CharField(max_length=30, blank=True, null=True)
    image = models.ImageField(upload_to='fishimages/', blank=True, null=True)
    verified = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'fishing'
        verbose_name_plural = "Fish"
        unique_together = ("name", "type", "water_type")

    def save(self, *args, **kwargs):
        try:
            this = Fish.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass
        super(Fish, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete(save=False)
        except:
            pass
        super(Fish, self).delete(*args, **kwargs)

class FishingType(models.Model):
    method = models.CharField("Type of Fishing Trip", max_length=100, unique=True)
    image = models.ImageField(upload_to='typeimages/', blank=True, null=True)
    verified = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        return self.method

    class Meta:
        app_label = 'fishing'
        verbose_name = "Fishing Type"

    def save(self, *args, **kwargs):
        try:
            this = FishingType.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass
        super(FishingType, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete(save=False)
        except:
            pass
        super(FishingType, self).delete(*args, **kwargs)

class InheritanceCastModel(models.Model):
    """
    An abstract base class that provides a ``real_type`` FK to ContentType.
    
    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.
    """
    real_type = models.ForeignKey(ContentType, editable=False, null=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(InheritanceCastModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    class Meta:
        abstract = True

class BaseBrand(InheritanceCastModel):
    brand = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='logos/', blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.brand

    class Meta:
        app_label = 'fishing'
        abstract = True

    def save(self, *args, **kwargs):
        try:
            this = self.cast()
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass
        super(BaseBrand, self).save(*args, **kwargs)
        make_thumbnail.send(sender=BaseBrand.__name__, instance=self, max_size=settings.BRAND_PHOTOS_MAX_SIZE)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete(save=False)
        except:
            pass
        super(BaseBrand, self).delete(*args, **kwargs)

class LureBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', null=True, blank=True)

    class Meta(BaseBrand.Meta):
        verbose_name = "Lure Brand"

class RodBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', blank=True, null=True)
    
    class Meta(BaseBrand.Meta):
        verbose_name = "Rod Brand"

class ReelBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', blank=True, null=True)
    
    class Meta(BaseBrand.Meta):
        verbose_name = "Reel Brand"

class LineBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', blank=True, null=True)

    class Meta(BaseBrand.Meta):
        verbose_name = "Line Brand"

class BaitBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', blank=True, null=True)

    class Meta(BaseBrand.Meta):
        verbose_name = "Bait Brand"

class EngineBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', related_name='related_%(class)s', blank=True, null=True)
    
    class Meta(BaseBrand.Meta):
        verbose_name = "Engine Brand"

class BoatBrand(BaseBrand):
    guide = models.ManyToManyField('FishingCore', through='GuideBoat', blank=True, null=True)

    class Meta(BaseBrand.Meta):
        verbose_name = "Boat Brand"

class GuideBoat(models.Model):
    boat_brand = models.ForeignKey(BoatBrand)
    guide = models.ForeignKey('FishingCore', related_name='boats')
    boat_length = models.PositiveIntegerField(help_text="Please enter the length in feet")
    model = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label='fishing'
        verbose_name = "Boats owned by Guides"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.boat_brand.__unicode__() + ', ' + self.model + ' for ' + self.guide.__unicode__()
