# Generated by Django 4.1.13 on 2024-01-10 15:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planning',
            name='intervalle',
        ),
        migrations.AddField(
            model_name='planning',
            name='datedebut',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='planning',
            name='datefin',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]