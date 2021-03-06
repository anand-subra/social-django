# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-04 12:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='member',
            name='following',
        ),
        migrations.AddField(
            model_name='friends',
            name='friend1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends_friend1', to='social.Member'),
        ),
        migrations.AddField(
            model_name='friends',
            name='friend2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends_friend2', to='social.Member'),
        ),
        migrations.AddField(
            model_name='friendrequests',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendrequests_recipient', to='social.Member'),
        ),
        migrations.AddField(
            model_name='friendrequests',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendrequests_sender', to='social.Member'),
        ),
    ]
