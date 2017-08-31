# -*- coding: utf-8 -*-
from django.forms import ModelForm,SelectMultiple,Textarea,PasswordInput,CheckboxSelectMultiple
from models import UserProfile,Voting
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def validate_email_unique(value):
    for p in User.objects.values('email'):
        if p['email']==value:
            raise ValidationError(u'%s juz istnieje w bazie' % value)

class UserProfileForm(ModelForm):
    pesel = forms.CharField(label='PESEL', max_length=11, min_length=11)
    captcha = CaptchaField()
    class Meta:
        model = UserProfile
        exclude = ['user']

class UserRegForm(UserCreationForm):
    email = forms.EmailField(label='E-mail',required=True,validators=[validate_email_unique])

    class Meta:
        model = User
        fields = ("username","first_name","last_name","email")


class VotingForm(ModelForm):

    class Meta:
        model = Voting
        exclude = ['moderator'] ## nie potrzebujemy tego pola - zalogowany uzytkownik to moderator
        widgets = {
            'kandydaci': SelectMultiple(attrs={'size':10,}),
            'uprawnieni': SelectMultiple(attrs={'size': 10,}),
            'opis': Textarea(attrs={'cols': 40, 'rows': 12}),
        }


    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user', None)
        super(VotingForm, self).__init__(*args, **kwargs)
        self.fields["kandydaci"].queryset = UserProfile.objects.exclude(user=self.user)
        self.fields["kandydaci"].required=True

    def clean_maxGlosow(self):
        maxgg = self.cleaned_data.get("maxGlosow")
        if maxgg<1:
            raise forms.ValidationError(
                                        _(u'Nieprawidłowa maksymalna liczba głosów do oddania: %(value)s'),
                                        code='invalid',
                                        params={'value': self.cleaned_data['maxGlosow']},
                                        )
        return maxgg

    def clean_kandydaci(self):
        kand = self.cleaned_data.get("kandydaci")
        if len(kand)<2:
            raise forms.ValidationError(
                                        _(u'Aby założyć głosowanie należy wybrać co najmniej 2 kandydatów'),
                                        code='invalid',
                                        )
        return kand

    def clean_do(self):
        koniec = self.cleaned_data['do']

        if koniec:
            if koniec <= timezone.now().date():
                raise forms.ValidationError(
                                        _(u'Data zakończenia głosowania musi być terminem przyszłym: %(value)s'),
                                        code='invalid',
                                        params={'value': self.cleaned_data['do']},
                                        )
        return koniec

    def clean_od(self):
        poczatek = self.cleaned_data['od']

        if poczatek:
            if poczatek < timezone.now().date():
                raise forms.ValidationError(
                                        _(u'Data rozpoczęcia głosowania nie może być przeszła: %(value)s'),
                                        code='invalid',
                                        params={'value': self.cleaned_data['od']},
                                        )
        return poczatek

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        kandydaci = cleaned_data.get("kandydaci")
        uprawnieni = cleaned_data.get("uprawnieni")

        if kandydaci and uprawnieni:
            # Only do something if both fields are valid so far.
            for kan in kandydaci:
                if kan in uprawnieni:
                    raise forms.ValidationError(u"Osoba bedaca kandydatem("+kan.__str__().decode('utf-8', 'ignore')+u") nie moze jednocześnie głosować!")

        poczatek=self.cleaned_data.get("od")
        koniec=self.cleaned_data.get("do")

        if poczatek and koniec:
            if koniec<=poczatek:
                raise forms.ValidationError(
                                        _(u'Data zakończenia musi być po dacie rozpoczęcia głosowania'),
                                        code='invalid'
                                        )

        maxG = self.cleaned_data.get('maxGlosow')
        if maxG and kandydaci:
            if maxG>len(kandydaci):
                raise forms.ValidationError(
                                        _(u'Maksymalna liczba głosów nie może być większa od liczby kandydatów'),
                                        code='invalid'
                                        )

        return self.cleaned_data


class EmailChangeForm(forms.Form):
      email1 = forms.EmailField(label='Podaj nowy adres e-mail',required=True,validators=[validate_email_unique])
      email2 = forms.EmailField(label='Powtórz adres e-mail',required=True)

      def clean(self):
        email1=self.cleaned_data.get('email1')
        email2=self.cleaned_data.get('email2')

        if email1 and email2:
            if email1 != email2:
                raise forms.ValidationError(
                                      _(u'Emaile muszą być takie same!'),
                                      code='invalid'
                                          )
        return self.cleaned_data

      def get_mail(self):
          return self.cleaned_data['email1']

class VoteForm(forms.Form):
    # nazwa i opis glosowania + lista kandydatow + wyswietlic max glosow do oddania, walidacja max liczby głosów
    #CheckboxSelectMultiple
    #SelectMultiple(attrs={'size':10,})
#     {% for radio in myform.beatles %}
#     <label for="{{ radio.id_for_label }}">
#         {{ radio.choice_label }}
#         <span class="radio">{{ radio.tag }}</span>
#     </label>
# {% endfor %}
    kandydaci=forms.ModelMultipleChoiceField(queryset=UserProfile.objects.none(),required=True,widget=CheckboxSelectMultiple())
    def __init__(self,*args,**kwargs):
        self.voting = kwargs.pop('voting', None)
        super(VoteForm, self).__init__(*args, **kwargs)

        self.fields["kandydaci"].queryset = self.voting.kandydaci.all()

    def clean_kandydaci(self):
        kan = self.cleaned_data.get('kandydaci',None)
        if kan:
            if len(kan)>self.voting.maxGlosow:
                raise forms.ValidationError(
                                        _(u'Nie możesz zagłosować na  %(value)s osoby/osób, limit to %(limit)s'),
                                        code='invalid',
                                        params={'value': len(kan),'limit':self.voting.maxGlosow},
                                        )
        return kan
    def getVotingResults(self):
        return self.cleaned_data.get('kandydaci',None)