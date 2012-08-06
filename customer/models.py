import os, sys
import Image
import random

from django.db import models
from django.db.models import F
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError, SuspiciousOperation, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.template.defaultfilters import slugify

from myproject.custom import digits, GoogleLatLng, resize_image
from myproject.location.models import BaseLocation, Country

# Create your models here.

new_image = Signal(providing_args={'instance'})

class ContactInfo(models.Model):
    address_line_1 = models.CharField(max_length=150, null=True, blank=True)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=150)
    country = models.ForeignKey(Country, blank=True, null=True)
    email = models.EmailField('Email Address', help_text="This is your ID for sign in by default")
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    main_phone = models.CharField(max_length=20, help_text="Enter a phone number. Include a country code if outside the USA", null=True, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Enter an alternate phone number. (optional)")
    lat = models.FloatField(editable=False, default=1000.0)
    lng = models.FloatField(editable=False, default=1000.0)

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __unicode__(self):
        return 'Contact Information for %s' % self.ParentInfo.full_name

    # clean and clean_location need to be changed based on location parsing
    def clean(self):
        if self.city and self.country:
            pass
        else:
            raise ValidationError("Please enter a location")

#    def clean_location(self):
#        return
#        # address_1 = self.address_line_1 if self.address_line_1 else ''
#         state = self.state.name if self.state else ''
#         address_2 = self.address_line_2 if self.address_line_2 else ''
#         ncity, created = BaseLocation.objects.get_or_create(city=self.city, state__name=state, country=self.country,
#                                                             defaults={'city':self.city,
#                                                                       'state':self.state,
#                                                                       'country':self.country})
#         locQuery = GoogleLatLng()
#         if not locQuery.requestLatLngJSON(address_1 + ', ' + address_2 + ', ' + self.city + ', ' + state + ', ' + self.country.abbr):
#             if not locQuery.requestLatLngJSON(address_2 + ', ' + self.city + ', ' + state + ', ' + self.country.abbr):
#                 self.lat = ncity.lat
#                 self.lng = ncity.lng
#             else:
#                 self.lat = locQuery.lat
#                 self.lng = locQuery.lng
#         else:
#             self.lat = locQuery.lat
#             self.lng = locQuery.lng

    def save(self, *args, **kwargs):
#        if self.city and self.country:
#            self.clean_location()
        super(ContactInfo, self).save(*args, **kwargs)

class CustomerCore(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    contact = models.OneToOneField(ContactInfo, related_name='ParentInfo', editable=False)
    profile = models.OneToOneField('CustomerProfile', related_name='CustomerMain', editable=False)
    user = models.OneToOneField(User, related_name='CustomerCore')
    is_fishing_guide = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Customer Primary Detail"
        ordering = ['first_name', 'middle_name', 'last_name']

    def save(self, *args, **kwargs):
        newcontact, created = ContactInfo.objects.get_or_create(ParentInfo__user=self.user,
                                                                defaults={'email':self.user.email})
        if created: self.contact = newcontact
        newprofile, created = CustomerProfile.objects.get_or_create(CustomerMain__user=self.user)
        if created: self.profile = newprofile
        super(CustomerCore, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return settings.PROFILE_URL + str(self.id) + '/'

    def get_pretty_url(self):
        return settings.DOMAIN + 'profiles/' + str(self.id) + '/' + slugify(self.full_name) + '/'

    def get_full_name(self):
        if self.middle_name:
            return u'%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        else:
            return u'%s %s' % (self.first_name, self.last_name)

    def set_full_name(self, fullname):
        self.first_name, self.last_name = fullname.split()

    full_name = property(get_full_name, set_full_name)

    def __unicode__(self):
        return self.full_name
    
class CustomerProfile(models.Model):
    allow_text = models.BooleanField(default=False)
    fave_fishguide = models.ManyToManyField('fishing.FishingCore', verbose_name="Favorite Guides", blank=True, null=True, related_name='Fans')
    ntrips = models.IntegerField("Number of trips", blank=True, default=0, editable=False)

    def __unicode__(self):
        return u'Profile for %s' % self.CustomerMain.full_name

    def save(self, *args, **kwargs):
        # A gallery is not created in a similar manner to a profile here
        # because a) There can be multiple galleries b) The profile ID is
        # needed to associate the profile with the gallery before saving.
        # Hence I need a signal
        super(CustomerProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Customer Profile Information"

class PictureGallery(models.Model):
    owner_profile = models.ForeignKey(CustomerProfile, related_name="Galleries")
    description = models.CharField(max_length=500, blank=True, null=True)
    creation_date = models.DateField(auto_now_add=True)
    num_photos = models.IntegerField(editable=False, default=0)
    max_photos = models.IntegerField(editable=False, blank=True)

    class Meta:
        verbose_name = "Picture Gallery"
        verbose_name_plural = "Picture Galleries"

    def __unicode__(self):
        return 'Gallery ID: %d, for %s' % (self.id, self.owner_profile.CustomerMain.full_name)

    def save(self, *args, **kwargs):
        if self.owner_profile.CustomerMain.is_fishing_guide:
            self.max_photos = settings.GUIDE_MAX_PHOTOS
        else:
            self.max_photos = settings.CUSTOMER_MAX_PHOTOS
        if self.num_photos > self.max_photos:
            return False
        super(PictureGallery, self).save(*args, **kwargs)

    def get_gallery_root(self):
        return 'users/' + str(self.owner_profile.CustomerMain.id) + '/gallery/' + str(self.id) + '/'

    def get_absolute_url(self):
        return settings.PROFILE_URL + str(self.owner_profile.CustomerMain.id) + '/gallery/' + str(self.id) + '/'

class Photograph(models.Model):
    gallery = models.ForeignKey(PictureGallery, related_name='Photos')
    title = models.CharField(help_text="Give your photo a title", max_length=30)
    summary = models.CharField(max_length=700, blank=True, default='', help_text="Give your photo a summary (optional)")
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='temp/photos/', help_text="Maximum resolution: 800x600. Larger images will be resized", max_length=300)
    thumb = models.ImageField(upload_to='temp/photos/', editable=False, max_length=300)

    class Meta:
        ordering = ['gallery', '-date']

    def __unicode__(self):
        return str(self.gallery.id) + ': ' + self.title

    def save(self, *args, **kwargs):
        newphoto = False
        try:
            this = Photograph.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
                newphoto = True
        except ObjectDoesNotExist:
            newphoto = True
        except:
            pass
        try:
            if this.thumb != self.thumb:
                this.thumb.delete(save=False)
                newphoto = True
        except ObjectDoesNotExist:
            newphoto = True
        except:
            pass
        super(Photograph, self).save(*args, **kwargs)
        self.gallery.num_photos = self.gallery.Photos.count()
        self.gallery.save()
        if (newphoto):
            new_image.send(sender=Photograph, instance=self)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete(save=False)
        except:
            pass
        try:
            self.thumb.delete(save=False)
        except:
            pass
        super(Photograph, self).delete(*args, **kwargs)

from myproject.customer.signals import *
