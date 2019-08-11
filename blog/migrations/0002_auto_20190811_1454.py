# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-08-11 06:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='article',
            name='desc',
            field=models.CharField(max_length=255, verbose_name='文章描述'),
        ),
    ]