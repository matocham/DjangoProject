# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ewybory', '0003_auto_20151118_1421'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='Glosowania',
            new_name='glosowanie',
        ),
        migrations.RenameField(
            model_name='candidate',
            old_name='Osoby',
            new_name='osoba',
        ),
        migrations.RenameField(
            model_name='voter',
            old_name='Glosowania',
            new_name='glosowanie',
        ),
        migrations.RenameField(
            model_name='voter',
            old_name='Osoby',
            new_name='osoba',
        ),
    ]
