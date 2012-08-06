from datetime import datetime, time, timedelta, date

from django.db import models
from django.db.models import Sum, Avg, Count, Q
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from myproject.location.models import BaseLocation, WaterBody
from myproject.customer.models import CustomerCore, ContactInfo, CustomerProfile

# Create your models here.

class FishingPayment(models.Model):
    guide = models.ForeignKey('FishingCore', related_name='PaymentModels')
    start_time = models.TimeField(default=time(9))
    end_time = models.TimeField(default=time(17))
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="How much do you charge for this time period? (In your local currency)")

    class Meta:
        app_label = 'fishing'
        verbose_name = "Payments Model"
        ordering = ['start_time', 'end_time']

    def __unicode__(self):
        return '%s: %s to %s' % (self.guide.person.full_name, self.start_time.strftime('%H-%M'), self.end_time.strftime('%H-%M'))

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("You cannot end before you started!")
        if self.amount < 0:
            raise ValidationError("Is giving away money really necessary?")
        payments = self.guide.PaymentModels.exclude((Q(start_time__lt=self.start_time) &
                                                     Q(end_time__lte=self.start_time)) |
                                                    (Q(end_time__gt=self.end_time) &
                                                     Q(start_time__gte=self.end_time)))
        if payments.exists():
            raise ValidationError("You have already defined an amount for this time period")

class FishingParty(models.Model):
    guide = models.OneToOneField('FishingCore', related_name='PartyModel')
    max_party = models.IntegerField("Max party size", help_text="Maximum Party Size that you are willing to take", blank=True, default=10)
    min_party = models.IntegerField("Min party size", help_text="Minimum Party Size that you are willing to take", blank=True, default=1)
    avg_party = models.IntegerField("Preferred party size", help_text="Leave blank to use average of max and min (if provided), otherwise default = 4", blank=True, default=4)

    def __unicode__(self):
        return 'Party Model for %s' % self.guide.person.full_name

    def clean(self):
        if self.max_party < self.min_party:
            raise ValidationError("Lookup minimum and maximum in the dictionary, and then fill these in")
        if self.avg_party > self.max_party or self.avg_party < self.min_party:
            raise ValidationError("Your math is truly awful. The avg lies between the min and max...")

    class Meta:
        app_label = 'fishing'
        verbose_name = "Party Model"

class FishingProfile(models.Model):
    blurb = models.CharField(help_text="Hook your customers with a few sentences", max_length=300, blank=True, default='')
    text = models.TextField(help_text="Say something about yourself on the Profile Page", blank=True, default='')
    num_recommends = models.IntegerField(editable=False, default=0)
    num_referrals = models.IntegerField(editable=False, default=0)
    date = models.DateField(auto_now_add=True)

    class Meta:
        app_label = 'fishing'
        verbose_name = "Fishing Profile"

    def __unicode__(self):
        return "Profile for Guide %s" % self.GuideMain.person.full_name

class FishingCore(models.Model):
    is_paying = models.BooleanField(blank=True, default=False, editable=False)
    is_signed_up = models.BooleanField(blank=True, default=False, editable=False)
    is_new = models.BooleanField(blank=True, default=True, editable=False)
    person = models.OneToOneField(CustomerCore, related_name='FishingCore')
    profile = models.OneToOneField(FishingProfile, related_name='GuideMain', editable=False, null=True)
    company = models.CharField(max_length=200, help_text="If you operate as part of a company, Enter the company name", blank=True, null=True)
    locations = models.ManyToManyField(BaseLocation, related_name='FishingGuides', blank=True, null=True)
    waterbodies = models.ManyToManyField(WaterBody, verbose_name="Bodies of Water", related_name='FishingGuides', blank=True, null=True)
    fish = models.ManyToManyField('Fish', related_name='FishingGuides', null=True, blank=True)
    methods = models.ManyToManyField('FishingType', related_name='FishingGuides', verbose_name="Methods of Fishing", help_text="What methods do you specialize in?", null=True, blank=True)
    experience = models.IntegerField("Years of Experience", default=0, blank=True)
    full_day_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)
    search_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)

    class Meta:
        app_label = 'fishing'
        verbose_name = "Core Fishing Guide Detail"
        verbose_name_plural = "Core Fishing Guide Details"

    def __unicode__(self):
        return 'Guide - %s' % self.person.full_name

    def get_absolute_url(self):
        return reverse('fishing_profile', kwargs={ 'id':str(self.id),
                                                   'name':slugify(self.person.full_name) })

    def associate_land(self):
        """
        Function to add locations of fishing for a guide, given the water bodies that he fishes in
        """
        if self.waterbodies.all():
            for w in self.waterbodies.all():
                self.locations.add(*w.locations.all())

    def associate_water(self):
        """
        Function to add water bodies for a guide, given the locations that he fishes in
        """
        if self.locations.all():
            for l in self.locations.all():
                self.waterbodies.add(*l.WaterBodies.all())

    def clean(self):
        if self.experience > settings.MAX_EXPERIENCE:
            raise ValidationError('Having over' + str(settings.MAX_EXPERIENCE) + 'years of experience is impossible without being in the record books')
        if self.experience < 0:
            raise ValidationError('Are you sure you are a Fishing Guide?')

    def save(self, *args, **kwargs):
        newprofile, created = FishingProfile.objects.get_or_create(GuideMain__person=self.person)
        if created: self.profile = newprofile
        try:
            this = FishingCore.objects.get(id=self.id)
        except:
            pass
        else:
            if self.is_new and date.today() > self.profile.date + timedelta(settings.NEW_TIME_LENGTH):
                self.is_new = False
        print self.person.id
        super(FishingCore, self).save(*args, **kwargs)

class FishingFAQ(models.Model):
    """
    Extras in this model that are not present on the profile page:
    - Capture Release
    - Lost Tackle
    - Allow International
    Things I should include?
    - Boats have a bathroom
    """
    guide = models.OneToOneField(FishingCore, related_name='FAQ')
    child_friendly = models.BooleanField(default=True, blank=True)
    alcohol_allowed = models.BooleanField(default=True, blank=True)
    food_provided = models.BooleanField(default=True, blank=True)
    capture_release = models.BooleanField(default=True, blank=True)
    state_certified = models.BooleanField(default=False, blank=True)
    CG_certified = models.BooleanField("US Coast Guard Certified", default=False, blank=True)
    cert_verify = models.BooleanField(default=False, blank=True)
    handicap_friendly = models.BooleanField(default=True, blank=True)
    personal_equipment = models.BooleanField("Require Personal Equipment", default=False, blank=True)
    lost_tackle = models.BooleanField("Extra Charge for Lost Tackle", default=False, blank=True)
    fillet_services = models.BooleanField(default=False, blank=True)
    taxidermy_services = models.BooleanField("Taxidermy Services", default=False, blank=True)
    allow_international = models.BooleanField("Allow International Customers", default=True, blank=True)
    explain = models.CharField("Explanations and Clarifications", max_length=1000, blank=True, null=True)
#    cf_explain = models.CharField("Explanation - Child Friendliness", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your children on board policies?")
#    al_explain = models.CharField("Explanation - Alcohol On Board", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your alcohol on board policies?")
#    fp_explain = models.CharField("Explanation - Food Provisions", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your policies on meals?")
#    cr_explain = models.CharField("Explanation - Capture and Release", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Capture and Release policies?")
#    sc_explain = models.CharField("Explanation - State Certification", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your State Certification?")
#    cg_explain = models.CharField("Explanation - Coast Guard Certification", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Coast Guard Certification?")
#    hf_explain = models.CharField("Explanation - Handicap Accessibility", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Handicap Person's policies?")
#    pe_explain = models.CharField("Explanation - Personal Equipment", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Policies on Personal Equipment?")
#    lt_explain = models.CharField("Explanation - Lost Tackle", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Policies on Lost Tackle?")
#    fs_explain = models.CharField("Explanation - Fillet Services", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Provision of Filleting Services?")
#    ts_explain = models.CharField("Explanation - Taxidermy Services", max_length=300, blank=True, null=True, help_text="Would you like to say a few words regarding your Provision of Taxidermy Services?")
#    ai_explain = models.CharField("Explanation - Allow International Customers", max_length=300, blank=True, null=True, help_text="Would you like to say a few words on your willingness to take International fishermen out on trips?")
    
    def __unicode__(self):
        return 'FAQ set for %s' % self.guide.person.full_name

    class Meta:
        app_label = 'fishing'
        verbose_name = "Guide FAQ"

class FishingExtraDetails(models.Model):
    """
    This can be divided into 2 portions based on my wishes. Also, remove equipment required from FAQ's
    (follow the table on the test profile page).
    To Bring:
    - Sunscreen
    - Hat
    - Sunglasses
    - Rain Gear
    - Motion Sickness Medicine
    - Food
    - Beverages
    - Ice Chest
    - Camera
    - Life Jacket
    - Fishing License
    - Fishing Rod
    - Fishing Reel
    - Bait
    - Insect Repellent
    - Layered Clothing
    - Fly Fishing Waders

    Not to Bring:
    - Glass Bottles
    - Illegal Drugs
    - Alcohol
    - Black or Dark soled shoes
    - Firearms
    - Bananas
    """
    guide = models.OneToOneField(FishingCore, related_name='ExtraDetails')
    good_attitude = models.NullBooleanField(null=True)
    life_jacket = models.NullBooleanField(null=True)
    other = models.CharField(max_length=700, help_text="Anything else that you want your customers to bring?", blank=True, null=True)

    def __unicode__(self):
        return "Extra Details for %s" % self.guide.person.full_name

    class Meta:
        app_label = 'fishing'
        verbose_name = "Extra Details"
        verbose_name_plural = "Extra Details"

class ShadowGuide(models.Model):
    """
    Do not need to be as stringent with these because this is either being filled in through the admin or
    automatically.
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=200, null=True, blank=True, help_text="Enter the name of the company if the guide has one")
    phone_number = models.CharField(max_length=20, help_text="Use standard characters in Phone number only", blank=True, null=True)
    locations = models.ManyToManyField(BaseLocation, related_name="ShadowGuides")
    email = models.EmailField(blank=True, null=True)
    added_from = models.URLField()

    class Meta:
        app_label = 'fishing'
        verbose_name = "Shadow Guide"
        unique_together = ('first_name', 'last_name', 'phone_number', 'email')

    def get_full_name(self):
        return self.first_name + self.last_name

    def set_full_name(self, name):
        self.first_name, self.last_name = name.split()

    full_name = property(get_full_name, set_full_name)

    def __unicode__(self):
        return self.full_name

# The following is the code to automatically add a calendar. Changes in the business model have made this
# unnecessary. Could be used as reference though
#            test = name_cal(self)
#            try:
#                Calendar.objects.get(name=test)
#            except ObjectDoesNotExist:
#                cal = Calendar(name=test, slug=test)
#                cal.save()
#                event = Event(title="Default Available", calendar=cal, creator=self.person, description="These are the default times that the guide is free. This can be altered by the guide at their discretion.")
#                event.start, event.end = datetime.combine(date.today(),time(8)), datetime.combine(date.today(),time(19))
#                event.rule = Rule.objects.get(name="Weekdays")
#                event.save()
