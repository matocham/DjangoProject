# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wynik', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name=b'profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('pesel', models.CharField(max_length=11)),
                ('interaction', models.PositiveIntegerField(default=0, verbose_name=b'interaction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zaglosowal', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazwa', models.CharField(max_length=100)),
                ('opis', models.CharField(max_length=500)),
                ('maxGlosow', models.PositiveIntegerField(default=0)),
                ('od', models.DateField(default=django.utils.timezone.now, verbose_name=b'poczatek')),
                ('do', models.DateField(verbose_name=b'koniec')),
                ('kandydaci', models.ManyToManyField(related_name=b'participate', through='ewybory.Candidate', to='ewybory.UserProfile')),
                ('moderator', models.ForeignKey(related_name=b'myVotings', to='ewybory.UserProfile')),
                ('uprawnieni', models.ManyToManyField(related_name=b'canVote', through='ewybory.Voter', to='ewybory.UserProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='voter',
            name='IdGlosowania',
            field=models.ForeignKey(to='ewybory.Voting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voter',
            name='IdOsoby',
            field=models.ForeignKey(to='ewybory.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='IdGlosowania',
            field=models.ForeignKey(to='ewybory.Voting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='IdOsoby',
            field=models.ForeignKey(to='ewybory.UserProfile'),
            preserve_default=True,
        ),
    ]
