# Generated by Django 4.2.5 on 2023-11-24 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_personnel_salairebrut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='information',
            name='duree',
            field=models.CharField(default='0', max_length=100, verbose_name='Durée'),
        ),
    ]