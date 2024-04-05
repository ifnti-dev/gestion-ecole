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
from django.db.models import Sum
from num2words import num2words
from decimal import Decimal, ROUND_DOWN
import math

def create_auth_user(nom, prenom, email):
    username = (prenom + nom).lower()
    username = username.replace(" ", "")
    year = date.today().year
    password = 'ifnti' + str(year) + '!'
    user = User.objects.create_user(username=username, password=password, email=email, last_name=nom, first_name=prenom, is_staff=False)
    return user

def get_str_id_order(compteur):
    return str(compteur).zfill(2)

class Utilisateur(models.Model):
    """
    Modèle représentant un utilisateur du système.
    """
    SEXE_CHOISE = [
        ('F', 'Feminin'),
        ('M', 'Masculin')
    ]
    nom = models.CharField(max_length=50, verbose_name="Nom")

    """
        Nom de l'utilisateur

        **Type**:    string
    """

    prenom = models.CharField(max_length=50, verbose_name="Prénom")

    """
        Prénom de l'utilisateur

        **Type**:    string
    """

    sexe = models.CharField(max_length=1, choices=SEXE_CHOISE)

    """
        Sexe de l'utilisateur

        **Type**:    string
    """

    datenaissance = models.DateField(blank=True, verbose_name="date de naissance", null=True, validators=[
                                     MaxValueValidator(limit_value=date(2006, 1, 1), message="L'année de naissance doit être inférieure à 2006")])

    """
        Date de naissance de l'utilisateur

        **Type**:    string

        **Nullable:** true
    """

    lieunaissance = models.CharField(
        blank=True, max_length=20, verbose_name="lieu de naissance", null=True)

    """
        Lieu de naissance de l'utilisateur

        **Type**:    string
    """

    contact = models.CharField(max_length=25, null=True)

    """
        Numéro de téléphone de l'utilisateur

        **Type**:    string

        **Nullable:** true
    """

    email = models.CharField(max_length=50, null=True)

    """
        Email de l'utilisateur

        **Type**:    string

        **Nullable:** true
    """

    adresse = models.CharField(max_length=50, null=True)

    """
        Adresse de l'utilisateur

        **Type**:    string

        **Nullable:** true
    """

    prefecture = models.CharField(
        max_length=50, null=True, verbose_name="Préfecture", default='tchaoudjo', blank=True)

    """
        Préfecture de provenance de l'utilisateur

        **Type**:    string

        **Valeur par defaut:** Tchaoudjo
    """

    is_active = models.BooleanField(
        default=True, verbose_name="Actif", null=True)

    """
        Statut de l'utilisateur (actif ou inactif)

        **Type**:    string

        **Valeur par défaut:** true
    """

    carte_identity = models.CharField(max_length=50, null=True,  verbose_name="Carte d'identité")

    """
        Carte d'identitée de l'utilisateur    
    
        **Type**:    string

        **Nullable:** true
    """

    nationalite = models.CharField(
        max_length=30, default='Togolaise', verbose_name='Nationalté', blank=True)

    """
        Attestation de nationalité de l'utilisateur

        **Type**:    string

        **Valeur par défaut:** Togolaise
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    profil = models.ImageField(storage="user_profils", null=True, blank=True, verbose_name="Profil")

    """
        Photo passeport de l'utilisateur

        **Type**:    string

        **Nullable:** true
    """

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.nom) + ' ' + str(self.prenom)

    def full_name(self):
        """

            Donne le nom et prénom de l'utilisateur    

            :return: Le nom et prénom de l'utilisateur
            :retype: string
        """
        return self.nom.upper() + ' ' + self.prenom

    def getrole(self):
        """
            Donne le nom du rôle de l'utilisateur

            :return: Le role de l'utilisateur.
            :retype:  string
        """
        return self.user.groups.all()[0].name

    def suspendre(self):
        """
            Désactive un utilisateur

        """

        self.is_active = False
        self.save()

    def reactiver(self):
        """
            Active un utilisateur inactif

        """

        self.is_active = True
        self.save()


class Etudiant(Utilisateur):

    """
        Classe Etudiant
    """
    id = models.CharField(primary_key=True, blank=True,
                          max_length=12, editable=False)
    CHOIX_SERIE = [('A', 'A'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'),
                   ('F4', 'F4'), ('G2', 'G2')]

    seriebac1 = models.CharField(
        blank=True, max_length=2, choices=CHOIX_SERIE, verbose_name="Série bac 1", null=True)

    """
        Série de l'étudiant en 1ere

        **Type**:    string

        **Nullable:** true
    """

    seriebac2 = models.CharField(
        blank=True, max_length=2, choices=CHOIX_SERIE, verbose_name="Série bac 2", null=True)

    """
        Série de l'étudiant en Terminale

        **Type**:    string

        **Nullable:** true
    """

    anneeentree = models.IntegerField(default=datetime.date.today(
    ).year, blank=True, verbose_name="Promotion", null=True)

    """
        Série de l'étudiant en Terminale

        **Type**:    string

        **Nullable:** true
    """

    anneebac1 = models.IntegerField(
        blank=True, verbose_name="Année d’obtention du BAC 1", null=True)

    """
        Année d'obtention du BAC 1

        **Type**:    integer

        **Nullable:** true
    """

    anneebac2 = models.IntegerField(
        blank=True, verbose_name="Année d’obtention du BAC 2", null=True, default=datetime.date.today().year)

    """
        Année d'obtention du BAC 2

        **Type**:    integer

        **Valeur par defaut:** Date actuelle
    """

    etablissementSeconde = models.CharField(
        max_length=300, verbose_name="Nom d'établissement seconde", null=True, blank=True)

    """
        Établissement de 2nde de l'étudiant

        **Type**:    string

        **Nullable:** true
    """

    francaisSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Seconde", default="0")

    """
        Note en français en classe de 2nde de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    anglaisSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Seconde", default="0")

    """
        Note en anglais en classe de 2nde de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    mathematiqueSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Seconde", default="0")

    """
        Note en mathematique en classe de 2nde de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    etablissementPremiere = models.CharField(
        max_length=300, verbose_name="Nom d'établissement Première", null=True, blank=True)

    """
        Établissement de 1ere de l'étudiant

        **Type**:    string

        **Nullable:** true
    """

    francaisPremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Première", default="0")

    """
        Note en français en classe de 1ere de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    anglaisPremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Première", default="0")

    """
        Note en anglais en classe de 1ere de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    mathematiquePremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Première", default="0")

    """
        Note en mathématiques en classe de 1ere de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    etablissementTerminale = models.CharField(
        max_length=300, verbose_name="Nom d'établissement Terminale", null=True, blank=True)

    """
        Établissement de Terminale de l'étudiant

        **Type**:    string

        **Nullable:** true
    """

    francaisTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Terminale", default="0")

    """
        Note en français en classe de Terminale de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    anglaisTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Terminale", default="0")

    """
        Note en anglais en classe de Terminale de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    mathematiqueTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Terminale", default="0")

    """
        Note en mathématiques en classe de Terminale de l'étudiant

        **Type**:    integer

        **Valeur par defaut:** 0
    """

    delegue = models.BooleanField(
        default=False, verbose_name="delegué", null=True)

    """
        Attribut permettant de savoir si l'étudiant est le délégué de sa classe 

        **Type**:    boolean

        **Valeur par défaut:** false
    """

    passer_semestre_suivant = models.BooleanField(
        default=False, verbose_name="Passer au semestre suivant")

    """
        Permet de savoir si l'étudiant passe au semestre suivant

        **Type**:    boolean

        **Valeur par défaut:** false
    """

    decision_conseil = models.TextField(
        verbose_name="Décision du conseil", null=True, default="Décision du conseil")

    """
        Décision du conseil sur lors du passage au niveau supérieur

        **Type**:    string

        **Valeur par défaut:** Décision du conseil
    """

    photo_passport = models.ImageField(storage="photo_passport", null=True, blank=True, verbose_name="Photo passport")

    """
        Photo de profil

        **Type**:    string

        **Nullable:** true
    """

    semestres = models.ManyToManyField('Semestre', null=True)

    """
        Liste des semestres de l'étudiant

        **Type**:    list[Semestre]

        **Nullable:** true
    """

    tuteurs = models.ManyToManyField(
        'Tuteur', related_name="Tuteurs", blank=True, null=True)

    """
        Tuteurs de l'étudiant

        **Type**:    list[Tuteur]

        **Nullable:** true
    """

    class Meta:
        verbose_name = "Etudiant"
        verbose_name_plural = "Etudiants"
        unique_together = [["nom", "prenom", "datenaissance", "email"]]

    def generate_email(self):
        prenoms = "-".join(self.prenom.split()).lower()
        return f"{prenoms}.{self.nom.lower()}@ifnti.com"

    """ Cléf de l'étudiant"""

    def save(self, force_insert=False, force_update=False, using=None):
        """
        Méthode pour sauvegarder un étudiant
        """
        self.email = self.generate_email()
        if not self.id:
            list_etudiants = Etudiant.objects.filter(anneeentree=self.anneeentree)
            if list_etudiants:
                compteur = list_etudiants.count()+1
                str_valeur_compteur = get_str_id_order(compteur)
                            
                self.id = f"{self.nom[0]}{self.prenom[0]}{self.anneeentree}{str_valeur_compteur}"
            else:
                self.id = f"{self.nom[0]}{self.prenom[0]}{self.anneeentree}01"
            
            self.user = create_auth_user(self.prenom, self.nom, self.email)  
            group_etudiant = Group.objects.get(name="etudiant")
            self.user.groups.add(group_etudiant)
        super().save()

    def get_semestre_courant(self):
        """
            Cette fonction retourne le semestre actuel de l'étudiant.


            :return: Retourne le semestre actuel de l'étudiant.
            :retype: Semestre 

        """
        semestre = self.semestres.filter(courant=True)
        if semestre:
            return semestre

    def get_niveau_annee(self, annee_universitaire):
        """
            Cette fonction retourne le niveau de l'étudiant au cours d'une année universitaire donnée.

            :param annee_universitaire: Année Universitaire de l'étudiant
            :type annee_universitaire: AnneeUniversitaire
            :return: Retourne le niveau de l'étudiant au cours de l'année universitaire avec ses semestres.
            :retype: tuple (niveau, list[Semestre]) 

        """

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
        """
            Cette fonction retourne les moyennes dans toutes les matières suivies par un étudiant au cours d'un trimestre donné, pour chaque matière défini un attribut booléen pour déterminer s'il à validé ou non. 

            :param semestre: Semestre de l'étudiant.
            :type semestre: Semestre
            :return: Retourne un tableau de dictionnaires, chaque dictionnaire composé du libellé de la matière, la moyenne obtenue et la validation.
            :retype: list[dict()] 
        """

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
            moyenne, a_valider, _ = self.moyenne_etudiant_matiere(
                matiere, semestre)
            # print(moyenne, a_valider)
            result.append({
                'matiere': matiere.libelle,
                'moyenne': moyenne,
                'a_valider': a_valider
            })
        return result

    def notes_etudiant_matiere(self, matiere, semestre):
        """
            Cette fonction retourne les notes obtenues par un étudiant dans une matière au cours d'un semestre. 

            :param matiere: Matière contenant les notes.
            :type matiere: Matiere
            :param semestre: Semestre des notes.
            :type semestre: Semestre
            :return: Retourne un tableau de dictionnaires, chaque dictionnaire composé du libellé de l'évaluation, la note obtenue.
            :retype: list[dict()]
        """
        # Verifier si l'étudiant suis cette matiere
        # Récupérerer toute les évaluations de l'étuidant dans cette matière
        evaluations = Evaluation.objects.filter(
            matiere=matiere, semestre=semestre)
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
        """

            Cette fonction permet de calculer la moyenne de l'étudiant dans une matière et de donner l'année de validation, si l'étudiant à passé des rattrapages il retourne alors la note de rattrapage et l'année de passage de rattrapage. Ces deux valeurs seront associées d'un booléen définissant si la personne à validé la matière ou non.

            :param matiere: La matière dans laquelle la moyenne est calculée. 
            :type matiere: Matiere 
            :param semestre: Le semestre au cours duquel l'élève a composé dans la matière
            :type semestre: Semestre 
            :return: Retourne un tuple contenant la moyenne obtenue, un booléen déterminant si l'étudiant à validé ou pas, et l'année de validation.
            :retype: tuple(moyenne, validation, année de validation)



        """
        # Verifier si l'étudiant suit cette matiere
        # Récupérerer toute les évaluations de l'étuidant dans cette matière
        evaluations = Evaluation.objects.filter(
            matiere=matiere, rattrapage=False, semestre=semestre)
        if not evaluations:
            return 0, 0, semestre.annee_universitaire.annee

        # on récupère tous les rattrapages faits dans cette matière au cours des différentes années scolaires
        rattrapages = Evaluation.objects.filter(
            matiere=matiere, rattrapage=True)
        # s'il il y'a eu des rattrapages alors on recherche les notes de l'étudiant au cours de ces rattrapages
        if rattrapages:
            for rattrapage in rattrapages:
                note = rattrapage.note_set.filter(etudiant=self)
                # si l'étudiant a eu à passer alors un ou plusieurs rattrapage on prend uniquement la note la plus élevée
                # par la suite on retourne alors la note minimale comme sa moyenne de la matière ainsi que l'année de validation
                # l'année de validation servira à déterminer en quelle année l'étudiant à validé l'UE.
                if note:
                    if note.get().valeurNote >= matiere.minValue:
                        moyenne = matiere.minValue
                        a_valide = True
                        anneeValidation = rattrapage.semestre.annee_universitaire.annee
                        return moyenne, a_valide, anneeValidation

        note_ponderation = {}
        somme = 0
        for evaluation in evaluations:
            notes = evaluation.note_set.filter(etudiant=self)
            if notes:
                note = notes.get()
                somme += note.valeurNote * evaluation.ponderation
                note_ponderation[evaluation.libelle] = (
                    note, evaluation.ponderation)
        moyenne = round(somme/100, 2)
        a_valide = moyenne >= matiere.minValue
        return moyenne, a_valide, semestre.annee_universitaire.annee

    def moyenne_etudiant_ue(self, ue, semestre):
        """

            Cette fonction permet de calculer la moyenne de l'étudiant dans une UE et de donner l'année de validation. L'année de validation est déterminée dans les cas de rattrapage passé par l'étudinat dans une matière de l'ue par l'année du dernier rattrapage en date passé par l'étudiant et qui de surcroît a été validé.

            :param ue: L'UE dans laquelle la moyenne est calculée. 
            :type ue: Ue
            :param semestre: Le semestre au cours duquel l'élève a suivi l'UE.
            :type semestre: Semestre
            :return: Retourne un tuple contenant la moyenne obtenue, un booléen déterminant si l'étudiant à validé ou pas, et l'année de validation.
            :retype: tuple(moyenne, validation, année de validation)


        """
        moyenne = 0
        somme_note = 0
        somme_coef = 0
        matieres = ue.matiere_set.all()
        # on fixe tout d'abord l'année de validation par défaut à l'année actuelle
        # si l'étudiant à tout validé correctement alors l'année est maintenue
        # dans le cas contraire il s'agit de l'année de validation du dernier rattrapage qu'il à réussi
        anneeValidation = semestre.annee_universitaire.annee

        if not matieres:
            return 0.0, False, anneeValidation

        a_valide = True
        for matiere in matieres:
            note, validation_matiere, annee = self.moyenne_etudiant_matiere(matiere, semestre)
            somme_note += float(note) * float(matiere.coefficient)
            somme_coef += matiere.coefficient
            # ici on effectue une comparaison pour récupérer l'année scolaire la plus élevée
            # il s'agit en réalité de l'année de la validation du dernier rattrapage
            if anneeValidation < annee:
                anneeValidation = annee
            if validation_matiere == False:
                a_valide = False

        moyenne = round(somme_note/somme_coef, 2)
        # matiere_principale = ue.matiere_principacle()
        # a_valide = moyenne >= matiere_principale.minValue
        if ue.type == 'Technologie':
            if moyenne < 12:
                a_valide = False
        else:
            if moyenne < 10:
                a_valide = False
        return moyenne, a_valide, anneeValidation


# Calcule le nombre de crédits obtenus par l'étudiant dans un semestre donné.


    def credits_obtenus_semestre(self, semestre):
        """
            Cette fonction permet de calculer le nombre de crédits obtenus dans le semestre donné.

            :param semestre: Semestre dans lequel calculer le nombe de crédits. 
            :type semestre: Semestre
            :return: Nombre de crédits obtenus au cours du semestre.
            :retype: int
        """
        credits_obtenus = 0

        # Récupérer tous les programmes liés à ce semestre
        programme = Programme.objects.get(semestre=semestre)

        for ue in programme.ues.all():
            # Calculer la moyenne de l'UE
            moyenne_ue, a_valide_ue, _ = self.moyenne_etudiant_ue(ue, semestre)

            # Si l'étudiant a validé l'UE, ajouter les crédits de l'UE aux crédits obtenus
            if a_valide_ue:
                credits_obtenus += ue.nbreCredits
        return credits_obtenus

    @staticmethod
    def get_Ln(semestres, annee_universitaire=None):
        """
            C'est une fonction statique qui permet de récupérer les étudiants de plusieurs semestres d'une année universitaire.

            :param semestres: Liste des semestres. 
            :type semestres: list
            :param annee_universitaire: Année universitaire . 
            :type annee_universitaire: AnneeUniversitaire
            :return: Liste des étudiants ainsi que les semestres
            :retype: tuple(list[Etudiant], list[Semestre])
        """
        if not annee_universitaire:
            annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestres_pk = [
            f'{semestre}-{annee_universitaire.annee}' for semestre in semestres]

        programmes = Programme.objects.filter(semestre__in=semestres_pk)

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
            Cette fonction permet de calculer le nombre de crédits obtenus dans le semestre donné.

            :param semestre: Semestre dans lequel calculer le nombe de crédits. 
            :type semestre: Semestre
            :return: Nombre de crédits obtenus au cours du semestre.
            :retype: int
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
        """
            Cette fonction permet de récupérer l'ensemble des étudiants de L1 et les semestres de L1.

            :param annee: L'année universitaire de la classe de L1. 
            :type annee: AnneeUniversitaire
            :param semestres: Tableau contenant les semestres de L1. 
            :type semestres: list[Semestre]
            :return: Un tuple contenant un tableau d'étudiant et un tableau contenant les semestres de L1.
            :retype: tuple(list[Etudiant], list[Semestre])
        """
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
        """
            Cette fonction permet de récupérer l'ensemble des étudiants de L2 et les semestres de L2.

            :param annee: L'année universitaire de la classe de L2. 
            :type annee: AnneeUniversitaire
            :param semestres: Tableau contenant les semestres de L2. 
            :type semestres: list[Semestre]
            :return: Un tuple contenant un tableau d'étudiant et un tableau contenant les semestres de L2.
            :retype: tuple(list[Etudiant], list[Semestre])
        """

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
        """
            Cette fonction permet de récupérer l'ensemble des étudiants de L3 et les semestres de L3.

            :param annee: L'année universitaire de la classe de L3. 
            :type annee: AnneeUniversitaire
            :param semestres: Tableau contenant les semestres de L3. 
            :type semestres: list[Semestre]
            :return: Un tuple contenant un tableau d'étudiant et un tableau contenant les semestres de L3.
            :retype: tuple(list[Etudiant], list[Semestre])
        """

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
        """
            Cette fonction permet de récupérer l'ensemble des semestres d'une Année universitaire.

            :param type: Défini les types de semestres à récupérer. 
            :type type: str
            :param annee: Année universitaire des semestres. 
            :type annee: AnneeUniversitaire
            :return: Un tableau de semestres.
            :retype: list[Semestre]
        """
        if not annee:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
        if type == 'tous':
            semestre = self.semestres.all()
        elif type == 'courant':
            semestre = self.semestres.filter(
                courant__in=[True], annee_universitaire=annee)
        return semestre

    def __str__(self):
        """

            Méthode toString de la classe Etudiant


            :return: Retourne le nom d'utilisateur de l'étudiant
            :retype: str



        """
        str_sem = "|".join([sem.id for sem in self.semestres.all()])
        return self.user.username

    def create_compte_etudiant(self):
        """
            Crée le compte écolage de l'étudiant.
        """

        # Récupérez l'année universitaire courante
        annee_universitaire_courante = AnneeUniversitaire.objects.get(
            annee_courante=True)

    # Créez un compte étudiant associé à l'année universitaire courante
        CompteEtudiant.objects.create(
            etudiant=self, annee_universitaire=annee_universitaire_courante, solde=0)


@receiver(post_save, sender=Etudiant)
def create_compte_etudiant(sender, instance, created, **kwargs):
    if created:
        instance.create_compte_etudiant()


class Personnel(Utilisateur):   
    # id = models.CharField(primary_key=True, blank=True, max_length=30)
    """
        Classe Personnel, représentant les membres du personnel. Elle hérite de la classe Utilisateur
    """
    numero_cnss = models.CharField(
        max_length=30, verbose_name="Numéro CNSS", default=0)
    """
        Numéro CNSS (Caisse Nationale de Sécurité Sociale)
        
        **Type:** string

        **Valeur par défaut:** "0"

    """
    nif = models.CharField(max_length=50, verbose_name="Num d'identification fiscale", default=0)
    """
        Numéro d'identification fiscale

        **Type:** string

        **Valeur par défaut:** "0"

    """
    salaireBrut = models.DecimalField(
        max_digits=15, decimal_places=2,  verbose_name="Salaire Brut", default=0)
    """
        Salaire brut du membre du employé

        **Type**:   Decimal

        **Valeur par défaut:** 0
    """
    dernierdiplome = models.ImageField(
        null=True, blank=True, verbose_name="Dernier diplome")
    """
        Dernier diplome obtenu par le membre du employé

        **Type**:    string

        **Nullable:** true
    """
    nbreJrsCongesRestant = models.IntegerField(
        verbose_name="Nbre jours de congé restant", default=0)
    """
        Nombre de congés restants prennables par le membre du employé

        **Type**:    integer

        **Valeur par défaut:** 0
    """
    nbreJrsConsomme = models.IntegerField(
        verbose_name="Nombre de jours consommé", default=0)
    """
        Nombre de jours de congés déjà consommés par l'employé

        **Type**:    integer

        **Valeur par défaut:** 0
    """
    nombre_de_personnes_en_charge = models.IntegerField(
        verbose_name="Nbre de pers pris en charge", default=0)
    """
        Nombre de personnes prises en charge par l'employé

        **Type**:    integer

        **Valeur par défaut:** 0
    """

    def save(self):
        """
        Fonction rattachant l'employé à un utilisateur lors de sa sauvegarde.

        """
        print(f'----{self.id}----')
        if not self.id:
            self.user = create_auth_user(self.prenom, self.nom, self.email)  
        super().save()

    def update_conge_counts(self):
        """
        Fonction mettant à jour le nombre de congés disponibles pour l'employé
        """
        # Ajoutez la condition de validation ici
        conges_pris = Conge.objects.filter(personnel=self, valider='Actif')
        total_jours_pris = conges_pris.aggregate(
            total=Sum('nombre_de_jours_de_conge'))['total'] or 0
        self.nbreJrsConsomme = total_jours_pris
        self.nbreJrsCongesRestant = 30 - \
            total_jours_pris if total_jours_pris <= 30 else 0  # Mise à zéro si dépassement
        self.save()

    def calculer_salaire_brut_annuel(self):
        """
        Fonction calculant le salaire brut annuel de l'employé

        :return: Salaire brut annuel de l'employé

        :retype: Decimal

        """
        salaires = Salaire.objects.filter(personnel=self)
        total_salaire_brut_annuel = sum(
            salaire.calculer_salaire_brut_mensuel() for salaire in salaires)
        return int(total_salaire_brut_annuel)


    def calculer_irpp_tcs_annuel(self):
        """
        Fonction calculant la cumulation annuelle de l'IRPP (Import sur le Revenu des Personnes Physiques) et de la TCS (Taxe Complémentaire sur le Salaire).

        :return: Somme entre le IRPP annuel et le TCS annuel del'employé

        :retype: Decimal
        """

        salaires = Salaire.objects.filter(personnel=self)
        total_irpp_annuel = sum(salaire.calculer_irpp_mensuel()
                                for salaire in salaires)
        total_tcs_annuel = sum(salaire.tcs for salaire in salaires)
        total_irpp_tcs_annuel = Decimal(
            total_irpp_annuel) + Decimal(total_tcs_annuel)
        return int(total_irpp_tcs_annuel)


    def calcule_deductions_cnss_annuel(self):
        """
        Fonction calculant la déduction annuelle de la CNSS sur le salaire de l'employé

        :return: Total déduit par la cnss sur le salaire de l'employé au cours de l'année.

        :retype: Decimal
        """

        salaires = Salaire.objects.filter(personnel=self)

        total_deductions_cnss = sum(
            salaire.calculer_deductions_cnss() for salaire in salaires)
        # total_deductions_cnss = total_deductions_cnss.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

        return int(total_deductions_cnss)

class Enseignant(Personnel):
    """
    Cette classe hérite de la classe Personnel, elle représente les enseignants.
    """    
    """
        Définit le numéro d'ordre

        **Type:** string

        **Nullable:** False
    """
    
    CHOIX_TYPE = (('Vacataire', 'Vacataire'), ('Permanent', 'Permanent'))

    type = models.CharField(null=True, blank=True,
                            max_length=9, choices=CHOIX_TYPE)
    """
        Définit le type d'enseignant qu'est l'employé: Vacataire ou Permanent

        **Type:** string

        **Nullable:** true
    """
    specialite = models.CharField(
        max_length=300, verbose_name="Spécialité", blank=True, null=True)

    """
        Définit la spécialitée de l'enseignant

        **Type:** string

        **Nullable:** true
    """

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)  
            group = Group.objects.get(name="enseignant")
            self.user.groups.add(group)
        else:
            super().save(*args, **kwargs)

    def niveaux(self):
        """
        Cette fonction donne l'ensemble des semestre au cours desquels l'enseignant intervient
        :return: Liste de chaine de caractères contenant les libellé des semestres dans lesquels il intervient
        :retype: list[string]
        """
        matieres = self.matiere_set.all()
        niveaux = set()
        for matiere in matieres:
            result = matiere.ue.programme_set.values('semestre')
            temp_semstres_libelles = [AnneeUniversitaire.getNiveau(
                elt['semestre'][:2]) for elt in result]
            niveaux.update(temp_semstres_libelles)

        return list(niveaux)

    def matieres(self, semestres):
        return Matiere.objects.filter(enseignant=self, ue__programme__semmestre__in=semestres)

    def __str__(self):
        return f'{super().__str__()}'
        # return f'{self.user.username}'


class DirecteurDesEtudes(Personnel):
    """
        Cette classe hérite de la classe Personnel, elle correspont au Directeur des Études.
    """

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs) 
            group_comptable = Group.objects.get(name="comptable")
            self.user.groups.add(group_comptable)
        else:
            super().save(*args, **kwargs)
            
        if self.is_active:
            # Désactiver les autres directeurs des études
            DirecteurDesEtudes.objects.exclude(
                pk=self.pk).update(is_active=False)

        return super().save(*args, **kwargs)

class Comptable(Personnel):
    """
    Cette classe hérite de la classe Personnel, elle représente les comptables.
    """
    
    pass

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs) 
            group_comptable = Group.objects.get(name="comptable")
            self.user.groups.add(group_comptable)
        else:
            super().save(*args, **kwargs)
        

class Tuteur(models.Model):
    """
    Modèle représentant un tuteur ou un parent d'un étudiant.

    """
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
    """
        Nom du responsable

        **Type:** string
    """
    prenom = models.CharField(max_length=20)
    """
        Prenom du responsable

        **Type:** string
    """
    sexe = models.CharField(blank=True, max_length=1, choices=CHOIX_SEX)
    """
        Sexe du responsable

        **Type:** string
    """
    adresse = models.CharField(
        blank=True, max_length=20, verbose_name="Adresse")
    """
        Adresse du responsable

        **Type:** string
    """
    contact = models.CharField(max_length=25)
    """
        Numéro de téléphone du responsable

        **Type:** string
    """
    profession = models.CharField(
        blank=True, max_length=20, verbose_name="Profession")
    """
        Profession du responsable

        **Type:** string
    """
    type = models.CharField(blank=True, max_length=20, choices=CHOIX_TYPE)
    """
        Type de tuteur: Père, Mère ou Tuteur

        **Type:** string
    """

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
    """
        Code de l'UE

        **Type:** string
    """
    libelle = models.CharField(max_length=100)
    """
        Nom du responsable

        **Type:** string
    """
    TYPES = [
        ("Technologie", "Technologie"),
        ("Communication", "Communication"),
        ("Anglais", "Anglais"),
        ("Maths", "Maths"),
        ("Organisation", "Organisation"),
    ]
    TYPES_NIVEAU = [
        ("1", "Licence"),
        ("2", "Master"),
        ("3", "Doctorat")
    ]
    niveau = models.CharField(max_length=50, choices=TYPES_NIVEAU)
    """
        Niveau d'enseignement de l'UE

        **Type:** string
    """
    type = models.CharField(max_length=50, choices=TYPES)
    """
        Type de l'UE

        **Type:** string
    """
    nbreCredits = models.IntegerField(verbose_name="Nombre de crédit", validators=[MinValueValidator(1)])
    """
        Nombre de crédits de l'UE

        **Type:** integer
    """
    heures = models.DecimalField(
        blank=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(1)])
    """
        Total d'heures d'enseignement de l'UE

        **Type:** Decimal
    """
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant responsable", null=True, blank=True)
    """
        Identifiant de l'enseignant responsable de l'UE

        **Type:** string

        **Nullable:** true
    """

    class Meta:
        verbose_name_plural = 'UE'

    def matiere_principacle(self):
        """
        Cette fonction donne la matière principale de l'UE

        :return: Un objet Matière si l'UE à une matière principale au cas contraire None.

        :retype: Matiere or None


        """
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
    codematiere = models.CharField(
        max_length=50, verbose_name="Code de la matière")
    """
        Code de la matière

        **Type:** string
    """
    libelle = models.CharField(max_length=100)
    """
        Libellé de la matière

        **Type:** string
    """
    coefficient = models.IntegerField(
        null=True,  verbose_name="Coefficient", default="1")
    """
        Coefficient de la matière

        **Type:** integer

        **Valeur par défaut:** 1
    """
    minValue = models.FloatField(
        null=True,  verbose_name="Valeur minimale",  default="7")
    """
        Moyenne minimale pour valider la matière.

        **Type:** float

        **Valeur par défaut:** 7.0
    """
    heures = models.DecimalField(blank=True, max_digits=4, decimal_places=1, validators=[
                                 MinValueValidator(1)], null=True)
    """
        Total d'heures d'enseignement de la matière

        **Type:** Decimal
    """
    abbreviation = models.CharField(
        max_length=10, default="Short", unique=True)
    """
        Nom de la matière abbrégé

        **Type:** string

        **Unique:** true
    """
    enseignant = models.ForeignKey(Enseignant, blank=True, null=True, verbose_name="Enseignants responsable", on_delete=models.CASCADE)
    """
        Identifiant de l'enseignant responsable de la matière

        **Type:** string

        **Nullable:** true
    """
    # enseignants = models.ManyToManyField(Enseignant, related_name="EnseignantsMatiere", blank=True, null=True, verbose_name="Enseignants")
    ue = models.ForeignKey('Ue', on_delete=models.CASCADE)
    """
        Identifiant de l'UE de la matière

        **Type:** string
    """
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    """
        Défini si la matière est enseignée ou non

        **Type:** booelan

        **Valeur par défaut:** true
    """

    def save(self, *args, **kwargs):
        if not self.codematiere and len(self.codematiere) == 0:
            # Calculer le préfixe numérique en fonction de l'ordre des matières dans l'UE
            ordre_matiere = Matiere.objects.filter(ue=self.ue).count() + 1
            # Construire le code de la matière en utilisant le code de l'UE et le préfixe numérique
            self.codematiere = f"{ordre_matiere}{self.ue.codeUE}"

        super().save(*args, **kwargs)

    def count_evaluations(self, annee, semestres):
        """
        Cette fonction donne le nombre d'évaluations faites au cours du semestre dans la matière

        :param annee: AnneeUniversitaire
        :type annee: AnneeUniversitaire

        :param semestres: Liste de semestres
        :type semestres: list[Semestre]

        :return: Retourne le nombre d'évalution faites dans la matière.

        :retype: integer


        """
        return Evaluation.objects.filter(matiere=self, semestre__in=semestres).count()

    def __str__(self):
        return self.codematiere + " " + self.libelle

    class Meta:
        verbose_name_plural = "Matières"

    def suspendre(self):
        """
        Cette fonction permet de suspendre la matiere.
        """

        self.is_active = False
        self.save()

    def reactiver(self):
        """
        Cette fonction permet de ractiver la matière
        """

        self.is_active = True
        self.save()

    def ponderation_restante(self, semestre):
        """
        Calcule la pondération disponible pour les évaluations dans la matière

        :param semestre: Semestre d'enseignement de la matière
        :type semestre: Semestre

        :return: Retourne la pondération restante.

        :retype: integer

        """

        try:
            evaluations = Evaluation.objects.filter(
                matiere=self, rattrapage=False, semestre=semestre)
            ponderation_total = sum(
                [evaluation.ponderation for evaluation in evaluations])
            return 100-ponderation_total
        except:
            return -1

    def is_available_to_add_evaluation(self, semestre):
        """
        Verifie s'il est possible d'ajouter une évaluation en fonction de la pondération restante

        :param semestre: Semestre d'enseignement de la matière
        :type semestre: Semestre


        :return: Retourne un booléen.

        :retype: boolean


        """
        return self.ponderation_restante(semestre=semestre) > 0

    def dans_semestre(self, semestre):
        """
        Verifie si la matière est enseignée dans le semestre donné

        :param semestre: Semestre d'enseignement de la matière
        :type semestre: Semestre


        :return: Retourne un booléen.

        :retype: boolean


        """
        return semestre in self.get_semestres(semestre.annee_universitaire, type="__all__")

    def get_semestres(self, annee_universitaire, type):
        """
        Cette méthode retourne tous les semestres dans lesquels sont enseignés la matière au cours d'une année universitaire donnée.

        :param annee_universitaire: Année universitaire de recherche
        :type annee_universitaire: AnneeUniversitaire ou __all__

        :param type: :;,  
        :type type: __current__ ou __all__

        :return: Liste des semestres dans lesquels la matière est enseignée
        :retype: list[Semestre]
        """

        # Passer plus tard le parcours
        type_semestres = []
        if type == "__current__":
            type_semestres = [True]
        elif type == "__all__":
            type_semestres = [True, False]
        if annee_universitaire == '__all__':
            annee_universitaires = AnneeUniversitaire.objects.all()
        else:
            annee_universitaires = [annee_universitaire]

        programmes = self.ue.programme_set.filter(
            semestre__annee_universitaire__in=annee_universitaires, semestre__courant__in=type_semestres)
        semestres = set()

        for programme in programmes:
            semestres.update([programme.semestre])
        semestres = list(semestres)
        return semestres

    def get_etudiants_en_rattrapage(self):
        """
        Cette méthode donne les étudiants en rattrapage dans la matière.

        :return: Liste des étudiants en rattrapage.
        :retype: list[Etudiant]

        """

        # Passer plus tard le parcours

        etudiants = set()
        semestres = self.get_semestres('__all__', '__all__')
        for semestre in semestres:
            for etudiant in semestre.etudiant_set.all():
                _, a_valide, _ = etudiant.moyenne_etudiant_matiere(
                    self, semestre)
                if not a_valide:
                    etudiants.update([etudiant])
        return list(etudiants)

    def get_etudiant_semestre(self, semestre):
        """
        Cette méthode donne les étudiants suivant la matière au cours du semestre donné

        :param semestre: Semestre d'enseignement
        :type semestre: Semestre


        :return: Liste des semestres dans lesquels la matière est enseignée
        :retype: list[Etudiant]

        """
        return semestre.etudiant_set.all()

# class EnseignantsMatiere(models.Model):
#     enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name="Enseignant")
#     matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, verbose_name="Matière")
#     est_responsable = models.BooleanField(verbose_name="Est responsable", default=False)


class Evaluation(models.Model):
    libelle = models.CharField(max_length=258, verbose_name="Nom")
    """
        Nom de l'évaluation

        **Type:** string

    """
    ponderation = models.IntegerField(
        default=1, verbose_name="Pondération (1-100)", validators=[MinValueValidator(1), MaxValueValidator(100)])
    """
        Pondération de l'évaluation

        **Type:** integer

        **Valeur par défaut:** 1
    """
    date = models.DateField(verbose_name="Date évaluation")
    """
        Date de l'évaluation

        **Type:** string

    """
    matiere = models.ForeignKey(
        Matiere, on_delete=models.CASCADE, verbose_name='Matiere')
    """
        Identifiant de la matière rattachée à l'évaluation

        **Type:** string

    """
    etudiants = models.ManyToManyField(
        Etudiant, through='Note', verbose_name="Étudiants")
    """
        Ensemble des étudiants ayant participés à l'evaluation

        **Type:** list[Etudiant]

    """
    semestre = models.ForeignKey(
        'Semestre', on_delete=models.CASCADE, null=True)
    """
        Semestre dans lequel l'évaluation à été réalisée

        **Type:** Semestre

    """
    rattrapage = models.BooleanField(verbose_name="Rattrapage", default=False)
    """
        Défini si l'évaluation est un rattrapage ou non

        **Type:** boolean

        **Valeur par défaut:** false
    """

    def save(self, *args, **kwargs):
        if self.rattrapage:
            self.ponderation = 100
        super().save(*args, **kwargs)

    def afficher_rattrapage(self):
        return ("evaluation", "rattrapage")[self.rattrapage]

    def __str__(self):
        return f'{self.matiere}-{self.libelle}-{self.semestre}'


class Competence(models.Model):
    """
        Classe compétence
    """
    id = models.CharField(primary_key=True, blank=True, max_length=30)
    """
        Identifiant de la compétence

        **Type:** string

    """
    code = models.CharField(max_length=100)
    """
        Code de la compétence

        **Type:** string

    """
    libelle = models.CharField(max_length=100)
    """
        Nom de la compétence

        **Type:** string

    """
    ue = models.ForeignKey('Ue', on_delete=models.CASCADE, verbose_name="UE")
    """
        Identifiant de l'UE de la compétence

        **Type:** string

    """
    matiere = models.ForeignKey(
        'Matiere', on_delete=models.CASCADE, verbose_name="Matiere")
    """
        Identifiant de la matière de la compétence

        **Type:** string

    """


class AnneeUniversitaire(models.Model):
    """
        Cette classe représente l'année universitaire.
    """
    annee = models.DecimalField(
        max_digits=4, decimal_places=0, verbose_name="Année universitaire")
    """
        Libellé de l'année universitaire

        **Type:** string

    """
    annee_courante = models.BooleanField(
        default=False, verbose_name="Année universitaire acutuelle", null=True)
    """
        Définit s'il s'agit de l'année en cours d'utilisation dans l'application

        **Type:** string

        **Valeur par défaut:** false
    """

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generateSemeste()

    def disable(self):
        """
            Désactive une année universitaire et la définie plus comme année "courante"
        """
        self.annee_courante = False
        self.save()

    def get_semestres(self):
        """
        Retourne les semestre de l'année universitaire

        :retype: Une liste de semestres

        :retype: list[Semestre]
        """
        return self.semestre_set.all()

    def generateSemeste(self):
        """
            Génère tous les semestres de l'année universitaire
        """
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
    def static_get_selected_annee_universitaire():
        return AnneeUniversitaire.objects.get_object_or_404(annee_courante=True)

    @staticmethod
    def static_get_current_annee_universitaire():
        """
            Méthode statique donnant l'année universitaire courante.

            :return: Un objet AnneUniversitaire correspondant à l'année universitaire en cours
            :retype: AnneeUniversitaire
        """
        current_date = timezone.now()
        virtual_current_university_date, created = AnneeUniversitaire.objects.get_or_create(annee_courante=True, defaults={'annee': current_date.year-1})
        if virtual_current_university_date.annee == current_date.year-1 and current_date.month >= 8:
            virtual_current_university_date.disable()
            return AnneeUniversitaire.objects.create(annee=timezone.now().year, annee_courante=True)
        return virtual_current_university_date
        

    @staticmethod
    def getNiveau(semestre_libelle):
        """
            Méthode statique donnant le niveau correspondant à un semestre.

            :param semestre_libelle: Nom du semestre

            :type semestre_libelle: string

            :return: Le nom correspondant au niveau du semestre.
            :retype: string
        """
        data = {'L1': ['S1', 'S2'], 'L2': ['S3', 'S4'], 'L3': ['S5', 'S6']}
        for key in data:
            if semestre_libelle in data[key]:
                return key
        return

    def __str__(self):
        return f'{self.annee}-{self.annee + 1}'


class Semestre(models.Model):
    """
        Classe correspondant aux semestres
    """
    id = models.CharField(primary_key=True, blank=True, max_length=14)
    """
        Identifiant du semestre

        **Type:** string
    """
    CHOIX_SEMESTRE = [('S1', 'Semestre1'), ('S2', 'Semestre2'), ('S3', 'Semestre3'),
                      ('S4', 'Semestre4'), ('S5', 'Semestre5'), ('S6', 'Semestre6')]
    libelle = models.CharField(max_length=30, choices=CHOIX_SEMESTRE)
    """
        Intitulé du semestre

        **Type:** string

    """
    credits = models.IntegerField(default=30)
    """
        Nombre de crédits du semestre    
    
        **Type:** integer

        **Valeur par défaut:** 30
    """
    courant = models.BooleanField(
        default=False, verbose_name="Semestre actuel", null=True)
    """
        Définit s'il s'agit d'un semestre en cours

        **Type:** string

        **Valeur par défaut:** false
    """
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.SET_NULL, null=True)
    """
    identifiant de l'année universitaire à laquelle le semestre est rattaché    
    
        **Type:** string

        **Nullable:** true
    """

    def save(self):
        if not self.id:
            self.id = str(self.libelle) + "-" + \
                str(self.annee_universitaire.annee)
        return super().save()

    def static_get_current_semestre():
        try:
            annee = AnneeUniversitaire.static_get_current_annee_universitaire()
            # Revoir cette partie retourner S1,S3,S5 ou S2,S4,S6
            if annee != "-":
                return annee.semestre_set.all()
        except:
            return Semestre.objects.all()

    def get_all_ues(self):
        """
            Méthode donnant l'ensemble des UEs contenues dans un semestre.

            :return: Liste d'UE.
            :retype: list[UE]
        """
        try:
            programme = Programme.objects.get(semestre__id=self.id)
            return programme.ues.all()
        except:
            return []

    def code_semestre(self):
        """
            Donne le code du semestre.

            :return: Une chaine de caractère correspondant au code du semestre.
            :retype: string
        """
        return f'{self.libelle}-{self.annee_universitaire}'

    def __str__(self):
        return f'{self.libelle} -{self.annee_universitaire}'

class Domaine(models.Model):
    """
        Classe correspondant aux domaines
    """
    nom = models.CharField(max_length=255, verbose_name="Nom")
    """
        Nom du domaine

        **Type:** string

    """
    description = models.TextField(max_length=500, verbose_name="description")
    """
        Description du domaine

        **Type:** string

    """

    def generate_code(self):
        """
            Donne le code du domaine.

            :return: Une chaine de caractère correspondant au code du domaine.
            :retype: string
        """
        tab_nom = self.nom.strip().split(" ")
        return f'{tab_nom[0][0]}{tab_nom[0][1]}'.upper()

    def __str__(self):
        return self.generate_code()

class Parcours(models.Model):
    """
        Classe correspondant à un parcours
    """
    nom = models.CharField(max_length=255, verbose_name="Nom")
    """
        Nom du parcours

        **Type:** string

    """
    domaine = models.ForeignKey(
        Domaine, on_delete=models.CASCADE, verbose_name="Domaine", null=True)
    """
        Identifiant du domaine auquel est rattaché le parcours

        **Type:** string

        **Nullable:** true  

    """
    description = models.TextField(max_length=500, verbose_name="description")
    """
        Description du parcours

        **Type:** string

    """

    def __str__(self):
        return self.nom

class Programme(models.Model):
    """
        Classe correspondant à un programme
    """
    parcours = models.ForeignKey(
        Parcours, on_delete=models.CASCADE, verbose_name="Parcours", null=True, blank=True)
    """
        Identifiant du parcours auquel est rattaché le programme

        **Type:** string

        **Nullable:** true

    """
    semestre = models.ForeignKey(
        Semestre, on_delete=models.CASCADE, verbose_name="Semestre")
    """
        Identifiant du semestre auquel est rattaché le programme

        **Type:** string

    """
    ues = models.ManyToManyField(Ue, verbose_name="UE")
    """
        UEs contenues dans le parcours

        **Type:** string

    """

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
        """
            Donne le code du parcours.

            :return: Une chaine de caractère correspondant au code du parcours.
            :retype: string
        """
        return f'{self.parcours}-{self.ues}-{self.semestre}'

    def __str__(self):
        return self.generate_code()

    class Meta:
        unique_together = ["parcours", "semestre"]

class Settings(models.Model):
    data_is_load = models.BooleanField(default=False)

class CorrespondanceMaquette(models.Model):
    """
        Classe permettant de faire les correspondances entre différentes maquettes. Cette classe à étét mise en place pour fair e la correpondance entre les UEs et Matières de l'IFNTI d'avant 2023 et celles post-2023.
    """
    class Nature(models.TextChoices):
        UE = "U", "UE"
        MATIERE = "M", "Matière"

    nature = models.CharField(max_length=1, choices=Nature.choices)
    """
        Nature des éléments à correspondre (UE ou Matière)

        **Type:** string

    """
    ancienne = models.CharField(max_length=225, blank=True, null=True)
    """
        Ancienne UE ou Matiere

        **Type:** string

        **Nullable:** true

    """
    nouvelle = models.CharField(max_length=225, blank=True, null=True)
    """
        Nouvelle UE ou Matiere

        **Type:** string

        **Nullable:** true

    """

    def save(self):
        super().save()

    def afficher_nature(self):
        """
            Affiche la nature de la correspondance

            :return: Une chaine de caractère correspondant à la nature de la correpondance.
            :retype: string
        """
        return "UE" if self.nature.lower() == 'u' else "Matière"

    def get_ancienne(self):
        """
            Donne l'ancienne UE ou Matiere.

            :return: Un objet UE ou Matiere en fonction de la nature de la correspondance.

            :retype: UE ou Matiere.
        """
        return Ue.objects.get(id=self.ancienne) if self.nature.lower() == 'u' else Matiere.objects.get(id=self.ancienne)

    def get_nouvelle(self):
        """
            Donne la nouvelle UE ou Matiere.

            :return: Un objet UE ou Matiere en fonction de la nature de la correspondance.

            :retype: UE ou Matiere
        """
        return Ue.objects.get(id=self.nouvelle) if self.nature.lower() == 'u' else Matiere.objects.get(id=self.nouvelle)

class Note(models.Model):
    """
    Ce modèle représente la note d'un étudiant dans un semestre et une matière donnée.
    """
    valeurNote = models.DecimalField(default=0.0, blank=False, max_digits=5, decimal_places=2,
                                     verbose_name="note", validators=[MaxValueValidator(20), MinValueValidator(0.0)])
    """
        Valeur de la note

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, verbose_name="Étudiant")
    """
        Identifiant de l'étudiant à qui appartient la note

        **Type:** string

    """
    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.CASCADE, verbose_name="Evaluation")
    """
        Evaluation dans laquelle l'étudiant a obtenu la note

        **Type:** string

    """

    def __str__(self):
        """
        Renvoie une représentation en chaîne de caractères de l'objet Note.
        """
        return str(self.id) + " " + str(self.evaluation) + " " + str(self.valeurNote)


class Frais(models.Model):
    """
        Classe correpsondant aux Frais de scolarité chaque année
    """
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.CASCADE)
    """
        Année universitaire du montant des frais

        **Type:** string

    """
    montant_inscription = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Frais d'inscription")
    """
        Montant de l'inscription

        **Type:** Decimal

    """
    montant_scolarite = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Frais de scolarité")
    """
        Montant de la scolaritée

        **Type:** Decimal

    """

    def __str__(self):
        return "Année universitaire: " + str(self.annee_universitaire) + "  Frais d'inscription : " + str(self.montant_inscription) + "     " + " Frais de scolarité : " + str(self.montant_scolarite)


class CompteEtudiant(models.Model):
    """
        Classe représentant le compte de paiement de l'étudiant
    """
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    """
        Montant de la scolaritée

        **Type:** Decimal

    """
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.CASCADE)
    """
        Montant de la scolaritée

        **Type:** Decimal

    """
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    """
        Total à solder par l'étudiant au cours de l'année scolaire

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """

    def __str__(self):
        return str(self.etudiant.nom) + str(self.etudiant.prenom) + "  Solde - " + str(self.annee_universitaire) + " : " + str(self.solde)


class Paiement(models.Model):
    """
        Classe correspondant au versement des frais de scolarité par l'étudiant
    """
    TYPE_CHOICES = [
        ('Frais de scolarité', 'Frais de scolarité'),
        ("Frais d'inscription", "Frais d'inscription"),
    ]
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    """
        Type de paiement

        **Type:** string


    """
    montant = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    """

        Montant versé par l'étudiant

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    dateversement = models.DateField(
        default=timezone.now, verbose_name="Date de versement")
    """
        Date du versement

        **Type:** string

    """
    etudiant = models.ForeignKey(
        'Etudiant', on_delete=models.CASCADE, verbose_name="Etudiant")
    """
        Étudiant ayant éffectué le versement
    
        **Type:** string

    """
    comptable = models.ForeignKey(
        'Comptable', on_delete=models.CASCADE, verbose_name="Comptable")
    """
        Total à solder par l'étudiant au cours de l'année scolaire

        **Type:** Decimal

    """
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    """
        Compte bancaire sur lequel le versement à été effectué.

        **Type:** integer

        **Nullable:** true

    """
    numerobordereau = models.CharField(
        max_length=30, verbose_name="Numéro de bordereau", default=0)
    """
        Numéro du bordereau de versement

        **Type:** string

        **Valeur par défaut:** "0"

    """
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.CASCADE)
    """
        Année universitaire correspondant au versement

        **Type:** string

    """

    def __str__(self):
        return str(self.dateversement) + " : " + str(self.etudiant.nom) + "  " + str(self.etudiant.prenom) + "  " + str(self.montant)


class CompteBancaire(models.Model):
    """
    Modèle représentant un compte bancaire.

    """
    numero = models.CharField(max_length=100, verbose_name="Numéro du compte")
    """
       Numéro du compte bancaire

        **Type:** string


    """
    solde_bancaire = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    """
        Solde dans le compte

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    frais_tenue_de_compte = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Frais de tenue de compte")
    """
        Frais de tenue de compte
    
        **Type:** Decimal

        **Valeur par défaut:** 0

    """

    def __str__(self):
        """
        Renvoie une représentation en chaîne de caractères de l'objet CompteBancaire.
        """
        return "Solde actuel : " + str(self.solde_bancaire)


class Salaire(models.Model):
    """
    Modèle représentant les détails du salaire d'un personnel.
    """
    TYPE_CHOICES = [
        ('Enseignant', 'Enseignant'),
        ("Comptable", "Comptable"),
        ("Directeur des études", "Directeur des études"),
        ("Gardien", "Gardien"),
        ("Agent d'entretien", "Agent d'entretien"),
        ('Stagiaire', 'Stagiaire'),
    ]
    date_debut = models.DateField(verbose_name="Date de début", null=True)
    """
        Date à laquelle l'employé à commencé par travailler

        **Type:** string

        **Nullable:** true

    """
    date_fin = models.DateField(verbose_name="Date de fin", null=True)
    """
        Date à laquelle l'employé s'est arrêté de travailler    
    
        **Type:** string

        **Nullable:** true

    """
    personnel = models.ForeignKey(
        Personnel, on_delete=models.CASCADE, null=False)
    """
        Employé à qui est rattaché le salaire
    
        **Type:** string

        **Nullable:** true

    """
    qualification_professionnel = models.CharField(
        max_length=30, choices=TYPE_CHOICES, verbose_name="Qualification professionnelle")
    """
        Qualification professionelle de l'employé

        **Type:** string

    """
    prime_efficacite = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'éfficacité")
    """
        Prime d'efficacité de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    prime_qualite = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime de qualité")
    """
        Prime de qualitée de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    frais_travaux_complementaires = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Travaux complémentaires")
    """
        Frais des travaux complémentaires réalisés par l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    prime_anciennete = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'ancienneté")
    """
        Prime d'anciennetée de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    frais_prestations_familiales = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.03)
    """
        Frais des prestations familiales de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.03

    """
    frais_risques_professionnel = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.02)
    """
        Frais des risques professionnels

        **Type:** Decimal

        **Valeur par défaut:** 0.02

    """
    frais_pension_vieillesse_emsalaire = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.125)
    """
        Frais de la pension de vieillesse de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.125

    """
    frais_prestations_familiale_salsalaire = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.04)
    """
        Frais prestations familiale salariales

        **Type:** Decimal

        **Valeur par défaut:** 0.04

    """
    assurance_maladie_universelle = models.DecimalField(max_digits=10, decimal_places=2, default=0.05, verbose_name="Assurance maladie universelle")
    """
        Frais pour l'assurance maladie universelle

        **Type:** Decimal

        **Valeur par défaut:** 0.05

    """
    tcs = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="TCS")
    """
        Taxe complémentaire sur le salaire

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    irpp = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="IRPP")
    """
        Impôt sur le revenu des personnes physiques

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    prime_forfaitaire = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime forfaitaires")
    """
        Prime forfaitaire de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    acomptes = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Acomptes")
    """
        Acomptes de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    salaire_net_a_payer = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Salaire Net à payer")
    """
        Salaire net de l'employé

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    """
        Compte bancaire de l'employé
    
        **Type:** string

        **Nullable:** true

    """
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    """
        Année universitaire au cours duquel l'employé à reçu le paiement
    
        **Type:** string

        **Nullable:** true

    """

    def calculer_salaire_brut_annuel(self):
        """
            Donne le salaire brut annuel de l'employé

            :return: Le salaire brut annuel de l'employé

            :retype: Decimal
        """
        salaire_de_base = self.personnel.salaireBrut
        prime_efficacite = self.prime_efficacite
        prime_qualite = self.prime_qualite
        frais_travaux_complementaires = self.frais_travaux_complementaires
        prime_anciennete = self.prime_anciennete
        primes = (
            prime_efficacite
            + prime_qualite
            + frais_travaux_complementaires
            + prime_anciennete
        )
        salaire_brut_mensuel = salaire_de_base + primes
        salaire_brut_annuel = salaire_brut_mensuel * 12
        return salaire_brut_annuel

    def calculer_salaire_brut_mensuel(self):
        """
            Donne le salaire brut mensuel de l'employé

            :return: Le salaire brut mensuel de l'employé

            :retype: Decimal
        """
        salaire_brut_mensuel = self.calculer_salaire_brut_annuel() / 12
        return salaire_brut_mensuel

    def calculer_total_A(self):
        total_A = self.calculer_salaire_brut_annuel()
        return total_A

    def calculer_total_B(self):
        total_B = Decimal(self.calculer_salaire_brut_annuel()) * Decimal(0.04)
        return total_B

    def calculer_total_C(self):
        total_C = self.calculer_total_A() - self.calculer_total_B()
        return total_C

    def calculer_total_D(self):
        G41 = self.calculer_total_C()
        if G41 < 10000000:
            total_D = Decimal(0.28) * G41
        elif G41 > 10000000:
            total_D = 10000000 * 0.28
        else:
            total_D = 0
        return total_D

    def calculer_semi_net(self):
        G41 = self.calculer_total_C()
        G42 = self.calculer_total_D()
        semi_net = G41 - G42
        return semi_net

    def calculer_charges_de_familles(self):
        """
            Calcule les charges familliales de l'employé

            :return: Frais des charges familliales de l'employé

            :retype: Decimal
        """
        F44 = self.personnel.nombre_de_personnes_en_charge
        if F44 <= 6:
            resultat = 120000 * F44
        else:
            resultat = 6 * 120000
        return resultat

    def calculer_net_taxable(self):
        G43 = self.calculer_semi_net()
        G44 = self.calculer_charges_de_familles()
        net_taxable = G43 - G44
        return net_taxable

    def calculer_net_imposable(self):
        net_imposable = self.calculer_net_taxable()
        return net_imposable

    def calculer_net_imposable_arrondi(self):
        G50 = self.calculer_net_imposable()
        net_imposable_arrondi = round(G50, -3)
        net_imposable_arrondi_str = "{:.0f}".format(net_imposable_arrondi)
        return int(net_imposable_arrondi_str)

    def calculer_irpp_annuel(self):
        """
            Calcul du IRPP annuel de l'employé

            :return: IRPP annuel de l'employé

            :retype: Decimal
        """
        G51 = self.calculer_net_imposable_arrondi()
        if G51 < 900000 or G51 == 900000:
            irpp = G51 * 0
        elif G51 < 3000000 or G51 == 3000000:
            irpp = (G51 - 900000) * 0.03 + 0
        elif G51 < 6000000 or G51 == 6000000:
            irpp = (G51 - 3000000) * 0.1 + 63000
        elif G51 < 9000000 or G51 == 9000000:
            irpp = (G51 - 6000000) * 0.15 + 363000
        elif G51 < 12000000 or G51 == 12000000:
            irpp = (G51 - 9000000) * 0.2 + 813000
        elif G51 < 15000000 or G51 == 15000000:
            irpp = (G51 - 12000000) * 0.25 + 1413000
        elif G51 < 20000000 or G51 == 20000000:
            irpp = (G51 - 15000000) * 0.3 + 2163000
        else:
            irpp = (G51 - 20000000) * 0.35 + 3663000
        return irpp

    def calculer_irpp_mensuel(self):
        """
            Calcul du IRPP mensuel de l'employé

            :return: IRPP mensuel de l'employé

            :retype: Decimal
        """
        irpp_mensuel = self.calculer_irpp_annuel() / 12
        return irpp_mensuel

    def calculer_deductions_cnss(self):
        """
            Calcul des déductions de la CNSS sur le salaire de l'employé

            :return: Déductions de la CNSS

            :retype: Decimal
        """
        frais_prestations_familiale_salsalaire = Decimal(
            self.frais_prestations_familiale_salsalaire) * Decimal(self.calculer_salaire_brut_mensuel())
        deductions = (
            frais_prestations_familiale_salsalaire
        )
        return deductions

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        tcs = Decimal(self.tcs)
        irpp = self.calculer_irpp_mensuel()
        self.irpp = Decimal(irpp)
        prime_forfaitaire = self.prime_forfaitaire
        acomptes = self.acomptes

        salaire_brut = self.calculer_salaire_brut_mensuel()
        deductions = self.calculer_deductions_cnss() + Decimal(irpp) + tcs

        salaire_net = salaire_brut - deductions
        pret = salaire_net - acomptes
        self.salaire_net_a_payer = pret + prime_forfaitaire
        super(Salaire, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.personnel.nom)


class Fournisseur(models.Model):
    """
    Modèle représentant les paiements effectués aux fournisseurs de service.
    """

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
    """
        Fournisseur de service 

        **Type:** string

    """
    montant = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    """
        Montant versé au fourniseur

        **Type:** Decimal

        **Valeur par défaut:** 0.0

    """
    dateversement = models.DateField(
        default=timezone.now, verbose_name="Date de versement")
    """
        Date du versement

        **Type:** string

    """
    le_mois = models.CharField(
        max_length=30, choices=TYPE_MOIS, verbose_name="Mois")
    """
        Mois du versement

        **Type:** string

    """
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    """
        Compte bancaire du fournisseur

        **Type:** string

        **Nullable:** true

    """
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    """
        Année du versement

        **Type:** string

        **Nullable:** true

    """
    facture_pdf = models.FileField(upload_to="pdf/facture_pdf", null=True, blank=True, verbose_name="Pdf de la Facture")
    """
        Pdf du reçu de la facture

        **Type:** Url image

        **Nullable:** true

    """
    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        super(Fournisseur, self).save(*args, **kwargs)


class Information(models.Model):
    """
    Modèle pour enregistrer les informations relatives aux attestations de service des enseignants.
    """
    TYPE_CHOISE = [
        ('Premier', 'Niveau 1'),
        ('Deuxième', 'Niveau 2'),
        ('Troisième', 'Niveau 3'),
    ]
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseigant", null=True)
    """
        Enseignant associé à l'information

        **Type:** string

        **Nullable:** true

    """
    directeur = models.ForeignKey(
        'DirecteurDesEtudes', on_delete=models.CASCADE, verbose_name="Directeur des études", null=True)
    """
        Directeur des études asscocié à l'information

        **Type:** string

        **Nullable:** true

    """
    numeroSecurite = models.IntegerField(
        verbose_name="Numéro de sécurité sociale")
    """
        Numéro de sécurité sociale de l'employé

        **Type:** integer

    """
    discipline = models.ForeignKey(
        'Matiere', on_delete=models.CASCADE, verbose_name="Discipline")
    """
        Matiere enseignée par l'employé

        **Type:** string

    """
    niveau = models.CharField(
        max_length=100, choices=TYPE_CHOISE, verbose_name="Niveau")
    """
        Niveau de l'enseignant

        **Type:** string

    """
    dateDebut = models.DateField(verbose_name="Date de début")
    """
        Date à laquelle l'employé à commencé par travailler

        **Type:** string


    """
    dateFin = models.DateField(verbose_name="Date de fin")
    """
        Date à laquelle l'employé s'est arrêté de travailler

        **Type:** string

    """
    duree = models.CharField(max_length=100, verbose_name="Durée", default='0')
    """
        Durée du contrat de l'employé

        **Type:** string

        **Valeur par défaut:** "0"

    """

    def save(self, *args, **kwargs):
        duree = self.dateFin - self.dateDebut
        self.duree = duree.days if duree.days > 0 else 0
        super(Information, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.enseignant.nom) + " " + str(self.numeroSecurite) + " " + str(self.discipline.libelle)


class FicheDePaie(models.Model):
    """
    Modèle représentant les fiches de paie des enseignants.
    """
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    """
        Date à laquelle l'employé à commencé

        **Type:** string

        **Nullable:** true

    """
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    """
        Date à laquelle l'employé s'est arrêté

        **Type:** string

        **Nullable:** true

    """
    matiere = models.ManyToManyField('Matiere', related_name="Matières", blank=True, null=True)
    """
        Matières enseignées par le reçeveur de la fiche de paie

        **Type:** string

    """
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant")
    """
        Identifiant de l'enseignant reçevant la fiche de paie

        **Type:** string

    """
    nombreHeureL1 = models.IntegerField(
        verbose_name="Nombre d'heure L1", default=0)
    """
        Nombre d'heure réalisées en L1

        **Type:** integer

        **Valeur par défaut:** 0

    """
    nombreHeureL2 = models.IntegerField(
        verbose_name="Nombre d'heure L2", default=0)
    """
        Nombre d'heures réalisées en L2

        **Type:** integer

        **Valeur par défaut:** 0

    """
    nombreHeureL3 = models.IntegerField(
        verbose_name="Nombre d'heure L3", default=0)
    """
        Nombre d'heures réalisées en L3

        **Type:** integer

        **Valeur par défaut:** 0

    """
    nombreHeure = models.IntegerField(verbose_name="Nombre d'heure", default=0)
    """
        Nombre d'heures au total

        **Type:** integer

        **Valeur par défaut:** 0

    """
    prixUnitaire = models.IntegerField(verbose_name="Prix unitaire", default=0)
    """
        Prix unitaire de l'heure

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montantL1 = models.IntegerField(verbose_name="montant L1", default=0)
    """
        Montant total en L1

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montantL2 = models.IntegerField(verbose_name="montant L2", default=0)
    """
        Montant total en L2

        **Type:** integer

        **Valeur par défaut:** 0
    """
    montantL3 = models.IntegerField(verbose_name="montant L3", default=0)
    """
        Montant total en L3

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montant = models.IntegerField(verbose_name="montant", default=0)
    """
        Montant total

        **Type:** integer

        **Valeur par défaut:** 0

    """
    difference = models.IntegerField(verbose_name="Différence", default=0)
    """
        Différence

        **Type:** integer

        **Valeur par défaut:** 0

    """
    acomptes = models.IntegerField(verbose_name="Acomptes", default=0)
    """
        Acompte

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montantEnLettre = models.CharField(
        max_length=100, verbose_name="Montant en lettre", default="lettres")
    """
        Montant en lettres du paiement
    
        **Type:** string

        **Valeur par défaut:** "lettres"

    """
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    """
        Compte bancaire du bénéficiare

        **Type:** string

        **Nullable:** true

    """
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    """
        Année Universitaire au correspondant au paiement

        **Type:** string

        **Nullable:** true

    """

    def __str__(self):
        return str(self.enseignant.nom) + "  " + str(self.enseignant.prenom) + "  " + str(self.dateDebut) + "-" + str(self.dateFin)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        self.montantL1 = self.nombreHeureL1 * self.prixUnitaire
        self.montantL2 = self.nombreHeureL2 * self.prixUnitaire
        self.montantL3 = self.nombreHeureL3 * self.prixUnitaire
        heure_totale = self.nombreHeure = self.nombreHeureL1 + \
            self.nombreHeureL2 + self.nombreHeureL3
        self.montant = heure_totale * self.prixUnitaire
        difference = self.difference = self.montant - self.acomptes
        self.montantEnLettre = num2words(difference, lang='fr')
        super(FicheDePaie, self).save(*args, **kwargs)


class Charge(models.Model):
    """
    Modèle représentant les fiches de prise en charge des frais pour le personnel.
    """
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    """
        Date de debut de la prise en charge

        **Type:** string

        **Nullable:** true
    """
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    """
        Date de fin de la prise en charge

        **Type:** string

        **Nullable:** true

    """
    personnel = models.ForeignKey(
        'Personnel', on_delete=models.CASCADE, verbose_name="Personnel")
    """
        Employé pris en charge

        **Type:** string

    """
    frais_de_vie = models.IntegerField(verbose_name="Frais de vie", default=20000)
    """
        Contribution des Frais de vie de l'employé par l'IFNTI

        **Type:** integer

        **Valeur par défaut:** 0

    """
    frais_nourriture = models.IntegerField(
        verbose_name="Frais de nourriture", default=70000)
    """
        Contribution des Frais de nourriture de l'employé par l'IFNTI

        **Type:** integer

        **Valeur par défaut:** 0

    """
    frais_de_vie_dcc = models.IntegerField(verbose_name="Frais de vie DCC", default=0)
    """
        Contribution des Frais de vie de l'employé pas la DCC 

        **Type:** integer

        **Valeur par défaut:** 0

    """
    frais_nourriture_dcc = models.IntegerField(
        verbose_name="Frais de nourriture DCC", default=0)
    """
        Contribution des Frais de nourriture de l'employé pas la DCC 

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montant = models.IntegerField(verbose_name="Montant", default=0)
    """
        Montant de la facture

        **Type:** integer

        **Valeur par défaut:** 0

    """
    montantEnLettre = models.CharField(
        max_length=100, verbose_name="Montant en lettre", default="lettres")
    """
        Montant en lettre de la facture

        **Type:** string

        **Valeur par défaut:** "lettres"

    """
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    """
        Année Universitaire au correspondant à la facture

        **Type:** string

        **Nullable:** true

    """
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    """
        Compte bancaire de versement

        **Type:** string

        **Nullable:** true

    """

    def __str__(self):
        """
             __str__(): Renvoie une représentation en chaîne de caractères de la prise en charge.
        """
        return str(self.personnel.nom) + "  " + str(self.personnel.prenom) + "  " + str(self.dateDebut) + "-" + str(self.dateFin)

    def save(self, *args, **kwargs):
        """
            save(*args, **kwargs): Enregistre les détails de la prise en charge dans la base de données.
        """
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        total = self.frais_de_vie + self.frais_nourriture + self.frais_de_vie_dcc + self.frais_nourriture_dcc
        self.montant = total
        self.montantEnLettre = num2words(total, lang='fr')
        super(Charge, self).save(*args, **kwargs)


class Conge(models.Model):
    """
    Modèle représentant les demandes de congé du personnel.

    """
    NATURE_CHOICES = [
        ('Congé annuel', 'Congé annuel'),
        ('Congé de maternité', 'Congé de maternité'),
        ('Congé de paternité', 'Congé de paternité'),
        ('Autres', 'Autres'),
    ]
    VALIDATION_CHOICES = [
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
        ('Inconnu', 'Inconnu'),
    ]

    nature = models.CharField(
        max_length=30, choices=NATURE_CHOICES, verbose_name="Nature des congés")
    """
        Nature de la demande de congés 

        **Type:** string

    """
    autre_nature = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Autre nature à préciser")
    """
        Nature secondaire de la demande de congés

        **Type:** string

        **Nullable:** true

    """
    date_et_heure_debut = models.DateField(
        default=timezone.now, verbose_name="Date de début")
    """
        Date de début des congés

        **Type:** string

    """
    date_et_heure_fin = models.DateField(
        default=timezone.now, verbose_name="Date de fin")
    """
        Date de fin des congés

        **Type:** string

    """
    personnel = models.ForeignKey(
        'Personnel', on_delete=models.CASCADE, verbose_name="Personnel", null=True)
    """
        Identifiant de l'employé partant en congés

        **Type:** string

    """
    motif_refus = models.TextField(
        null=True, blank=True, verbose_name="Motif de refus")
    """
        Motif de refus des congés 

        **Type:** string

        **Nullable:** true

    """
    valider = models.CharField(
        max_length=30, choices=VALIDATION_CHOICES, verbose_name="État", default="Inconnu")
    """
        Validation des congés

        **Type:** string

        **Valeur par défaut:** "Inconnu"

    """
    nombre_de_jours_de_conge = models.IntegerField(default=0)
    """
        Nombre de jours de congés demandés

        **Type:** integer

        **Valeur par défaut:** 0

    """
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    """
        Année Universitaire des congés

        **Type:** integer

        **Nullable:** true

    """

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        duree = self.date_et_heure_fin - self.date_et_heure_debut
        self.nombre_de_jours_de_conge = duree.days if duree.days > 0 else 0
        super(Conge, self).save(*args, **kwargs)
        self.personnel.update_conge_counts()

    def __str__(self):
        return str(self.personnel.nom) + "  " + str(self.personnel.prenom) + "  " + str(self.nombre_de_jours_de_conge)
