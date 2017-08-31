# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ewybory', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='IdGlosowania',
            new_name='Glosowania',
        ),
        migrations.RenameField(
            model_name='candidate',
            old_name='IdOsoby',
            new_name='Osoby',
        ),
        migrations.RenameField(
            model_name='voter',
            old_name='IdGlosowania',
            new_name='Glosowania',
        ),
        migrations.RenameField(
            model_name='voter',
            old_name='IdOsoby',
            new_name='Osoby',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='interaction',
        ),
    ]
