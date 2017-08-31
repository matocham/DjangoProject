from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login,logout,password_change,password_change_done

handler404 = 'ewybory.views.handler404'

urlpatterns = patterns('',
    url(r'register$','ewybory.views.register'),
    url(r'addVoting$','ewybory.views.addVoting'),
    url(r'login$',login,{'template_name':'login.html'},name = 'login'),
    url(r'logout$',logout,{'template_name':'logoutSuccess.html'},name='logout'),
    url(r'myVotings$','ewybory.views.myVotings',name='myVotings'),
    url(r'participate$','ewybory.views.participate',name='participate'),
    url(r'votings$','ewybory.views.vote',name='vote'),
    url(r'voting/(?P<vot_id>\d+)/detail$','ewybory.views.voting_details',name='votingDetails'),
    url(r'voting/(?P<vot_id>\d+)/edit$','ewybory.views.voting_edit',name='votingEdit'),
    url(r'voting/(?P<vot_id>\d+)/resign$','ewybory.views.voting_resign',name='votingResign'),
    url(r'voting/(?P<vot_id>\d+)/delete$','ewybory.views.voting_delete',name='votingDelete'),
    url(r'voting/(?P<vot_id>\d+)/summary$','ewybory.views.voting_summary',name='votingSummary'),
    url(r'voting/(?P<vot_id>\d+)/vote$','ewybory.views.voting_vote',name='vote'),
    url(r'passwordChange$',password_change,{'template_name':'passChange.html'},name='passChange'),
    url(r'passSuccess$',password_change_done,{'template_name':'changeSuccess.html'},name='password_change_done'),
    url(r'emailChange$','ewybory.views.email_change',name='emailChange'),
    url(r'accountDetails$','ewybory.views.account_details',name='accountDetails'),
    url(r'(?P<vot_id>\d+)/pdf$', 'ewybory.views.report', name='pdf'),
    url(r'home$', 'ewybory.views.home', name='homepage'),
)
