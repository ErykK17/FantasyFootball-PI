# Generated by Django 3.2.8 on 2023-01-23 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_alter_myfootballer_footballer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myfootballer',
            name='footballer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.footballer'),
        ),
    ]