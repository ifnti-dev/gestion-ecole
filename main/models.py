from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from datetime import datetime
import datetime
from django.db.models import Max
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.db.models import Sum  
from num2words import num2words
from decimal import Decimal
from django.db.models import Q


class Utilisateur(models.Model):
    SEXE_CHOISE = [
        ('F', 'Feminin'),
        ('M', 'Masculin')
    ]
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOISE)
    datenaissance = models.DateField(blank=True, verbose_name="date de naissance", null=True, validators=[MaxValueValidator(limit_value=date(2006, 1, 1), message="L'année de naissance doit être inférieure à 2006")])
    lieunaissance = models.CharField(blank=True, max_length=20, verbose_name="lieu de naissance", null=True)
    contact = models.CharField(max_length=25, null=True)
    email = models.CharField(max_length=50, null=True)
    adresse = models.CharField(max_length=50, null=True)
    prefecture = models.CharField(max_length=50, null=True, verbose_name="Préfecture", default='tchaoudjo', blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif", null=True)
    carte_identity = models.CharField(max_length=50, null=True,  verbose_name="Carte d'identité")
    nationalite = models.CharField(max_length=30, default='Togolaise', verbose_name='Nationalté', blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    photo_passport = models.ImageField(null=True, blank=True, verbose_name="Photo passport")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.nom) + ' ' + str(self.prenom)

    def full_name(self):
        return self.nom.upper() + ' ' + self.prenom

    def suspendre(self):
        self.is_active = False
        self.save()

    def reactiver(self):
        self.is_active = True
        self.save()

class Etudiant(Utilisateur):
    id = models.CharField(primary_key=True, blank=True, max_length=12, editable=False)
    CHOIX_SERIE = [('A', 'A'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'),
                   ('F4', 'F4'), ('G2', 'G2')]
    seriebac1 = models.CharField(blank=True, max_length=2, choices=CHOIX_SERIE, verbose_name="Série bac 1", null=True)
    seriebac2 = models.CharField(blank=True, max_length=2, choices=CHOIX_SERIE, verbose_name="Série bac 2", null=True)
    anneeentree = models.IntegerField(default=datetime.date.today().year, blank=True, verbose_name="Promotion", null=True)
    anneebac1 = models.IntegerField(blank=True, verbose_name="Année d’obtention du BAC 1", null=True)
    anneebac2 = models.IntegerField(blank=True, verbose_name="Année d’obtention du BAC 2", null=True, default=datetime.date.today().year)
    etablissementSeconde = models.CharField(max_length=300, verbose_name="Nom d'établissement seconde", null=True, blank=True)
    francaisSeconde = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de français Seconde", default="0")
    anglaisSeconde = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note d'anglais Seconde", default="0")
    mathematiqueSeconde = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de mathématique Seconde", default="0")
    etablissementPremiere = models.CharField(max_length=300, verbose_name="Nom d'établissement Première", null=True, blank=True)
    francaisPremiere = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de français Première", default="0")
    anglaisPremiere = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note d'anglais Première", default="0")
    mathematiquePremiere = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de mathématique Première", default="0")
    etablissementTerminale = models.CharField(max_length=300, verbose_name="Nom d'établissement Terminale", null=True, blank=True)
    francaisTerminale = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de français Terminale", default="0")
    anglaisTerminale = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note d'anglais Terminale", default="0")
    mathematiqueTerminale = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Note de mathématique Terminale", default="0")
    delegue = models.BooleanField(default=False, verbose_name="delegué", null=True)
    passer_semestre_suivant = models.BooleanField(default=False, verbose_name="Passer au semestre suivant")
    decision_conseil = models.TextField(verbose_name="Décision du conseil", null=True, default="Décision du conseil")
    profil = models.ImageField(null=True, blank=True, verbose_name="Photo de profil")
    semestres = models.ManyToManyField('Semestre')
    tuteurs = models.ManyToManyField('Tuteur', related_name="Tuteurs", blank=True, null=True)

    class Meta:
        verbose_name = "Etudiant"
        verbose_name_plural = "Etudiants"
        unique_together = [["nom", "prenom", "datenaissance", "email"]]


    def generate_email(self):
        prenoms = "-".join(self.prenom.split()).lower()
        return f"{prenoms}.{self.nom.lower()}@ifnti.com"

    """ Cléf de l'étudiant"""
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            list_etudiants = Etudiant.objects.filter(
                anneeentree=self.anneeentree)
            if list_etudiants:
                n = 1
                rang = "0" + str(len(list_etudiants) + n) if len(
                    list_etudiants) + n < 10 else str(
                    len(list_etudiants) + n)
                val_id = self.nom[0] + self.prenom[0] + \
                    str(self.anneeentree) + rang
                for i in [etud.id for etud in list_etudiants]:
                    if val_id == i:
                        n = n + 1
                        rang = "0" + str(len(list_etudiants) + n) if len(
                            list_etudiants + n) < 10 else str(
                            len(list_etudiants) + n)
                        val_id = self.nom[0] + self.prenom[0] + \
                            str(self.anneeentree) + rang
                self.id = val_id
            else:
                self.id = self.nom[0] + self.prenom[0] + \
                    str(self.anneeentree) + "0" + str(1)
            # Création de l'utilisateur associé à l'instance de l'étudiant
            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(username=username, password=password,
                                            email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=False)
            self.user = user  # association de l'utilisateur à l'instance de l'étudiant
            group_etudiant = Group.objects.get(name="etudiant")
            self.user.groups.add(group_etudiant)
           
        self.email = self.generate_email()
        super().save()

    def get_semestre_courant(self):
        semestre = self.semestres.filter(courant=True)
        if semestre:
            return semestre

    def get_niveau_annee(self, annee_universitaire):
        semestres = self.semestres.filter(
            annee_universitaire=annee_universitaire)
        semestres_libelle = [semestre.libelle for semestre in semestres]
        niveau = ""
        if 'S1' in semestres_libelle or 'S2' in semestres_libelle:
            niveau = "L1"
        elif 'S3' in semestres_libelle or 'S4' in semestres_libelle:
            niveau = "L2"
        if 'S5' in semestres_libelle or 'S6' in semestres_libelle:
            niveau = "L3"

        return niveau, semestres

    def moyenne_etudiant_matieres(self, semestre):
        result = []
        programmes = Programme.objects.filter(semestre=semestre)
        if not programmes:
            return []
        programme = programmes.get()
        ues = programme.ues.all()
        matieres = set()
        for ue in ues:
            matieres.update(ue.matiere_set.all())
        
        for matiere in matieres:
            moyenne, a_valider = self.moyenne_etudiant_matiere(matiere, semestre)
            #print(moyenne, a_valider)
            result.append({
                'matiere' : matiere.libelle,
                'moyenne' : moyenne,
                'a_valider' : a_valider
            })
        return result
    
    def notes_etudiant_matiere(self, matiere, semestre):
        """_summary_
        Returns:
            _type_: _description_
        """
        # Verifier si l'étudiant suis cette matiere
        # Récupérerer toute les évaluations de l'étuidant dans cette matière
        evaluations = Evaluation.objects.filter(matiere=matiere, rattrapage=False, semestre=semestre)
        if not evaluations:
            return []

        result = []
        for evaluation in evaluations:
            _result = {}
            notes = evaluation.note_set.filter(etudiant=self)
            if notes:
                note = notes.get()
                _result['evaluation'] = evaluation.libelle
                _result['valeur'] = note.valeurNote
                result.append(_result)
        return result


    def moyenne_etudiant_matiere(self, matiere, semestre):
        """_summary_
        Returns:
            _type_: _description_
        """
        # Verifier si l'étudiant suis cette matiere
        # Récupérerer toute les évaluations de l'étuidant dans cette matière
        evaluations = Evaluation.objects.filter(
            matiere=matiere, rattrapage=False, semestre=semestre)
        if not evaluations:
            return 0, 0

        note_ponderation = {}
        somme = 0
        for evaluation in evaluations:
            notes = evaluation.note_set.filter(etudiant=self)
            if notes:
                note = notes.get()
                somme += note.valeurNote * evaluation.ponderation
                note_ponderation[evaluation.libelle] = (note, evaluation.ponderation)
        moyenne = somme/100
        a_valide = moyenne >= matiere.minValue
        return moyenne, a_valide

    def moyenne_etudiant_ue(self, ue, semestre):
        moyenne = 0
        somme_note = 0
        somme_coef = 0
        matieres = ue.matiere_set.all()

        if not matieres:
            return 0.0, False
        
        for matiere in matieres:
            print(matiere, matiere.coefficient)
            note, _ = self.moyenne_etudiant_matiere(matiere, semestre)
            somme_note += float(note) * float(matiere.coefficient)
            somme_coef += matiere.coefficient
            print('sous-total ',somme_coef)
        print('total', somme_coef)
        moyenne = round(somme_note/somme_coef, 2)
        matiere_principale = ue.matiere_principacle()
        a_valide = moyenne >= matiere_principale.minValue
        return moyenne, a_valide


# Calcule le nombre de crédits obtenus par l'étudiant dans un semestre donné.


    def credits_obtenus_semestre(self, semestre):
        credits_obtenus = 0

        # Récupérer tous les programmes liés à ce semestre
        programme = Programme.objects.get(semestre=semestre)  
 
        for ue in programme.ues.all():
            # Calculer la moyenne de l'UE
            moyenne_ue, a_valide_ue = self.moyenne_etudiant_ue(ue, semestre)

            # Si l'étudiant a validé l'UE, ajouter les crédits de l'UE aux crédits obtenus
            if a_valide_ue:
                credits_obtenus += ue.nbreCredits
        return credits_obtenus

    @staticmethod
    def get_Ln(semestres, annee_universitaire=None):
        """ 
        semestre : liste de chaîne de caractère
        annee_universitaire : instance de la classe AnneUniversitaire
        """
        if not annee_universitaire:
            annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestres_pk = [
            f'{semestre}-{annee_universitaire.annee}' for semestre in semestres]
        
        programmes = Programme.objects.filter(semestre__in=semestres_pk)
        print(programmes)

        if programmes:
            semestres = set()
            for programme in programmes:
                semestres.update([programme.semestre])

            etudiants = set()
            for semestre in semestres:
                etudiants.update(semestre.etudiant_set.all())
            return list(etudiants), semestres
        return [], []

    @staticmethod
    def get_etudiants_semestre(semestre, id_annee_selectionnee=None):
        """ 
        semestre : chaîne de caractère
        id_annee_selectionnee : entier
        """
        try:
            annee_universitaire = AnneeUniversitaire.objects.get(
                id=id_annee_selectionnee)
            semestre_id = f'{semestre}-{annee_universitaire.annee}'
            semestre = Semestre.objects.get(id=semestre_id)
            return semestre.etudiant_set.all()
        except:
            return []

    @staticmethod
    def static_get_L1(annee=None, semestres=['S1', 'S2']):
        if not annee:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestres_pk = [f'{semestre}-{annee.annee}' for semestre in semestres]

        programmes = Programme.objects.filter(semestre__pk__in=semestres_pk)

        semestres = set()
        for programme in programmes:
            semestres.update([programme.semestre])

        etudiants = set()
        for semestre in semestres:
            etudiants.update(semestre.etudiant_set.all())
        return list(etudiants), semestres

    @staticmethod
    def static_get_L2(annee=None, semestres=['S3', 'S4']):
        if not annee:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestres_pk = [f'{semestre}-{annee.annee}' for semestre in semestres]

        programmes = Programme.objects.filter(semestre__pk__in=semestres_pk)
        semestres = set()
        for programme in programmes:
            semestres.update([programme.semestre])

        etudiants = set()
        for semestre in semestres:
            etudiants.update(semestre.etudiant_set.all())
        return list(etudiants), semestres

    @staticmethod
    def static_get_L3(annee=None, semestres=['S5', 'S6']):
        if not annee:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestres_pk = [f'{semestre}-{annee.annee}' for semestre in semestres]

        programmes = Programme.objects.filter(semestre__pk__in=semestres_pk)
        semestres = set()
        for programme in programmes:
            semestres.update([programme.semestre])

        etudiants = set()
        for semestre in semestres:
            etudiants.update(semestre.etudiant_set.all())
        return list(etudiants), semestres

    def get_semestres(self, type='courant', annee=None):
        if not annee:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
        if type == 'tous':
            semestre = self.semestres.all()
        elif type == 'courant':
            semestre = self.semestres.filter(
                courant__in=[True], annee_universitaire=annee)
        return semestre

    def __str__(self):
        str_sem = "|".join([sem.id for sem in self.semestres.all()])
        return self.user.username

    def create_compte_etudiant(self):
        # Récupérez l'année universitaire courante
        annee_universitaire_courante = AnneeUniversitaire.objects.get(annee_courante=True)

    # Créez un compte étudiant associé à l'année universitaire courante
        CompteEtudiant.objects.create(etudiant=self, annee_universitaire=annee_universitaire_courante, solde=0)

@receiver(post_save, sender=Etudiant)
def create_compte_etudiant(sender, instance, created, **kwargs):
    if created:
        instance.create_compte_etudiant()


class Personnel(Utilisateur):
    id = models.CharField(primary_key=True, blank=True, max_length=12, editable=False)
    salaireBrut = models.DecimalField(max_digits=15, decimal_places=2,  verbose_name="Salaire Brut", default=0)
    dernierdiplome = models.ImageField(null=True, blank=True, verbose_name="Dernier diplome")
    nbreJrsCongesRestant = models.IntegerField(verbose_name="Nbre jours de congé restant", default=0)
    nbreJrsConsomme = models.IntegerField(verbose_name="Nombre de jours consommé", default=0)

    
    def save(self):
        print(f'----{self.id}----')
        if self.id == "" or self.id == None:
            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(
                username=username, password=password)
            self.user = user

        super().save()

    def update_conge_counts(self):
        conges_pris = Conge.objects.filter(personnel=self)
        total_jours_pris = conges_pris.aggregate(total=Sum('nombre_de_jours_de_conge'))['total'] or 0

        self.nbreJrsConsomme = total_jours_pris
        self.nbreJrsCongesRestant = 30 - total_jours_pris 
        self.save()



class DirecteurDesEtudes(Personnel):
   # actif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            directeurs = DirecteurDesEtudes.objects.all()
            if directeurs:
                raise ValidationError(
                    "Il ne peut y avoir qu'un seul directeur des études.")
            
            self.id = self.nom[0] + self.prenom[0] + "0" + str(1)
            username = (self.prenom[0] + self.nom).lower()
            password = "ifnti2023!"  # Définir le mot de passe souhaité
            user = User.objects.create_user(username=username, password=password,
                                            email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=True)
            self.user = user
            # association de l'utilisateur à l'instance de l'étudiant
            group_directeur = Group.objects.get(name="directeur_des_etudes")
            self.user.groups.add(group_directeur)

        if self.is_active:
            # Désactiver les autres directeurs des études
            DirecteurDesEtudes.objects.exclude(pk=self.pk).update(is_active=False)

        return super().save(*args, **kwargs)



    def delete(self, *args, **kwargs):
        if self.actif:
            raise ValidationError(
                "Le directeur des études actif ne peut pas être supprimé.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.prenom + " " + self.nom

    class Meta:
        verbose_name = "Directeur des études"
        verbose_name_plural = "Directeurs des études"

class Enseignant(Personnel):
    CHOIX_TYPE = (('Vacataire', 'Vacataire'), ('Permanent', 'Permanent'))
    type = models.CharField(null=True, blank=True,max_length=9, choices=CHOIX_TYPE)
    specialite = models.CharField(max_length=300, verbose_name="Spécialité", blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            enseignants = Enseignant.objects.all()
            if enseignants:
                n = 1
                rang = "0" + str(len(enseignants) + n) if len(enseignants) + n < 10 else str(len(enseignants) + n)
                val_id = self.nom[0] + self.prenom[0] + rang
                for i in [ens.id for ens in enseignants]:
                    if val_id == i:
                        n = n + 1
                        rang = "0" + str(len(enseignants) + n) if len(enseignants + n) < 10 else str(len(enseignants) + n)
                        val_id = self.nom[0] + self.prenom[0] + rang
                self.id = val_id
            else:
                self.id = self.nom[0] + self.prenom[0] + "0" + str(1)

            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(username=username, password=password, email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=False)
            self.user = user  
            group_enseignant = Group.objects.get(name="enseignant")
            self.user.groups.add(group_enseignant)
        super().save()


     
    def niveaux(self):
        matieres = self.matiere_set.all()
        niveaux = set()
        for matiere in matieres:
            result = matiere.ue.programme_set.values('semestre')
            temp_semstres_libelles = [ AnneeUniversitaire.getNiveau(elt['semestre'][:2]) for elt in result ]
            niveaux.update(temp_semstres_libelles)
            
        return list(niveaux)
    
    def __str__(self):
        return f'{super().__str__()}'
        #return f'{self.user.username}'

 
class Comptable(Personnel):
    pass

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            Comptables = Comptable.objects.all()
            if Comptables:
                n = 1
                rang = "0" + str(len(Comptables) + n) if len(Comptables) + n < 10 else str(len(Comptables) + n)
                val_id = self.nom[0] + self.prenom[0] + rang
                for i in [comp.id for comp in Comptables]:
                    if val_id == i:
                        n = n + 1
                        rang = "0" + str(len(Comptables) + n) if len(Comptables + n) < 10 else str(len(Comptables) + n)
                        val_id = self.nom[0] + self.prenom[0] + rang
                self.id = val_id
            else:
                self.id = self.nom[0] + self.prenom[0] + "0" + str(1)

            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(username=username, password=password, email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=False)
            self.user = user  
            group_comptable = Group.objects.get(name="comptable")
            self.user.groups.add(group_comptable)
        super().save()



class Tuteur(models.Model):
    CHOIX_SEX = [
        ("F", "Féminin"),
        ("M", "Masculin")
    ]
    CHOIX_TYPE = [
        ("pere", "Père"),
        ("mere", "Mère"),
        ("tuteur", "Tuteur"),
    ]
    nom = models.CharField(max_length=20)
    prenom = models.CharField(max_length=20)
    sexe = models.CharField(blank=True, max_length=1, choices=CHOIX_SEX)
    adresse = models.CharField(
        blank=True, max_length=20, verbose_name="Adresse")
    contact = models.CharField(max_length=25)
    profession = models.CharField(
        blank=True, max_length=20, verbose_name="Profession")
    type = models.CharField(blank=True, max_length=20, choices=CHOIX_TYPE)
   
    def save(self):
        # print(self.id)
        if self.id == None:
            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(
                username=username, password=password)
            self.user = user

        return super().save()

    def __str__(self):
        return self.nom + " " + self.prenom


class Ue(models.Model):
    codeUE = models.CharField(max_length=50, verbose_name="Code de l'UE")
    libelle = models.CharField(max_length=100)
    TYPES = [
        ("Technologie", "Technologie"),
        ("Communication", "Communication"),
        ("Anglais", "Anglais"),
        ("Maths", "Maths"),
    ]
    TYPES_NIVEAU = [
        ("1", "Licence"),
        ("2", "Master"),
        ("3", "Doctorat")
    ]
    niveau = models.CharField(max_length=50, choices=TYPES_NIVEAU)
    type = models.CharField(max_length=50, choices=TYPES)
    nbreCredits = models.IntegerField(verbose_name="Nombre de crédit")
    heures = models.DecimalField(
        blank=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(1)])
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant responsable", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'UE'

    def matiere_principacle(self):
        max_coef = self.matiere_set.all().aggregate(
            Max('coefficient'))['coefficient__max']
        matiere = self.matiere_set.filter(coefficient=max_coef)
        if matiere:
            return matiere.first()
        return None

    def __str__(self):
        return self.codeUE + " " + self.libelle


@receiver(post_save, sender=Ue)
def generate_ue_code(sender, instance, created, **kwargs):
    if created and not instance.codeUE:
        semestre = "0"
        if instance.type == "Technologie":
            type_abbr = "INF"
        else:
            type_abbr = instance.type[:3].upper()

        ue_count = Ue.objects.filter(type=instance.type).count()
        ue_count_str = str(ue_count).zfill(2)

        # Déconnectez le signal post_save temporairement
        post_save.disconnect(generate_ue_code, sender=Ue)

        instance.codeUE = f"{type_abbr}{instance.niveau}{semestre}{ue_count_str}"
        instance.save()

        # Reconnectez le signal post_save après la sauvegarde
        post_save.connect(generate_ue_code, sender=Ue)


class Matiere(models.Model):
    codematiere = models.CharField(max_length=50, verbose_name="Code de la matière")
    libelle = models.CharField(max_length=100)
    coefficient = models.IntegerField(null=True,  verbose_name="Coefficient", default="1")
    minValue = models.FloatField(null=True,  verbose_name="Valeur minimale",  default="7")
    heures = models.DecimalField(blank=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(1)], null=True) 
    enseignant = models.ForeignKey(Enseignant, blank=True, null=True, verbose_name="Enseignants responsable", on_delete=models.CASCADE)
    #enseignants = models.ManyToManyField(Enseignant, related_name="EnseignantsMatiere", blank=True, null=True, verbose_name="Enseignants")
    ue = models.ForeignKey('Ue', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def save(self, *args, **kwargs):
        if not self.codematiere:
            # Calculer le préfixe numérique en fonction de l'ordre des matières dans l'UE
            ordre_matiere = Matiere.objects.filter(ue=self.ue).count() + 1

            # Construire le code de la matière en utilisant le code de l'UE et le préfixe numérique
            self.codematiere = f"{ordre_matiere}{self.ue.codeUE}"

        super(Matiere, self).save(*args, **kwargs)

    def count_evaluations(self, annee, semestres):
        return len(Evaluation.objects.filter(matiere=self, semestre__in=semestres))

    def __str__(self):
        return self.codematiere + " " + self.libelle

    class Meta:
        verbose_name_plural = "Matières"

    def suspendre(self):
        self.is_active = False
        self.save()

    def reactiver(self):
        self.is_active = True
        self.save()

    def ponderation_restante(self, semestre):
        try:
            evaluations = Evaluation.objects.filter(
                matiere=self, rattrapage=False, semestre=semestre)
            ponderation_total = sum(
                [evaluation.ponderation for evaluation in evaluations])
            return 100-ponderation_total
        except:
            return -1

    def is_available_to_add_evaluation(self, semestre):
        return self.ponderation_restante(semestre=semestre) > 0

    def dans_semestre(self, semestre):
        return semestre in self.get_semestres(semestre.annee_universitaire, type="__all__")

    def get_semestres(self, annee_selectionnee, type):
        """
        Cette méthode retourne les semestres d'une matiere
        type : __current__| __all__
        annee_selectionnee : annee_selectionnee | __all__
        # Passer plus tard le parcours
        """
        type_semestres = []
        if type == "__current__":
            type_semestres = [True]
        elif type == "__all__":
            type_semestres = [True, False]
        if annee_selectionnee == '__all__':
            annee_selectionnees = AnneeUniversitaire.objects.all()
        else:
            annee_selectionnees = [annee_selectionnee]

        programmes = self.ue.programme_set.filter(
            semestre__annee_universitaire__in=annee_selectionnees, semestre__courant__in=type_semestres)
        semestres = set()

        for programme in programmes:
            semestres.update([programme.semestre])
        semestres = list(semestres)
        return semestres

    def get_etudiants_en_rattrapage(self):
        etudiants = set()
        semestres = self.get_semestres('__all__', '__all__')
        for semestre in semestres:
            for etudiant in semestre.etudiant_set.all():
                _, a_valide = etudiant.moyenne_etudiant_matiere(self, semestre)
                print(_, a_valide, semestre)
                if not a_valide:
                    etudiants.update([etudiant])
        print(etudiants)
        return list(etudiants)


# class EnseignantsMatiere(models.Model):
#     enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name="Enseignant")
#     matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, verbose_name="Matière")
#     est_responsable = models.BooleanField(verbose_name="Est responsable", default=False)


class Evaluation(models.Model):
    libelle = models.CharField(max_length=258, verbose_name="Nom")
    ponderation = models.IntegerField(
        default=1, verbose_name="Pondération (1-100)", validators=[MinValueValidator(1), MaxValueValidator(100)])
    date = models.DateField(verbose_name="Date évaluation")
    matiere = models.ForeignKey(
        Matiere, on_delete=models.CASCADE, verbose_name='Matiere')
    etudiants = models.ManyToManyField(
        Etudiant, through='Note', verbose_name="Étudiants")
    semestre = models.ForeignKey(
        'Semestre', on_delete=models.CASCADE, null=True)
    rattrapage = models.BooleanField(verbose_name="Rattrapage", default=False)

    def save(self, *args, **kwargs):
        if self.rattrapage:
            self.ponderation = 100
        super().save(*args, **kwargs)

    def afficher_rattrapage(self):
        return ("evaluation", "rattrapage")[self.rattrapage]

    def __str__(self):
        return f'{self.matiere}-{self.libelle}-{self.semestre}'


class Competence(models.Model):
    id = models.CharField(primary_key=True, blank=True, max_length=30)
    code = models.CharField(max_length=100)
    libelle = models.CharField(max_length=100)
    ue = models.ForeignKey('Ue', on_delete=models.CASCADE, verbose_name="UE")
    matiere = models.ForeignKey(
        'Matiere', on_delete=models.CASCADE, verbose_name="Matiere")


class AnneeUniversitaire(models.Model):
    annee = models.DecimalField(
        max_digits=4, decimal_places=0, verbose_name="Année universitaire")
    annee_courante = models.BooleanField(
        default=False, verbose_name="Année universitaire acutuelle", null=True)

    def save(self, *args, **kwargs):
        annee = AnneeUniversitaire.objects.filter(annee=self.annee)
        if not self.pk and annee:
            return
        super().save(*args, **kwargs)
        self.generateSemeste()

    def disable(self):
        self.annee_courante = False
        self.save()

    def get_semestres(self):
        return self.semestre_set.all()

    def generateSemeste(self):
        courant = False
        for i in range(1, 7):
            courant = i in [1, 3, 5] and self.annee > 2022
            print(courant)
            semestre = Semestre(
                libelle=f'S{i}',
                credits=30,
                courant=courant,
                annee_universitaire=self,
            )
            semestre.save()
            print(f"Semestre créé : {semestre}")

    @staticmethod
    def static_get_current_annee_universitaire():
        current_date = datetime.datetime.now()
        try:
            # Rechercher l'année accadémique courrante
            virtual_current_university_date = AnneeUniversitaire.objects.get(annee_courante=True)
            # Rechercher l'année courante
            if current_date.month >= 8 and virtual_current_university_date.annee < current_date.year:
                virtual_current_university_date.disable()
                return AnneeUniversitaire.objects.create(annee=current_date.year, annee_courante=True)
            return virtual_current_university_date
        except Exception as e:
            return AnneeUniversitaire.objects.create(annee=current_date.year, annee_courante=True)

    @staticmethod
    def getNiveau(semestre_libelle):
        data = { 'L1' : ['S1', 'S2'], 'L2' : ['S3', 'S4'], 'L3' : ['S5', 'S6'] }
        for key in data:
            if semestre_libelle in data[key]:
                return key
        return    
    
    def __str__(self):
        return f'{self.annee}-{self.annee + 1}'


class Semestre(models.Model):
    id = models.CharField(primary_key=True, blank=True, max_length=14)
    CHOIX_SEMESTRE = [('S1', 'Semestre1'), ('S2', 'Semestre2'), ('S3', 'Semestre3'),
                      ('S4', 'Semestre4'), ('S5', 'Semestre5'), ('S6', 'Semestre6')]
    libelle = models.CharField(max_length=30, choices=CHOIX_SEMESTRE)
    credits = models.IntegerField(default=30)
    courant = models.BooleanField(
        default=False, verbose_name="Semestre actuel", null=True)
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.SET_NULL, null=True)

    def save(self):
        if not self.id:
            self.id = str(self.libelle) + "-" + str(self.annee_universitaire.annee)
        return super().save()

    def static_get_current_semestre():
        try:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
            # Revoir cette partie retourner S1,S3,S5 ou S2,S4,S6
            if annee != "-":
                return annee.semestre_set.all()
        except:
            return Semestre.objects.all()

    # méthode permettant de retourner toutes les ues d'un semestre
    """
        paramètre : aucun 
        retour: tableau d'ues
    """

    def get_all_ues(self):
        try:
            programme = Programme.objects.get(semestre__id=self.id)
            return programme.ues.all()
        except:
            return []

    def code_semestre(self):
        return f'{self.libelle}-{self.annee_universitaire}'

    def __str__(self):
        return f'{self.libelle} -{self.annee_universitaire}'


class Domaine(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    description = models.TextField(max_length=500, verbose_name="description")

    def generate_code(self):
        tab_nom = self.nom.strip().split(" ")
        return f'{tab_nom[0][0]}{tab_nom[0][1]}'.upper()

    def __str__(self):
        return self.generate_code()


class Seance(models.Model):
    intitule = models.CharField(max_length=200)
    date_et_heure_debut = models.DateTimeField()
    date_et_heure_fin = models.DateTimeField()
    description = models.TextField()
    auteur = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='seance_auteur', default='Anonyme')
    valider = models.BooleanField(default=False)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.SET_NULL, null=True)
    commentaire = models.TextField(null=True)
    eleves_presents = models.ManyToManyField(Etudiant, related_name='seances_presents')

    def __str__(self):
        return self.intitule
    
    class meta :
        unique_together=["date_et_heure_debut","date_et_heure_fin","semestre"]
    
class Parcours(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    domaine = models.ForeignKey(Domaine, on_delete=models.CASCADE, verbose_name="Domaine", null=True)
    description = models.TextField(max_length=500, verbose_name="description")

    def __str__(self):
        return self.nom

class Programme(models.Model):
    parcours = models.ForeignKey(Parcours, on_delete=models.CASCADE, verbose_name="Parcours", null=True, blank=True)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, verbose_name="Semestre")
    ues = models.ManyToManyField(Ue, verbose_name="UE")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for ue in self.ues.all():
            if ue.type == "Technologie":
                type_abbr = "INF"
            else:
                type_abbr = ue.type[:3].upper()
            niveau = ue.niveau
            semestre = self.semestre.libelle[-1]
            ue_count = Ue.objects.filter(type=ue.type).count()
            ue_count_str = str(ue_count).zfill(2)
            ue.codeUE = f"{type_abbr}{niveau}{semestre}{ue_count_str}"
            ue.save()
    
    def generate_code(self):
        return f'{self.parcours}-{self.ues}-{self.semestre}'

    def __str__(self):
        return self.generate_code()

    class Meta:
        unique_together = ["parcours", "semestre"]



class Note(models.Model):
    """
    Ce modèle représente la note d'un étudiant dans un semestre et une matière donnée.

    Attributes:
        valeurNote (decimal): La valeur de la note.
        etudiant (Etudiant): L'étudiant à qui cette note appartient.
        matiere (Matiere): La matière dans laquelle l'étudiant a eu cette note. 

    Methods:
        __str__() -> str: Renvoie une représentation en chaîne de caractères de l'objet Note.
    """
    valeurNote = models.DecimalField(default=0.0, blank=False, max_digits=5, decimal_places=2,
                                     verbose_name="note", validators=[MaxValueValidator(20), MinValueValidator(0.0)])
    etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, verbose_name="Étudiant")
    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.CASCADE, verbose_name="Evaluation")

    def __str__(self):
        """
        Renvoie une représentation en chaîne de caractères de l'objet Note.
        """
        return str(self.id) + " " + str(self.evaluation) + " " + str(self.valeurNote)

class Frais(models.Model):
    annee_universitaire = models.ForeignKey(AnneeUniversitaire, on_delete=models.CASCADE)
    montant_inscription = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Frais d'inscription")
    montant_scolarite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Frais de scolarité")

    def __str__(self):
        return "Année universitaire: " + str(self.annee_universitaire) + "  Frais d'inscription : " + str(self.montant_inscription) + "     " + " Frais de scolarité : " + str(self.montant_scolarite)

class CompteEtudiant(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    annee_universitaire = models.ForeignKey(AnneeUniversitaire, on_delete=models.CASCADE)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.etudiant.nom) + str(self.etudiant.prenom) + "  Solde - " + str(self.annee_universitaire) + " : " + str(self.solde)

class Paiement(models.Model):
    TYPE_CHOICES = [
        ('Frais de scolarité', 'Frais de scolarité'),
        ("Frais d'inscription", "Frais d'inscription"),
    ]
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    dateversement = models.DateField(default=timezone.now, verbose_name="Date de versement")
    etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE, verbose_name="Etudiant")
    comptable = models.ForeignKey('Comptable', on_delete=models.CASCADE, verbose_name="Comptable")
    compte_bancaire = models.ForeignKey('CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    numerobordereau = models.CharField(max_length=30, verbose_name="Numéro de bordereau", default= 0)
    annee_universitaire = models.ForeignKey(AnneeUniversitaire, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.dateversement) + " : " + str(self.etudiant.nom) + "  " + str(self.etudiant.prenom) + "  " + str(self.montant)     


class CompteBancaire(models.Model):
    numero = models.CharField(max_length=100, verbose_name="Numéro du compte")
    solde_bancaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_tenue_de_compte = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais de tenue de compte")

    def __str__(self):
        return "Solde actuel : " + str(self.solde_bancaire)
     
    
class Salaire(models.Model):
    TYPE_CHOICES = [
        ('Enseignant', 'Enseignant'),
        ("Comptable", "Comptable"),
        ("Directeur des études", "Directeur des études"),
        ("Gardien", "Gardien"),
        ("Agent d'entretien", "Agent d'entretien"),
    ]
    date_debut = models.DateField(verbose_name="Date de début", null=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=False)
    numero_cnss = models.CharField(max_length=30, verbose_name="Numéro CNSS", default= 0)
    qualification_professionnel = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Qualification professionnelle")
    prime_efficacite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'éfficacité")
    prime_qualite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime de qualité")
    frais_travaux_complementaires = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Travaux complémentaires")
    prime_anciennete = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'ancienneté")
    frais_prestations_familiales = models.DecimalField(max_digits=10, decimal_places=3, default=0.03)
    frais_risques_professionnel = models.DecimalField(max_digits=10, decimal_places=3, default=0.02)
    frais_pension_vieillesse_emsalaire = models.DecimalField(max_digits=10, decimal_places=3, default=0.125)
    frais_prestations_familiale_salsalaire = models.DecimalField(max_digits=10, decimal_places=3, default=0.04)
    tcs = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="TCS")
    irpp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="IRPP")
    prime_forfaitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime forfaitaires")
    acomptes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Acomptes")
    salaire_net_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire Net à payer")
    compte_bancaire = models.ForeignKey('CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey('AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)


    def __str__(self):
        return str(self.personnel.nom) + " " + str(self.personnel.prenom) + " Salaire : " +  str(self.date_debut) +  " au " + str(self.date_fin)
    
    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        salaire_de_base = self.personnel.salaireBrut
        prime_efficacite = self.prime_efficacite
        prime_qualite = self.prime_qualite
        frais_travaux_complementaires = self.frais_travaux_complementaires
        prime_anciennete = self.prime_anciennete
        tcs = self.tcs
        prime_forfaitaire = self.prime_forfaitaire
        acomptes = self.acomptes
        frais_prestations_familiale_salsalaire = Decimal(self.frais_prestations_familiale_salsalaire) * Decimal(self.personnel.salaireBrut)

        primes = (
            prime_efficacite
            + prime_qualite
            + frais_travaux_complementaires
            + prime_anciennete
        )

        deductions = (
            frais_prestations_familiale_salsalaire
            + tcs
        )
        
        salaire_brut = salaire_de_base + primes
        salaire_net = salaire_brut - deductions
        pret = salaire_net - acomptes
        self.salaire_net_a_payer = pret + prime_forfaitaire 
        super(Salaire, self).save(*args, **kwargs)


class Fournisseur(models.Model):
    TYPE = [
        ('TDE', 'TDE'),
        ("CEET", "CEET"),
        ("Espoir+", "Espoir+"),
        ("Autres", "Autres"),
    ]
    TYPE_MOIS = [
        ('Janvier', 'Janvier'),
        ("Février", "Février"),
        ("Mars", "Mars"),
        ("Avril", "Avril"),
        ("Mai", "Mai"),
        ("Juin", "Juin"),
        ("Juillet", "Juillet"),
        ("Août", "Août"),
        ("Septembre", "Septembre"),
        ("Octobre", "Octobre"),
        ("Novembre", "Novembre"),
        ("Décembre", "Décembre")
    ]
    type = models.CharField(max_length=30, choices=TYPE)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    dateversement = models.DateField(default=timezone.now, verbose_name="Date de versement")
    le_mois = models.CharField(max_length=30, choices=TYPE_MOIS, verbose_name="Mois")
    compte_bancaire = models.ForeignKey('CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey('AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        super(Fournisseur, self).save(*args, **kwargs)

class Information(models.Model):
    TYPE_CHOISE = [
        ('Premier', 'Niveau 1'),
        ('Deuxième', 'Niveau 2'),
        ('Troisième', 'Niveau 3'),
    ]
    enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE, verbose_name="Enseigant", null=True)
    directeur = models.ForeignKey('DirecteurDesEtudes', on_delete=models.CASCADE, verbose_name="Directeur des études", null=True)
    numeroSecurite = models.IntegerField(verbose_name="Numéro de sécurité sociale")
    discipline = models.ForeignKey('Matiere', on_delete=models.CASCADE, verbose_name="Discipline") 
    niveau = models.CharField(max_length=100, choices=TYPE_CHOISE, verbose_name="Niveau")
    dateDebut = models.DateField(verbose_name="Date de début")
    dateFin = models.DateField(verbose_name="Date de fin")
    duree = models.CharField(max_length=100, verbose_name="Durée", default='0')

    def save(self, *args, **kwargs):
        duree = self.dateFin - self.dateDebut
        self.duree = duree.days if duree.days > 0 else 0
        super(Information, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.enseignant.nom) + " " + str(self.numeroSecurite) + " " + str(self.discipline.libelle) 


class FicheDePaie(models.Model):
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE, verbose_name="Matière")
    enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant")
    nombreHeureL1 = models.IntegerField(verbose_name="Nombre d'heure L1", default=0)
    nombreHeureL2 = models.IntegerField(verbose_name="Nombre d'heure L2", default=0)
    nombreHeureL3 = models.IntegerField(verbose_name="Nombre d'heure L3", default=0)
    nombreHeure = models.IntegerField(verbose_name="Nombre d'heure", default=0)
    prixUnitaire = models.IntegerField(verbose_name="Prix unitaire", default=0)
    montantL1 = models.IntegerField(verbose_name="montant L1", default=0)
    montantL2 = models.IntegerField(verbose_name="montant L2", default=0)
    montantL3 = models.IntegerField(verbose_name="montant L3", default=0)
    montant = models.IntegerField(verbose_name="montant", default=0)
    difference = models.IntegerField(verbose_name="Différence", default=0)
    acomptes = models.IntegerField(verbose_name="Acomptes", default=0)
    montantEnLettre = models.CharField(max_length=100, verbose_name="Montant en lettre", default="lettres")
    compte_bancaire = models.ForeignKey('CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey('AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def __str__(self):
        return str(self.enseignant.nom) + "  " +  str(self.enseignant.prenom) + "  " + str(self.dateDebut) + "-" + str(self.dateFin)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        self.montantL1 = self.nombreHeureL1 * self.prixUnitaire
        self.montantL2 = self.nombreHeureL2 * self.prixUnitaire
        self.montantL3 = self.nombreHeureL3 * self.prixUnitaire
        heure_totale = self.nombreHeure = self.nombreHeureL1 + self.nombreHeureL2 + self.nombreHeureL3
        self.montant = heure_totale * self.prixUnitaire
        difference = self.difference = self.montant - self.acomptes
        self.montantEnLettre = num2words(difference, lang='fr')
        super(FicheDePaie, self).save(*args, **kwargs)


class Charge(models.Model):
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, verbose_name="Personnel")
    frais_de_vie = models.IntegerField(verbose_name="Frais de vie", default=0)
    frais_nourriture = models.IntegerField(verbose_name="Frais de nourriture", default=0)   
    montant = models.IntegerField(verbose_name="Montant", default=0)
    montantEnLettre = models.CharField(max_length=100, verbose_name="Montant en lettre", default="lettres")
    annee_universitaire = models.ForeignKey('AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    compte_bancaire = models.ForeignKey('CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.personnel.nom) + "  " +  str(self.personnel.prenom) + "  " + str(self.dateDebut) + "-" + str(self.dateFin)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        total = self.frais_de_vie + self.frais_nourriture
        self.montant = total
        self.montantEnLettre = num2words(total, lang='fr')
        super(Charge, self).save(*args, **kwargs)


class Conge(models.Model):
    NATURE_CHOICES = [
        ('conge_annuel', 'Congé annuel'),
        ('conge_maternite', 'Congé de maternité'),
        ('conge_paternite', 'Congé de paternité'),
        ('autres', 'Autres'),
    ]
    VALIDATION_CHOICES = [
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
        ('Inconnu', 'Inconnu'),
    ]

    nature = models.CharField(max_length=30, choices=NATURE_CHOICES, verbose_name="Nature des congés")
    date_et_heure_debut = models.DateField(default=timezone.now, verbose_name="Date de début")
    date_et_heure_fin = models.DateField(default=timezone.now, verbose_name="Date de fin")
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, verbose_name="Personnel")
    motif_refus = models.TextField(null=True, blank=True, verbose_name="Motif de refus")
    valider = models.CharField(max_length=30, choices=VALIDATION_CHOICES, verbose_name="État", default="Inconnu")
    nombre_de_jours_de_conge = models.IntegerField(default=0) 
    annee_universitaire = models.ForeignKey('AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        duree = self.date_et_heure_fin - self.date_et_heure_debut
        self.nombre_de_jours_de_conge = duree.days if duree.days > 0 else 0
        super(Conge, self).save(*args, **kwargs)
        self.personnel.update_conge_counts()

    def __str__(self):
        return str(self.personnel.nom) + "  " +  str(self.personnel.prenom) + "  " + str(self.nombre_de_jours_de_conge) 
