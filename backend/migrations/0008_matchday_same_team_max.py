# Generated by Django 3.2.8 on 2023-01-23 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_rankingscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchday',
            name='same_team_max',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
