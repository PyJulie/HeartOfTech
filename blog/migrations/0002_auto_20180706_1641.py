# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='recommend_count',
            field=models.IntegerField(editable=False, default=0),
        ),
        migrations.AddField(
            model_name='recommendlist',
            name='recommend_post',
            field=models.ForeignKey(to='blog.Post'),
        ),
        migrations.AddField(
            model_name='recommendlist',
            name='referee',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
