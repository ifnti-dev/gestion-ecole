# Generated by Django 4.2.7 on 2023-12-04 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorrespondanceMaquette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature', models.CharField(choices=[('U', 'UE'), ('M', 'Matière')], max_length=1)),
                ('ancienne', models.IntegerField(blank=True, null=True)),
                ('nouveau', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]