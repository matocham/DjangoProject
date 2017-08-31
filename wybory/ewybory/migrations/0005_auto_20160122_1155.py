# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ewybory', '0004_auto_20151122_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='maxGlosow',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
