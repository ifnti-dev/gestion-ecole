

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Planning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.IntegerField()),
                ('datedebut', models.DateField()),
                ('datefin', models.DateField()),
                ('intervalle', models.CharField(max_length=50, null=True)),
                ('semestre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.semestre')),
            ],
        ),
        migrations.CreateModel(
            name='SeancePlannifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', models.CharField(max_length=200)),
                ('date_heure_debut', models.DateTimeField()),
                ('date_heure_fin', models.DateTimeField()),
                ('precision', models.CharField(max_length=255)),
                ('valider', models.BooleanField(default=False)),
                ('matiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.matiere')),
                ('planning', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='planning.planning')),
                ('professeur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.enseignant')),
            ],
        ),
    ]
