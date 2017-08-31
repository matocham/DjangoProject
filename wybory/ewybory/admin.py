from django.contrib import admin
from ewybory.models import Voting
from ewybory.models import UserProfile
from ewybory.models import Candidate
from ewybory.models import Voter
# Register your models here.
admin.site.register(Voting)
admin.site.register(UserProfile)
admin.site.register(Candidate)
admin.site.register(Voter)