# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ewybory', '0002_auto_20151118_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='pesel',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(regex=b'^\\d{11}$', message=b'Length has to be 11', code=b'nomatch')]),
        ),
    ]
