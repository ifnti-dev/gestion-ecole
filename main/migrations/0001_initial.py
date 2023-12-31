
# Generated by Django 4.1.13 on 2023-12-21 16:30

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnneeUniversitaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee', models.DecimalField(decimal_places=0, max_digits=4, verbose_name='Année universitaire')),
                ('annee_courante', models.BooleanField(default=False, null=True, verbose_name='Année universitaire acutuelle')),
            ],
        ),
        migrations.CreateModel(
            name='CompteBancaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=100, verbose_name='Numéro du compte')),
                ('solde_bancaire', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('frais_tenue_de_compte', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Frais de tenue de compte')),
            ],
        ),
        migrations.CreateModel(
            name='CorrespondanceMaquette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature', models.CharField(choices=[('U', 'UE'), ('M', 'Matière')], max_length=1)),
                ('ancienne', models.CharField(blank=True, max_length=225, null=True)),
                ('nouvelle', models.CharField(blank=True, max_length=225, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Domaine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, verbose_name='Nom')),
                ('description', models.TextField(max_length=500, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50, verbose_name='Prénom')),
                ('sexe', models.CharField(choices=[('F', 'Feminin'), ('M', 'Masculin')], max_length=1)),
                ('datenaissance', models.DateField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(limit_value=datetime.date(2006, 1, 1), message="L'année de naissance doit être inférieure à 2006")], verbose_name='date de naissance')),
                ('lieunaissance', models.CharField(blank=True, max_length=20, null=True, verbose_name='lieu de naissance')),
                ('contact', models.CharField(max_length=25, null=True)),
                ('email', models.CharField(max_length=50, null=True)),
                ('adresse', models.CharField(max_length=50, null=True)),
                ('prefecture', models.CharField(blank=True, default='tchaoudjo', max_length=50, null=True, verbose_name='Préfecture')),
                ('is_active', models.BooleanField(default=True, null=True, verbose_name='Actif')),
                ('carte_identity', models.CharField(max_length=50, null=True, verbose_name="Carte d'identité")),
                ('nationalite', models.CharField(blank=True, default='Togolaise', max_length=30, verbose_name='Nationalté')),
                ('photo_passport', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Photo passport')),
                ('id', models.CharField(blank=True, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('seriebac1', models.CharField(blank=True, choices=[('A', 'A'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'), ('F4', 'F4'), ('G2', 'G2')], max_length=2, null=True, verbose_name='Série bac 1')),
                ('seriebac2', models.CharField(blank=True, choices=[('A', 'A'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'), ('F4', 'F4'), ('G2', 'G2')], max_length=2, null=True, verbose_name='Série bac 2')),
                ('anneeentree', models.IntegerField(blank=True, default=2023, null=True, verbose_name='Promotion')),
                ('anneebac1', models.IntegerField(blank=True, null=True, verbose_name='Année d’obtention du BAC 1')),
                ('anneebac2', models.IntegerField(blank=True, default=2023, null=True, verbose_name='Année d’obtention du BAC 2')),
                ('etablissementSeconde', models.CharField(blank=True, max_length=300, null=True, verbose_name="Nom d'établissement seconde")),
                ('francaisSeconde', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de français Seconde')),
                ('anglaisSeconde', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name="Note d'anglais Seconde")),
                ('mathematiqueSeconde', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de mathématique Seconde')),
                ('etablissementPremiere', models.CharField(blank=True, max_length=300, null=True, verbose_name="Nom d'établissement Première")),
                ('francaisPremiere', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de français Première')),
                ('anglaisPremiere', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name="Note d'anglais Première")),
                ('mathematiquePremiere', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de mathématique Première')),
                ('etablissementTerminale', models.CharField(blank=True, max_length=300, null=True, verbose_name="Nom d'établissement Terminale")),
                ('francaisTerminale', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de français Terminale')),
                ('anglaisTerminale', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name="Note d'anglais Terminale")),
                ('mathematiqueTerminale', models.DecimalField(decimal_places=2, default='0', max_digits=4, verbose_name='Note de mathématique Terminale')),
                ('delegue', models.BooleanField(default=False, null=True, verbose_name='delegué')),
                ('passer_semestre_suivant', models.BooleanField(default=False, verbose_name='Passer au semestre suivant')),
                ('decision_conseil', models.TextField(default='Décision du conseil', null=True, verbose_name='Décision du conseil')),
                ('profil', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Photo de profil')),
            ],
            options={
                'verbose_name': 'Etudiant',
                'verbose_name_plural': 'Etudiants',
            },
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=258, verbose_name='Nom')),
                ('ponderation', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Pondération (1-100)')),
                ('date', models.DateField(verbose_name='Date évaluation')),
                ('rattrapage', models.BooleanField(default=False, verbose_name='Rattrapage')),
            ],
        ),
        migrations.CreateModel(
            name='Parcours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, verbose_name='Nom')),
                ('description', models.TextField(max_length=500, verbose_name='description')),
                ('domaine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.domaine', verbose_name='Domaine')),
            ],
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50, verbose_name='Prénom')),
                ('sexe', models.CharField(choices=[('F', 'Feminin'), ('M', 'Masculin')], max_length=1)),
                ('datenaissance', models.DateField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(limit_value=datetime.date(2006, 1, 1), message="L'année de naissance doit être inférieure à 2006")], verbose_name='date de naissance')),
                ('lieunaissance', models.CharField(blank=True, max_length=20, null=True, verbose_name='lieu de naissance')),
                ('contact', models.CharField(max_length=25, null=True)),
                ('email', models.CharField(max_length=50, null=True)),
                ('adresse', models.CharField(max_length=50, null=True)),
                ('prefecture', models.CharField(blank=True, default='tchaoudjo', max_length=50, null=True, verbose_name='Préfecture')),
                ('is_active', models.BooleanField(default=True, null=True, verbose_name='Actif')),
                ('carte_identity', models.CharField(max_length=50, null=True, verbose_name="Carte d'identité")),
                ('nationalite', models.CharField(blank=True, default='Togolaise', max_length=30, verbose_name='Nationalté')),
                ('photo_passport', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Photo passport')),
                ('id', models.CharField(blank=True, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('salaireBrut', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Salaire Brut')),
                ('dernierdiplome', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Dernier diplome')),
                ('nbreJrsCongesRestant', models.IntegerField(default=0, verbose_name='Nbre jours de congé restant')),
                ('nbreJrsConsomme', models.IntegerField(default=0, verbose_name='Nombre de jours consommé')),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tuteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=20)),
                ('prenom', models.CharField(max_length=20)),
                ('sexe', models.CharField(blank=True, choices=[('F', 'Féminin'), ('M', 'Masculin')], max_length=1)),
                ('adresse', models.CharField(blank=True, max_length=20, verbose_name='Adresse')),
                ('contact', models.CharField(max_length=25)),
                ('profession', models.CharField(blank=True, max_length=20, verbose_name='Profession')),
                ('type', models.CharField(blank=True, choices=[('pere', 'Père'), ('mere', 'Mère'), ('tuteur', 'Tuteur')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Ue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codeUE', models.CharField(max_length=50, verbose_name="Code de l'UE")),
                ('libelle', models.CharField(max_length=100)),
                ('niveau', models.CharField(choices=[('1', 'Licence'), ('2', 'Master'), ('3', 'Doctorat')], max_length=50)),
                ('type', models.CharField(choices=[('Technologie', 'Technologie'), ('Communication', 'Communication'), ('Anglais', 'Anglais'), ('Maths', 'Maths')], max_length=50)),
                ('nbreCredits', models.IntegerField(verbose_name='Nombre de crédit')),
                ('heures', models.DecimalField(blank=True, decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name_plural': 'UE',
            },
        ),
        migrations.CreateModel(
            name='Comptable',
            fields=[
                ('personnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.personnel')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.personnel',),
        ),
        migrations.CreateModel(
            name='DirecteurDesEtudes',
            fields=[
                ('personnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.personnel')),
            ],
            options={
                'verbose_name': 'Directeur des études',
                'verbose_name_plural': 'Directeurs des études',
            },
            bases=('main.personnel',),
        ),
        migrations.CreateModel(
            name='Enseignant',
            fields=[
                ('personnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.personnel')),
                ('type', models.CharField(blank=True, choices=[('Vacataire', 'Vacataire'), ('Permanent', 'Permanent')], max_length=9, null=True)),
                ('specialite', models.CharField(blank=True, max_length=300, null=True, verbose_name='Spécialité')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.personnel',),
        ),
        migrations.CreateModel(
            name='Semestre',
            fields=[
                ('id', models.CharField(blank=True, max_length=14, primary_key=True, serialize=False)),
                ('libelle', models.CharField(choices=[('S1', 'Semestre1'), ('S2', 'Semestre2'), ('S3', 'Semestre3'), ('S4', 'Semestre4'), ('S5', 'Semestre5'), ('S6', 'Semestre6')], max_length=30)),
                ('credits', models.IntegerField(default=30)),
                ('courant', models.BooleanField(default=False, null=True, verbose_name='Semestre actuel')),
                ('annee_universitaire', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.anneeuniversitaire')),
            ],
        ),
        migrations.CreateModel(
            name='Salaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateField(null=True, verbose_name='Date de début')),
                ('date_fin', models.DateField(null=True, verbose_name='Date de fin')),
                ('numero_cnss', models.CharField(default=0, max_length=30, verbose_name='Numéro CNSS')),
                ('qualification_professionnel', models.CharField(choices=[('Enseignant', 'Enseignant'), ('Comptable', 'Comptable'), ('Directeur des études', 'Directeur des études'), ('Gardien', 'Gardien'), ("Agent d'entretien", "Agent d'entretien")], max_length=30, verbose_name='Qualification professionnelle')),
                ('prime_efficacite', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Prime d'éfficacité")),
                ('prime_qualite', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Prime de qualité')),
                ('frais_travaux_complementaires', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Travaux complémentaires')),
                ('prime_anciennete', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Prime d'ancienneté")),
                ('frais_prestations_familiales', models.DecimalField(decimal_places=3, default=0.03, max_digits=10)),
                ('frais_risques_professionnel', models.DecimalField(decimal_places=3, default=0.02, max_digits=10)),
                ('frais_pension_vieillesse_emsalaire', models.DecimalField(decimal_places=3, default=0.125, max_digits=10)),
                ('frais_prestations_familiale_salsalaire', models.DecimalField(decimal_places=3, default=0.04, max_digits=10)),
                ('tcs', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='TCS')),
                ('irpp', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='IRPP')),
                ('is_tcs', models.BooleanField(default=False, null=True)),
                ('is_irpp', models.BooleanField(default=False, null=True)),
                ('prime_forfaitaire', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Prime forfaitaires')),
                ('acomptes', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Acomptes')),
                ('salaire_net_a_payer', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Salaire Net à payer')),
                ('annee_universitaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire', verbose_name='Année Universitaire')),
                ('compte_bancaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.comptebancaire')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.personnel')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valeurNote', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(0.0)], verbose_name='note')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.etudiant', verbose_name='Étudiant')),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.evaluation', verbose_name='Evaluation')),
            ],
        ),
        migrations.CreateModel(
            name='Matiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codematiere', models.CharField(max_length=50, verbose_name='Code de la matière')),
                ('libelle', models.CharField(max_length=100)),
                ('coefficient', models.IntegerField(default='1', null=True, verbose_name='Coefficient')),
                ('minValue', models.FloatField(default='7', null=True, verbose_name='Valeur minimale')),
                ('heures', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('ue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ue')),
                ('enseignant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.enseignant', verbose_name='Enseignants responsable')),
            ],
            options={
                'verbose_name_plural': 'Matières',
            },
        ),
        migrations.CreateModel(
            name='Frais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_inscription', models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Frais d'inscription")),
                ('montant_scolarite', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Frais de scolarité')),
                ('annee_universitaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire')),
            ],
        ),
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('TDE', 'TDE'), ('CEET', 'CEET'), ('Espoir+', 'Espoir+'), ('Autres', 'Autres')], max_length=30)),
                ('montant', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Montant versé')),
                ('dateversement', models.DateField(default=django.utils.timezone.now, verbose_name='Date de versement')),
                ('le_mois', models.CharField(choices=[('Janvier', 'Janvier'), ('Février', 'Février'), ('Mars', 'Mars'), ('Avril', 'Avril'), ('Mai', 'Mai'), ('Juin', 'Juin'), ('Juillet', 'Juillet'), ('Août', 'Août'), ('Septembre', 'Septembre'), ('Octobre', 'Octobre'), ('Novembre', 'Novembre'), ('Décembre', 'Décembre')], max_length=30, verbose_name='Mois')),
                ('annee_universitaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire', verbose_name='Année Universitaire')),
                ('compte_bancaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.comptebancaire')),
            ],
        ),
        migrations.AddField(
            model_name='evaluation',
            name='etudiants',
            field=models.ManyToManyField(through='main.Note', to='main.etudiant', verbose_name='Étudiants'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='matiere',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.matiere', verbose_name='Matiere'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='semestre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.semestre'),
        ),
        migrations.AddField(
            model_name='etudiant',
            name='semestres',
            field=models.ManyToManyField(to='main.semestre'),
        ),
        migrations.AddField(
            model_name='etudiant',
            name='tuteurs',
            field=models.ManyToManyField(blank=True, null=True, related_name='Tuteurs', to='main.tuteur'),
        ),
        migrations.AddField(
            model_name='etudiant',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Conge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature', models.CharField(choices=[('Congé annuel', 'Congé annuel'), ('Congé de maternité', 'Congé de maternité'), ('Congé de paternité', 'Congé de paternité'), ('autres', 'Autres')], max_length=30, verbose_name='Nature des congés')),
                ('date_et_heure_debut', models.DateField(default=django.utils.timezone.now, verbose_name='Date de début')),
                ('date_et_heure_fin', models.DateField(default=django.utils.timezone.now, verbose_name='Date de fin')),
                ('motif_refus', models.TextField(blank=True, null=True, verbose_name='Motif de refus')),
                ('valider', models.CharField(choices=[('Actif', 'Actif'), ('Inactif', 'Inactif'), ('Inconnu', 'Inconnu')], default='Inconnu', max_length=30, verbose_name='État')),
                ('nombre_de_jours_de_conge', models.IntegerField(default=0)),
                ('annee_universitaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire', verbose_name='Année Universitaire')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.personnel', verbose_name='Personnel')),
            ],
        ),
        migrations.CreateModel(
            name='CompteEtudiant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solde', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('annee_universitaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.etudiant')),
            ],
        ),
        migrations.CreateModel(
            name='Competence',
            fields=[
                ('id', models.CharField(blank=True, max_length=30, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100)),
                ('libelle', models.CharField(max_length=100)),
                ('matiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.matiere', verbose_name='Matiere')),
                ('ue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ue', verbose_name='UE')),
            ],
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateDebut', models.DateField(null=True, verbose_name='Date de début')),
                ('dateFin', models.DateField(null=True, verbose_name='Date de fin')),
                ('frais_de_vie', models.IntegerField(default=0, verbose_name='Frais de vie')),
                ('frais_nourriture', models.IntegerField(default=0, verbose_name='Frais de nourriture')),
                ('montant', models.IntegerField(default=0, verbose_name='Montant')),
                ('montantEnLettre', models.CharField(default='lettres', max_length=100, verbose_name='Montant en lettre')),
                ('annee_universitaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire', verbose_name='Année Universitaire')),
                ('compte_bancaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.comptebancaire')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.personnel', verbose_name='Personnel')),
            ],
        ),
        migrations.AddField(
            model_name='ue',
            name='enseignant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.enseignant', verbose_name='Enseignant responsable'),
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parcours', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.parcours', verbose_name='Parcours')),
                ('semestre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.semestre', verbose_name='Semestre')),
                ('ues', models.ManyToManyField(to='main.ue', verbose_name='UE')),
            ],
            options={
                'unique_together': {('parcours', 'semestre')},
            },
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Frais de scolarité', 'Frais de scolarité'), ("Frais d'inscription", "Frais d'inscription")], max_length=30)),
                ('montant', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Montant versé')),
                ('dateversement', models.DateField(default=django.utils.timezone.now, verbose_name='Date de versement')),
                ('numerobordereau', models.CharField(default=0, max_length=30, verbose_name='Numéro de bordereau')),
                ('annee_universitaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire')),
                ('compte_bancaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.comptebancaire')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.etudiant', verbose_name='Etudiant')),
                ('comptable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.comptable', verbose_name='Comptable')),
            ],
        ),
        migrations.CreateModel(
            name='Information',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numeroSecurite', models.IntegerField(verbose_name='Numéro de sécurité sociale')),
                ('niveau', models.CharField(choices=[('Premier', 'Niveau 1'), ('Deuxième', 'Niveau 2'), ('Troisième', 'Niveau 3')], max_length=100, verbose_name='Niveau')),
                ('dateDebut', models.DateField(verbose_name='Date de début')),
                ('dateFin', models.DateField(verbose_name='Date de fin')),
                ('duree', models.CharField(default='0', max_length=100, verbose_name='Durée')),
                ('discipline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.matiere', verbose_name='Discipline')),
                ('directeur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.directeurdesetudes', verbose_name='Directeur des études')),
                ('enseignant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.enseignant', verbose_name='Enseigant')),
            ],
        ),
        migrations.CreateModel(
            name='FicheDePaie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateDebut', models.DateField(null=True, verbose_name='Date de début')),
                ('dateFin', models.DateField(null=True, verbose_name='Date de fin')),
                ('nombreHeureL1', models.IntegerField(default=0, verbose_name="Nombre d'heure L1")),
                ('nombreHeureL2', models.IntegerField(default=0, verbose_name="Nombre d'heure L2")),
                ('nombreHeureL3', models.IntegerField(default=0, verbose_name="Nombre d'heure L3")),
                ('nombreHeure', models.IntegerField(default=0, verbose_name="Nombre d'heure")),
                ('prixUnitaire', models.IntegerField(default=0, verbose_name='Prix unitaire')),
                ('montantL1', models.IntegerField(default=0, verbose_name='montant L1')),
                ('montantL2', models.IntegerField(default=0, verbose_name='montant L2')),
                ('montantL3', models.IntegerField(default=0, verbose_name='montant L3')),
                ('montant', models.IntegerField(default=0, verbose_name='montant')),
                ('difference', models.IntegerField(default=0, verbose_name='Différence')),
                ('acomptes', models.IntegerField(default=0, verbose_name='Acomptes')),
                ('montantEnLettre', models.CharField(default='lettres', max_length=100, verbose_name='Montant en lettre')),
                ('annee_universitaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.anneeuniversitaire', verbose_name='Année Universitaire')),
                ('compte_bancaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.comptebancaire')),
                ('matiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.matiere', verbose_name='Matière')),
                ('enseignant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.enseignant', verbose_name='Enseignant')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='etudiant',
            unique_together={('nom', 'prenom', 'datenaissance', 'email')},
        ),
    ]
