import sys
import math

from django.db import models, connection, transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings

from myproject.custom import GoogleLatLng

# Create your models here.

WATER_TYPES = (('FW', 'Freshwater'),
               ('SW', 'Saltwater'))

WATERBODY_TYPES = (
    'Loch',
    'Canal',
    'Brook',
    'Ocean',
    'Creek',
    'Sea',
    'Lake',
    'River',
    'Stream',
    'Basin',
    'Bay',
    'Bayou',
    'Channel',
    'Strait',
)    

class Country(models.Model):
    abbr = models.CharField("Abbreviation", max_length=2, primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    abbr3 = models.CharField("3 letter Abbreviation", max_length=3, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Countries'
        unique_together = ('abbr', 'name')

class LocationManager(models.Manager):
    def nearby_locations(self, latitude, longitude, radius, use_miles=False):
        if use_miles:
            distance_unit = 3959
        else:
            distance_unit = 6371
        cursor = connection.cursor()
        sql = """SELECT id, lat, lng FROM %s WHERE (%f * acos( cos( radians(%f) ) * cos( radians( lat ) ) *
        cos( radians( lng ) - radians(%f) ) + sin( radians(%f) ) * sin( radians( lat ) ) ) ) < %d
        """ % (self.model._meta.db_table, distance_unit, latitude, longitude, latitude, int(radius))
        cursor.execute(sql)
        ids = [row[0] for row in cursor.fetchall()]
        return self.filter(id__in=ids)

class BaseLocation(models.Model):
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150, null=True, blank=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    lat = models.FloatField(blank=True, default=1000.0)
    lng = models.FloatField(blank=True, default=1000.0)
    
    objects = models.Manager()
    neighbours = LocationManager()

    def __unicode__(self):
        return u'%s, %s, %s' % (self.city, self.state, self.country.name)

    class Meta:
        verbose_name = "Location of Operation"
        unique_together = ('lat', 'lng')

class WaterBody(models.Model):
    name = models.CharField("Name of Water Body", max_length=150, unique=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    locations = models.ManyToManyField(BaseLocation, through='GeoRelations', verbose_name="Nearby Locations", blank=True, editable=False, null=True, related_name="WaterBodies")
    lat = models.FloatField(blank=True, default=1000.0)
    lng = models.FloatField(blank=True, default=1000.0)
    
    objects = models.Manager()
    neighbours = LocationManager()

    def __unicode__(self):
        return self.name
    
    def associate_locations(self, loc_model=BaseLocation, radius=100, use_miles=True):
        near = loc_model.neighbours.nearby_locations(self.lat, self.lng, radius, use_miles)
        for l in near:
            try:
                r = GeoRelations.objects.get(location__exact=l, water__exact=self)
            except:
                r = GeoRelations(location=l, water=self, verified=True)
                r.save()

    class Meta:
        verbose_name = "Body of Water"
        verbose_name_plural = "Bodies of Water"
        unique_together = ('lat', 'lng')

class GeoRelationsManager(models.Manager):
    def user_edit(self, loc, wat, cust):
        """
        loc is a BaseLocation object,
        wat is a WaterBody object,
        cust is a CustomerCore object
        """
        newrel = self.model(location=loc, water=wat, added_by=cust)
        newrel.save()
        return newrel

class GeoRelations(models.Model):
    location = models.ForeignKey(BaseLocation)
    water = models.ForeignKey(WaterBody)
    verified = models.BooleanField(blank=True, default=False)
    added_by = models.ForeignKey('customer.CustomerCore', null=True, related_name="GeoRelations")
    added_on = models.DateTimeField(auto_now_add=True)

    custom = GeoRelationsManager()
    objects = models.Manager()

    def __unicode__(self):
        return '%s - %s' % (self.location, self.water)

    def verify(self):
        self.verified = True
        self.save(force_update=True)

    class Meta:
        verbose_name = "Geographic Relationship"
        unique_together = ('location', 'water')

# The following is the code that the old Water Body had

#     def clean(self, **kwargs):
#         mquery = kwargs.get('mquery')
#         if self.name or mquery:
#             if not mquery:
#                 mquery = GoogleLatLng()
#                 state = self.state.name if self.state else ''
#                 country = self.country.abbr if self.country else ''
#                 if not mquery.requestLatLngJSON(self.name + ', ' + state + ', ' + country, True):
#                     raise ValidationError("There is an error in the location string")
#             l = mquery.parseLocation() # Again assume that all args to clean with mquery pass this test
#             if not l:
#                 raise ValidationError("This body of water could not be found")
#             self.json_response = mquery.results
#             self.name = l[0]
#             if len(l) > 1:
#                 newcountry, created = Country.objects.get_or_create(abbr=l[-1][1], name=l[-1][0],
#                                                                     defaults={'abbr':l[-1][1], 'name':l[-1][0]})
#                 self.country = newcountry
#             else:
#                 self.country = None
#             if len(l) > 2:
#                 newstate, created = State.objects.get_or_create(key=l[-2][1], name=l[-2][0], country=self.country,
#                                                                 defaults={'key':l[-2][1],
#                                                                           'name':l[-2][0],
#                                                                           'country':self.country})
#                 self.state = newstate
#             else:
#                 self.state = None
#             self.lat = mquery.lat
#             self.lng = mquery.lng

#     def save(self, mquery=None, *args, **kwargs):
#         self.clean(mquery=mquery)
#         if mquery:
#             try:
#                 test = WaterBody.objects.get(lat=self.lat, lng=self.lng)
#             except ObjectDoesNotExist:
#                 pass
#             else:
#                 return
#         super(WaterBody, self).save(*args, **kwargs)

# The following is the code that the old location had

#     def clean(self, **kwargs):
#         mquery = kwargs.get('mquery')
#         if self.city or mquery:
#             if not mquery:
#                 mquery = GoogleLatLng()
#                 state = self.state.name if self.state else ''
#                 country = self.country.abbr if self.country else ''
#                 if not mquery.requestLatLngJSON(self.city + ', ' + state + ', ' + country):
#                     raise ValidationError("There is an error in the location string")
#             l = mquery.parseLocation()
#             if not l: # It is assumed that all args to clean with mquery will be cities
#                 raise ValidationError("This city could not be found")
#             self.json_response = mquery.results
#             self.city = l[0]
#             newcountry, created = Country.objects.get_or_create(abbr=l[-1][1], name=l[-1][0],
#                                                                 defaults={'abbr':l[-1][1], 'name':l[-1][0]})
#             self.country = newcountry
#             if len(l) > 2:
#                 newstate, created = State.objects.get_or_create(key=l[-2][1], name=l[-2][0], country=self.country,
#                                                                 defaults={'key':l[-2][1],
#                                                                           'name':l[-2][0],
#                                                                           'country':self.country})
#                 self.state = newstate
#             else:
#                 self.state = None
#             self.lat = mquery.lat
#             self.lng = mquery.lng

#     def save(self, mquery=None, *args, **kwargs):
#         self.clean(mquery=mquery)
#         if mquery:
#             try:
#                 test = BaseLocation.objects.get(lat=self.lat, lng=self.lng)
#             except ObjectDoesNotExist:
#                 pass
#             else:
#                 return
#         super(BaseLocation, self).save(*args, **kwargs)

# The following is the old State model

# class State(models.Model):
#     country = models.ForeignKey(Country, related_name='States')
#     key = models.CharField(max_length=100, editable=False)
#     name = models.CharField(max_length=150)
#     verified = models.BooleanField()

#     def __unicode__(self):
#         return self.name

#     def save(self, **kwargs):
#         if not self.key or len(self.key) > 100:
#             self.key = self.name[:100]
#         super(State, self).save(**kwargs)
    
#     class Meta:
#         unique_together = ('country', 'name')
