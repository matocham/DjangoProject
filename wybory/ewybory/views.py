# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response,render,redirect,get_object_or_404
from models import UserProfile,Voter,Candidate,Voting
from forms import UserProfileForm,UserRegForm,VotingForm,EmailChangeForm,VoteForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.template import RequestContext
from django.utils import timezone
from django.db.models import Max
from reportlab.pdfgen import canvas
from django.db.models import Q
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html',context_instance=RequestContext(request))

def register(request):
    if request.user.is_authenticated():
        return redirect("/ewybory/home")
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserProfileForm(request.POST)
        form2 = UserRegForm(request.POST);
        # check whether it's valid:
        if form.is_valid() and form2.is_valid():
            usprof = form.save(commit=False)
            usr = form2.save();
            usprof.user=usr;
            usprof.save();
            return render(request, 'registerSuccess.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserProfileForm()
        form2 = UserRegForm();
    return render(request, 'register.html', {'regform': form, 'reg1form':form2})

@login_required(login_url='/ewybory/login')
def addVoting(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VotingForm(request.POST,user=request.user)
        # check whether it's valid:
        if form.is_valid():
            vot = form.save(commit=False);
            vot.moderator = UserProfile.objects.filter(user=request.user)[0]
            vot.save() ## zrobic zapisywanie wiele do wielu
            for k in form.cleaned_data['kandydaci']:
                kan = Candidate(glosowanie=vot,osoba=k)
                kan.save()

            for u in form.cleaned_data['uprawnieni']:
                upr = Voter(glosowanie=vot,osoba=u)
                upr.save()

            #form.save_m2m() ## zamiast tego dodac reczny zapis do bazy
            return render(request, 'AddVotingSuccess.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = VotingForm(user=request.user)
        #form.fields["kandydaci"].queryset = UserProfile.objects.exclude(user=request.user) ##modyfikujemy liste kandydatow
    return render(request, 'addVoting.html', {'regform': form,})

@login_required(login_url='/ewybory/login')
def myVotings(request):
    votings = UserProfile.objects.get(user=request.user).myVotings.all().order_by('od')
    return render(request, 'myVotings.html', {'votings': votings,'now':timezone.now().date()})
# @login_required(login_url='/login')
# def logoutUser(request):
#     logout(request)
#     return redirect('')

@login_required(login_url='/ewybory/login')
def participate(request):
    votings = Voting.objects.filter(kandydaci__user= request.user).order_by('od')
    return render(request, 'participate.html', {'votings': votings,'now':timezone.now().date()})

@login_required(login_url='/ewybory/login')
def vote(request):
    votings = Voting.objects.filter(uprawnieni__user= request.user,od__lte =timezone.now().date()).order_by('od') # zmiana na date()
    for vot in votings:
        #dodanie nowego pola do obiektu glosowania - alternatywnie mozna stworzyc slownik lub liste krotek
        vot.v=Voter.objects.get(osoba__user=request.user,glosowanie = vot)
    return render(request, 'votings.html', {'votings': votings,'now':timezone.now().date()})

@login_required(login_url='/ewybory/login')
def email_change(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmailChangeForm(request.POST)
        # check whether it's valid:

        if form.is_valid():

            user = request.user
            user.email=form.get_mail()
            user.save()
            #dodac zwrocenie normalnej odpowiedzi
            return render(request, 'mailChangeSuccess.html')
       # else:
        #    return HttpResponse('emial change error!'+form.errors.__str__()+" "+User.objects.values("email").__str__())
    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmailChangeForm()
    return render(request, 'changeEmail.html', {'form': form,})

@login_required()
def voting_details(request,vot_id):
    voting = get_object_or_404(Voting, pk=vot_id)
    resp = None
    #uzytkownik moze zobaczyc tylko swoje glosowanie
    if voting.moderator.user == request.user:
         resp=voting
     #lub glosowanie, w korym bierze udzial jako kandydat
    elif voting.kandydaci.filter(user=request.user).exists():
            resp=voting
    #lub glosowanie, w kotorym bierze udzial jako uprawniony i sie juz rozpoczelo
    else:
        time = timezone.now().date()
        logger.error(time)
        if voting.uprawnieni.filter(user=request.user).exists() and voting.od<=time:
            resp = voting
    return render(request, 'votingDetails.html', {'voting': resp})

@login_required()
def voting_edit(request,vot_id):
    #zabezpieczenie przed edycja glosowanie juz rozpoczetego oraz glosowania,ktorego nie jestesmy wlascicielami
    voting = get_object_or_404(Voting, pk=vot_id,moderator__user=request.user,od__gt =timezone.now().date()) #zmiana na date()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VotingForm(request.POST,instance=voting,user=request.user)
        # check whether it's valid:
        if form.is_valid():

            vot = form.save(commit=False);
            vot.save()
            vot.candidate_set.all().delete()
            vot.voter_set.all().delete()

            for k in form.cleaned_data['kandydaci']:
                kan = Candidate(glosowanie=vot,osoba=k)
                kan.save()

            for u in form.cleaned_data['uprawnieni']:
                upr = Voter(glosowanie=vot,osoba=u)
                upr.save()

            #form.save_m2m() ## zamiast tego dodac reczny zapis do bazy
            return render(request, 'editVotingSuccess.html')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = VotingForm(instance=voting,user=request.user)
        #form.fields["kandydaci"].queryset = UserProfile.objects.exclude(user=request.user) ##modyfikujemy liste kandydatow
    return render(request, 'editVoting.html', {'regform': form,'vot_id':voting.id})


@login_required()
def account_details(request):
    return render(request, 'userDetails.html')

@login_required()
def voting_resign(request,vot_id):
    voting = get_object_or_404(Voting, pk=vot_id, od__gt =timezone.now().date() ) #zmiana na date()
    message=''

    # jezeli mamy tyle mozliwych glosow co kandydatow to musimy zmienjszyc liczbe glosow do oddania
    if voting.kandydaci.filter(user=request.user).exists():
        if voting.candidate_set.all().count() == voting.maxGlosow:
            voting.maxGlosow=voting.maxGlosow-1;
            voting.save();

        voting.candidate_set.get(osoba__user=request.user).delete()
        message=u'Pomyślnie wypisałeś się z głosowania '+voting.nazwa
        #próbujemy poinformować moderatora, że osoba zrezygnowała z jego głosowania

        if not voting.kandydaci.all().exists():
            voting.delete()
            message+=u' Ponieważ byłeś jedynym kandydatem, głosowanie to nie będzie dłuzej dostępne w serwisie'
    else:
        message = u'Nie możesz wypisać się z głosowania, w którym nie bierzesz udziału'
    return render(request, 'resign.html', {'message': message})

def voting_delete(request,vot_id):
    voting = get_object_or_404(Voting,Q(od__gt =timezone.now().date())|Q(do__lt =timezone.now().date()), pk=vot_id,moderator__user=request.user) # zmiana na date x2
    voting.delete()
    return render(request, 'votingDelete.html', {'name': voting.nazwa,})

def voting_summary(request,vot_id):
    #pobranie głosowania z przeszłą datą zakończenia
    voting = get_object_or_404(Voting, pk=vot_id,do__lt = timezone.now().date()) #zmiana na date()
    mozna=False
    #sprawdzenie czy osoba,ktora chce zobaczyc głosowanie jest do tego uprawniona
    # moderator,głosujący lub kandydat
    if voting.moderator.user== request.user or voting.uprawnieni.filter(user=request.user).exists() or \
    voting.kandydaci.filter(user=request.user).exists():
    #przygotowanie statystyk
        wszyscy = voting.uprawnieni.count()
        zaglosowali = voting.voter_set.filter(zaglosowal=True,glosowanie = voting).count()
        maxG = voting.candidate_set.all().aggregate(Max('wynik'))
        zwyciezcy = voting.candidate_set.filter(wynik=maxG['wynik__max'])
        return render(request, 'votingSummary.html', {'v_count': wszyscy,'voted_count': zaglosowali,'voting': voting,'winners': zwyciezcy})
    else:
        return render(request, 'votings.html')

@login_required()
def voting_vote(request,vot_id):
    voting = get_object_or_404(Voting, pk=vot_id,uprawnieni__user=request.user,od__lte =timezone.now().date(),do__gte=timezone.now().date()) #zmiana na date() x2
    if Voter.objects.get(osoba__user=request.user,glosowanie=voting).zaglosowal==True:
        #juz glosowal przekierowujemy na strone bledu
        return render(request, 'voteError.html')
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VoteForm(request.POST,voting=voting)
        # check whether it's valid:
        if form.is_valid():
            # zapisanie oddanych glosow
            for kan in form.getVotingResults():
                k = voting.candidate_set.get(osoba=kan)
                k.wynik=k.wynik+1
                k.save()
            #oddany glos - nie mozna glosowac drugi raz
            us =voting.voter_set.get(osoba=request.user.profile)
            us.zaglosowal=True;
            us.save()
            return render(request, 'voteSuccess.html',{'voting':voting.nazwa})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = VoteForm(voting=voting)
        #form.fields["kandydaci"].queryset = UserProfile.objects.exclude(user=request.user) ##modyfikujemy liste kandydatow
    return render(request, 'vote.html', {'form': form,'vot_id':voting.id})

def handler404(request):
    return render(request,'404.html',status=404)


def report(request,vot_id):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Raport_z_glosowania.pdf"'

    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    p.setFont("Verdana", 8)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(200, 820, u"Raport z głosowania")
    voting = get_object_or_404(Voting, pk=vot_id,do__lt = timezone.now().date()) #zmiana na date()
    #sprawdzenie czy osoba,ktora chce zobaczyc głosowanie jest do tego uprawniona
    # moderator,głosujący lub kandydat
    if voting.moderator.user== request.user or voting.uprawnieni.filter(user=request.user).exists() or \
    voting.kandydaci.filter(user=request.user).exists():
    #przygotowanie statystyk
        wszyscy = voting.uprawnieni.count()
        zaglosowali = voting.voter_set.filter(zaglosowal=True,glosowanie = voting).count()
        maxG = voting.candidate_set.all().aggregate(Max('wynik'))
        zwyciezcy = voting.candidate_set.filter(wynik=maxG['wynik__max'])

        p.drawString(100, 788, u"Nazwa głosowania:")
        p.drawString(100, 776, voting.nazwa)
        p.drawString(100, 760, u"Opis głosowania:")
        p.drawString(100, 748, voting.opis)
        p.drawString(100, 730, u"Głosowanie założył :")
        p.drawString(100, 718, str(voting.moderator.user.get_full_name()))
        p.drawString(100, 700, u"Zakończono: ")
        p.drawString(100, 688, str(voting.do))
        p.drawString(100, 670, u"Uprawnionych do głosowania było: ")
        p.drawString(100, 658, str(wszyscy))
        p.drawString(100, 640, u"Zagłosowało :")
        p.drawString(100, 628, str(zaglosowali))
        p.drawString(100, 610, u"Kandydowało osób: ")
        p.drawString(100, 592, str(voting.candidate_set.count()))
        p.drawString(100, 576, u"Lista kandydatów :")
        kandydacii=u" "
        for k in voting.candidate_set.all():
                kandydacii+= k.osoba.user.get_full_name()+", "
        p.drawString(100, 550, kandydacii)
        p.drawString(100, 500, u"Wygrali :")
        kandydacii=u" "
        for w in zwyciezcy :
            kandydacii+=w.osoba.user.get_full_name()+u" ("+ unicode(w.wynik)+u") głosów, "
        p.drawString(100, 475, kandydacii)
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response