from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name="profile")
    pesel = models.CharField(validators=[RegexValidator(regex='^\d{11}$', message='Length has to be 11', code='nomatch')],max_length=11)

    def __str__(self):
        return self.user.get_full_name().encode('utf-8')

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()


class Voting(models.Model):
    #Klucze dodawane sa automatycznie
    nazwa = models.CharField(max_length=100)
    opis = models.CharField(max_length=500)
    maxGlosow = models.PositiveIntegerField(default=1)
    od = models.DateField('poczatek',default=timezone.now)
    do = models.DateField('koniec')
    moderator = models.ForeignKey(UserProfile,related_name='myVotings') # domyslnie relacja wiele do jednego

    #te dwa pola nie sa koniecznie potrzebne
    kandydaci = models.ManyToManyField(UserProfile, through='Candidate',related_name='participate')
    uprawnieni = models.ManyToManyField(UserProfile, through='Voter',related_name='canVote')
     # kandydaci pozwala na szybki dostep do kandydatow danego glosowania
    def __str__(self):
        return self.nazwa.encode('utf-8')


class Candidate(models.Model):

    glosowanie = models.ForeignKey(Voting)
    osoba = models.ForeignKey(UserProfile)
    wynik = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.osoba.__str__()

class Voter(models.Model):
    #Id
    glosowanie = models.ForeignKey(Voting)
    osoba = models.ForeignKey(UserProfile)
    zaglosowal = models.BooleanField(default=False)
    def __str__(self):
        return self.osoba.__str__()
