# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20180706_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='alipay_qrcode_path',
            field=models.ImageField(blank=True, upload_to='/alipay_qrcode'),
        ),
        migrations.AddField(
            model_name='user',
            name='wechat_qrcode_path',
            field=models.ImageField(blank=True, upload_to='/wechat_qrcode'),
        ),
    ]
