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


class Utilisateur(models.Model):
    """
    Modèle représentant un utilisateur du système.

    Attributes:
        SEXE_CHOISE (list): Liste des choix de sexe pour l utilisateur.
        nom (str): Nom de l'utilisateur.
        prenom (str): Prénom de l'utilisateur.
        sexe (str): Sexe de l'utilisateur (F pour féminin, M pour masculin).
        datenaissance (date): Date de naissance de l'utilisateur.
        lieunaissance (str): Lieu de naissance de l'utilisateur.
        contact (str): Numéro de contact de l'utilisateur.
        email (str): Adresse e-mail de l'utilisateur.
        adresse (str): Adresse de l'utilisateur.
        prefecture (str): Préfecture de l'utilisateur.
        is_active (bool): Statut d'activation de l'utilisateur.
        carte_identity (str): Numéro de carte d'identité de l'utilisateur.
        nationalite (str): Nationalité de l'utilisateur.
        user (User): Référence à l'utilisateur authentifié associé.
        photo_passport (ImageField): Photo de passeport de l'utilisateur.

    Methods:
        __str__(): Renvoie une représentation en chaîne de caractères de l'utilisateur.
        full_name(): Renvoie le nom complet de l'utilisateur en majuscules.
        getrole(): Renvoie le rôle de l'utilisateur.
        suspendre(): Suspend l'utilisateur.
        reactiver(): Réactive l'utilisateur.

    """
    SEXE_CHOISE = [
        ('F', 'Feminin'),
        ('M', 'Masculin')
    ]
    nom = models.CharField(max_length=50)

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
    """

    email = models.CharField(max_length=50, null=True)

    """
        Email de ml'utilisateur

        **Type**:    string
    """

    adresse = models.CharField(max_length=50, null=True)

    """
        Adresse de l'utilisateur

        **Type**:    string
    """

    prefecture = models.CharField(
        max_length=50, null=True, verbose_name="Préfecture", default='tchaoudjo', blank=True)

    """
        Préfecture de provenance de l'utilisateur

        **Type**:    string
    """

    is_active = models.BooleanField(
        default=True, verbose_name="Actif", null=True)

    """
        Statut de l'utilisateur (actif ou inactif)

        **Type**:    string
    """

    carte_identity = models.CharField(
        max_length=50, null=True,  verbose_name="Carte d'identité")

    """
        Carte d'identitée de l'utilisateur    
    
        **Type**:    string
    """

    nationalite = models.CharField(
        max_length=30, default='Togolaise', verbose_name='Nationalté', blank=True)

    """
        Attestation de nationalité de l'utilisateur

        **Type**:    string
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    photo_passport = models.ImageField(
        null=True, blank=True, verbose_name="Photo passport")

    """
        Photo passeport de l'utilisateur

        **Type**:    string
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
    """

    seriebac2 = models.CharField(
        blank=True, max_length=2, choices=CHOIX_SERIE, verbose_name="Série bac 2", null=True)

    """
        Série de l'étudiant en Terminale

        **Type**:    string
    """

    anneeentree = models.IntegerField(default=datetime.date.today(
    ).year, blank=True, verbose_name="Promotion", null=True)

    """
        Série de l'étudiant en Terminale

        **Type**:    string
    """

    anneebac1 = models.IntegerField(
        blank=True, verbose_name="Année d’obtention du BAC 1", null=True)

    """
        Année d'obtention du BAC 1

        **Type**:    integer
    """

    anneebac2 = models.IntegerField(
        blank=True, verbose_name="Année d’obtention du BAC 2", null=True, default=datetime.date.today().year)

    """
        Année d'obtention du BAC 2

        **Type**:    integer
    """

    etablissementSeconde = models.CharField(
        max_length=300, verbose_name="Nom d'établissement seconde", null=True, blank=True)

    """
        Établissement de 2nde de l'étudiant

        **Type**:    string
    """

    francaisSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Seconde", default="0")

    """
        Note en français en classe de 2nde de l'étudiant

        **Type**:    integer
    """

    anglaisSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Seconde", default="0")

    """
        Note en anglais en classe de 2nde de l'étudiant

        **Type**:    integer
    """

    mathematiqueSeconde = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Seconde", default="0")

    """
        Note en mathematique en classe de 2nde de l'étudiant

        **Type**:    integer
    """

    etablissementPremiere = models.CharField(
        max_length=300, verbose_name="Nom d'établissement Première", null=True, blank=True)

    """
        Établissement de 1ere de l'étudiant


        **Type**:    string
    """

    francaisPremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Première", default="0")

    """
        Note en français en classe de 1ere de l'étudiant

        **Type**:    integer
    """

    anglaisPremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Première", default="0")

    """
        Note en anglais en classe de 1ere de l'étudiant

        **Type**:    integer
    """

    mathematiquePremiere = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Première", default="0")

    """
        Note en mathématiques en classe de 1ere de l'étudiant

        **Type**:    integer
    """

    etablissementTerminale = models.CharField(
        max_length=300, verbose_name="Nom d'établissement Terminale", null=True, blank=True)

    """
        Établissement de Terminale de l'étudiant

        **Type**:    string
    """

    francaisTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de français Terminale", default="0")

    """
        Note en français en classe de Terminale de l'étudiant

        **Type**:    integer
    """

    anglaisTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note d'anglais Terminale", default="0")

    """
        Note en anglais en classe de Terminale de l'étudiant

        **Type**:    integer
    """

    mathematiqueTerminale = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Note de mathématique Terminale", default="0")

    """
        Note en mathématiques en classe de Terminale de l'étudiant

        **Type**:    integer
    """

    delegue = models.BooleanField(
        default=False, verbose_name="delegué", null=True)

    """
        Attribut permettant de savoir si l'étudiant est le délégué de sa classe 

        **Type**:    boolean
    """

    passer_semestre_suivant = models.BooleanField(
        default=False, verbose_name="Passer au semestre suivant")

    """
        Permet de savoir si l'étudiant passe au semestre suivant

        **Type**:    boolean
    """

    decision_conseil = models.TextField(
        verbose_name="Décision du conseil", null=True, default="Décision du conseil")

    """
        Décision du conseil sur lors du passage au niveau supérieur

        **Type**:    string
    """

    profil = models.ImageField(
        null=True, blank=True, verbose_name="Photo de profil")

    """
        Photo de profil

        **Type**:    string
    """

    semestres = models.ManyToManyField('Semestre', null=True)

    """
        Liste des semestres de l'étudiant

        **Type**:    list[Semestre]
    """

    tuteurs = models.ManyToManyField(
        'Tuteur', related_name="Tuteurs", blank=True, null=True)

    """
        Tuteurs de l'étudiant

        **Type**:    list[Tuteur]
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
        Méthode pour sauvegarder un étudiant"""
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

        for matiere in matieres:
            note, _, annee = self.moyenne_etudiant_matiere(matiere, semestre)
            somme_note += float(note) * float(matiere.coefficient)
            somme_coef += matiere.coefficient
            # ici on effectue une comparaison pou récupérer l'année scolaire la plus élevée
            # il s'agit en réalité de l'année de la validation du dernier rattrapage
            if anneeValidation < annee:
                anneeValidation = annee

        moyenne = round(somme_note/somme_coef, 2)
        matiere_principale = ue.matiere_principacle()
        a_valide = moyenne >= matiere_principale.minValue
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
    id = models.CharField(primary_key=True, blank=True, max_length=12, editable=False)
    salaireBrut = models.DecimalField(max_digits=15, decimal_places=2,  verbose_name="Salaire Brut", default=0)
    dernierdiplome = models.ImageField(null=True, blank=True, verbose_name="Dernier diplome")
    nbreJrsCongesRestant = models.IntegerField(verbose_name="Nbre jours de congé restant", default=0)
    nbreJrsConsomme = models.IntegerField(verbose_name="Nombre de jours consommé", default=0)
    nombre_de_personnes_en_charge = models.IntegerField(verbose_name="Nbre de pers pris en charge", default=0)
    
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
        # Ajoutez la condition de validation ici
        conges_pris = Conge.objects.filter(personnel=self, valider='Actif')
        total_jours_pris = conges_pris.aggregate(
            total=Sum('nombre_de_jours_de_conge'))['total'] or 0
        self.nbreJrsConsomme = total_jours_pris
        self.nbreJrsCongesRestant = 30 - \
            total_jours_pris if total_jours_pris <= 30 else 0  # Mise à zéro si dépassement
        self.save()

    def calculer_salaire_brut_annuel(self):
        salaires = Salaire.objects.filter(personnel=self)
        total_salaire_brut_annuel = sum(
            salaire.calculer_salaire_brut_mensuel() for salaire in salaires)
        return total_salaire_brut_annuel

    def calculer_irpp_tcs_annuel(self):
        salaires = Salaire.objects.filter(personnel=self)
        total_irpp_annuel = sum(salaire.calculer_irpp_mensuel()
                                for salaire in salaires)
        total_tcs_annuel = sum(salaire.tcs for salaire in salaires)
        total_irpp_tcs_annuel = Decimal(
            total_irpp_annuel) + Decimal(total_tcs_annuel)
        total_irpp_tcs_annuel = total_irpp_tcs_annuel.quantize(
            Decimal('0.00'), rounding=ROUND_DOWN)
        return total_irpp_tcs_annuel

    def calcule_deductions_cnss_annuel(self):
        salaires = Salaire.objects.filter(personnel=self)

        total_deductions_cnss = sum(salaire.calculer_deductions_cnss() for salaire in salaires)
        #total_deductions_cnss = total_deductions_cnss.quantize(Decimal('0.00'), rounding=ROUND_DOWN) 

        return Decimal(total_deductions_cnss)


class DirecteurDesEtudes(Personnel):
    """
    Modèle représentant le directeur des études de l'organisation.

    Attributes:
        id (str): Identifiant unique du directeur des études.
        nom (str): Nom du directeur des études.
        prenom (str): Prénom du directeur des études.
        email (str): Adresse e-mail du directeur des études.
        is_active (bool): Indique si le directeur des études est actif ou non.

    Methods:
        save(*args, **kwargs): Enregistre le directeur des études dans la base de données.
        delete(*args, **kwargs): Supprime le directeur des études de la base de données.
        __str__(): Renvoie une représentation en chaîne du directeur des études.

    Meta:
        verbose_name = "Directeur des études"
        verbose_name_plural = "Directeurs des études"

    """
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
            DirecteurDesEtudes.objects.exclude(
                pk=self.pk).update(is_active=False)

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
    """
    Modèle représentant un enseignant dans l'organisation.

    Attributes:
        id (str): Identifiant unique de l'enseignant.
        nom (str): Nom de l'enseignant.
        prenom (str): Prénom de l'enseignant.
        email (str): Adresse e-mail de l'enseignant.
        type (str): Type d'enseignant (vacataire ou permanent).
        specialite (str): Spécialité de l'enseignant.

    Methods:
        save(force_insert=False, force_update=False, using=None): Enregistre l'enseignant dans la base de données.
        niveaux(): Renvoie les niveaux d'enseignement de l'enseignant.
        __str__(): Renvoie une représentation en chaîne de l'enseignant.

    """
    CHOIX_TYPE = (('Vacataire', 'Vacataire'), ('Permanent', 'Permanent'))
    type = models.CharField(null=True, blank=True,
                            max_length=9, choices=CHOIX_TYPE)
    specialite = models.CharField(
        max_length=300, verbose_name="Spécialité", blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            enseignants = Enseignant.objects.all()
            if enseignants:
                n = 1
                rang = "0" + str(len(enseignants) + n) if len(enseignants) + \
                    n < 10 else str(len(enseignants) + n)
                val_id = self.nom[0] + self.prenom[0] + rang
                for i in [ens.id for ens in enseignants]:
                    if val_id == i:
                        n = n + 1
                        rang = "0" + \
                            str(len(enseignants) + n) if len(enseignants +
                                                             n) < 10 else str(len(enseignants) + n)
                        val_id = self.nom[0] + self.prenom[0] + rang
                self.id = val_id
            else:
                self.id = self.nom[0] + self.prenom[0] + "0" + str(1)

            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(username=username, password=password,
                                            email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=False)
            self.user = user
            group_enseignant = Group.objects.get(name="enseignant")
            self.user.groups.add(group_enseignant)
        super().save()

    def niveaux(self):
        matieres = self.matiere_set.all()
        niveaux = set()
        for matiere in matieres:
            result = matiere.ue.programme_set.values('semestre')
            temp_semstres_libelles = [AnneeUniversitaire.getNiveau(
                elt['semestre'][:2]) for elt in result]
            niveaux.update(temp_semstres_libelles)

        return list(niveaux)

    def __str__(self):
        return f'{super().__str__()}'
        # return f'{self.user.username}'


class Comptable(Personnel):
    pass

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            Comptables = Comptable.objects.all()
            if Comptables:
                n = 1
                rang = "0" + str(len(Comptables) + n) if len(Comptables) + \
                    n < 10 else str(len(Comptables) + n)
                val_id = self.nom[0] + self.prenom[0] + rang
                for i in [comp.id for comp in Comptables]:
                    if val_id == i:
                        n = n + 1
                        rang = "0" + \
                            str(len(Comptables) + n) if len(Comptables +
                                                            n) < 10 else str(len(Comptables) + n)
                        val_id = self.nom[0] + self.prenom[0] + rang
                self.id = val_id
            else:
                self.id = self.nom[0] + self.prenom[0] + "0" + str(1)

            username = (self.prenom + self.nom).lower()
            year = date.today().year
            password = 'ifnti' + str(year) + '!'
            user = User.objects.create_user(username=username, password=password,
                                            email=self.email, last_name=self.nom, first_name=self.prenom, is_staff=False)
            self.user = user
            group_comptable = Group.objects.get(name="comptable")
            self.user.groups.add(group_comptable)
        super().save()


class Tuteur(models.Model):
    """
    Modèle représentant un tuteur ou un parent d'un étudiant.

    Attributes:
        CHOIX_SEX (list): Liste des choix de sexe pour le tuteur.
        CHOIX_TYPE (list): Liste des choix de type de tuteur (père, mère, tuteur).

        nom (str): Nom du tuteur.
        prenom (str): Prénom du tuteur.
        sexe (str): Sexe du tuteur (F pour féminin, M pour masculin).
        adresse (str): Adresse du tuteur.
        contact (str): Numéro de contact du tuteur.
        profession (str): Profession du tuteur.
        type (str): Type de tuteur (père, mère, tuteur).

    Methods:
        save(): Enregistre le tuteur dans la base de données et crée un utilisateur associé.
        __str__(): Renvoie une représentation en chaîne de caractères du tuteur.

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
    codematiere = models.CharField(
        max_length=50, verbose_name="Code de la matière", blank=True)
    libelle = models.CharField(max_length=100)
    coefficient = models.IntegerField(null=True,  verbose_name="Coefficient", default="1")
    minValue = models.FloatField(null=True,  verbose_name="Valeur minimale",  default="7")
    heures = models.DecimalField(blank=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(1)], null=True) 
    abbreviation = models.CharField(max_length=20,default ="Short", unique=True)
    enseignant = models.ForeignKey(Enseignant, blank=True, null=True, verbose_name="Enseignants responsable", on_delete=models.CASCADE)
    #enseignants = models.ManyToManyField(Enseignant, related_name="EnseignantsMatiere", blank=True, null=True, verbose_name="Enseignants")
    ue = models.ForeignKey('Ue', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def save(self, *args, **kwargs):
        print("Save Matière")
        if not self.codematiere and len(self.codematiere) == 0:
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
                _, a_valide, _ = etudiant.moyenne_etudiant_matiere(
                    self, semestre)
                if not a_valide:
                    etudiants.update([etudiant])
        return list(etudiants)

    def get_etudiant_semestre(self, semestre):
        return semestre.etudiant_set.all()

# class EnseignantsMatiere(models.Model):
#     enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name="Enseignant")
#     matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, verbose_name="Matière")
#     est_responsable = models.BooleanField(verbose_name="Est responsable", default=False)


class Evaluation(models.Model):
    libelle = models.CharField(max_length=258, verbose_name="Nom")
    ponderation = models.IntegerField(default=1, verbose_name="Pondération (1-100)", validators=[MinValueValidator(1), MaxValueValidator(100)])
    date = models.DateField(verbose_name="Date évaluation")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, verbose_name='Matiere')
    etudiants = models.ManyToManyField(Etudiant, through='Note', verbose_name="Étudiants")
    semestre = models.ForeignKey('Semestre', on_delete=models.CASCADE, null=True)
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
    annee = models.DecimalField(max_digits=4, decimal_places=0, verbose_name="Année universitaire", unique=True)
    annee_courante = models.BooleanField(default=False, verbose_name="Année universitaire acutuelle", null=True)

    def save(self, *args, **kwargs):
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
            
            # Rechercher l'année  réel courante
            print("::: IN TRY ::::")
            if virtual_current_university_date.annee == current_date.year and current_date.month >= 8 :
                virtual_current_university_date.disable()
                return AnneeUniversitaire.objects.create(annee=current_date.year, annee_courante=True)
            return virtual_current_university_date
        except Exception as e:
            print("::: IN except ::::")
            return -1

    @staticmethod
    def getNiveau(semestre_libelle):
        data = {'L1': ['S1', 'S2'], 'L2': ['S3', 'S4'], 'L3': ['S5', 'S6']}
        for key in data:
            if semestre_libelle in data[key]:
                return key
        return

    def __str__(self):
        return f'{self.annee}-{self.annee + 1}'


class Semestre(models.Model):
    id = models.CharField(primary_key=True, blank=True, max_length=14)
    CHOIX_SEMESTRE = [('S1', 'Semestre1'), ('S2', 'Semestre2'), ('S3', 'Semestre3'),('S4', 'Semestre4'), ('S5', 'Semestre5'), ('S6', 'Semestre6')]
    libelle = models.CharField(max_length=30, choices=CHOIX_SEMESTRE)
    credits = models.IntegerField(default=30)
    courant = models.BooleanField(default=False, verbose_name="Semestre actuel", null=True)
    annee_universitaire = models.ForeignKey(AnneeUniversitaire, on_delete=models.SET_NULL, null=True)

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


class Parcours(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    domaine = models.ForeignKey(
        Domaine, on_delete=models.CASCADE, verbose_name="Domaine", null=True)
    description = models.TextField(max_length=500, verbose_name="description")

    def __str__(self):
        return self.nom


class Programme(models.Model):
    parcours = models.ForeignKey(
        Parcours, on_delete=models.CASCADE, verbose_name="Parcours", null=True, blank=True)
    semestre = models.ForeignKey(
        Semestre, on_delete=models.CASCADE, verbose_name="Semestre")
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

class Settings(models.Model):
    pass

class CorrespondanceMaquette(models.Model):
    class Nature(models.TextChoices):
        UE = "U", "UE"
        MATIERE = "M", "Matière"

    nature = models.CharField(max_length=1, choices=Nature.choices)
    ancienne = models.CharField(max_length=225, blank=True, null=True)
    nouvelle = models.CharField(max_length=225, blank=True, null=True)

    def save(self):
        super().save()

    def afficher_nature(self):
        return "UE" if self.nature.lower() == 'u' else "Matière"

    def get_ancienne(self):
        return Ue.objects.get(id=self.ancienne) if self.nature.lower() == 'u' else Matiere.objects.get(id=self.ancienne)

    def get_nouvelle(self):
        return Ue.objects.get(id=self.nouvelle) if self.nature.lower() == 'u' else Matiere.objects.get(id=self.nouvelle)


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
    """
    Modèle représentant le compte associé à un étudiant pour une année universitaire donnée.

    Attributes:
        etudiant (Etudiant): Référence à l'étudiant associé au compte.
        annee_universitaire (AnneeUniversitaire): Année universitaire associée au compte.
        solde (Decimal): Solde du compte.

    Methods:
        __str__(): Renvoie une représentation en chaîne de caractères du compte étudiant.

    """
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.CASCADE)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.etudiant.nom) + str(self.etudiant.prenom) + "  Solde - " + str(self.annee_universitaire) + " : " + str(self.solde)


class Paiement(models.Model):
    """
    Modèle représentant les versements effectués par les étudiants.

    Attributes:
        TYPE_CHOICES (list): Liste des choix de type de versement.

        type (str): Type de versement (frais de scolarité, frais d'inscription, etc.).
        montant (Decimal): Montant versé.
        dateversement (date): Date du versement.
        etudiant (Etudiant): Référence à l'étudiant effectuant le versement.
        comptable (Comptable): Référence au comptable en charge du versement.
        compte_bancaire (CompteBancaire): Référence au compte bancaire utilisé pour le versement (optionnel).
        numerobordereau (str): Numéro de bordereau du versement.
        annee_universitaire (AnneeUniversitaire): Année universitaire associée au versement.

    Methods:
        __str__(): Renvoie une représentation en chaîne de caractères du versement.

    """
    TYPE_CHOICES = [
        ('Frais de scolarité', 'Frais de scolarité'),
        ("Frais d'inscription", "Frais d'inscription"),
    ]
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    montant = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    dateversement = models.DateField(
        default=timezone.now, verbose_name="Date de versement")
    etudiant = models.ForeignKey(
        'Etudiant', on_delete=models.CASCADE, verbose_name="Etudiant")
    comptable = models.ForeignKey(
        'Comptable', on_delete=models.CASCADE, verbose_name="Comptable")
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    numerobordereau = models.CharField(
        max_length=30, verbose_name="Numéro de bordereau", default=0)
    annee_universitaire = models.ForeignKey(
        AnneeUniversitaire, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.dateversement) + " : " + str(self.etudiant.nom) + "  " + str(self.etudiant.prenom) + "  " + str(self.montant)


class CompteBancaire(models.Model):
    """
    Modèle représentant un compte bancaire.

    Attributes:
        numero (str): Le numéro du compte bancaire.
        solde_bancaire (decimal): Le solde du compte bancaire.
        frais_tenue_de_compte (decimal): Les frais de tenue de compte.

    Methods:
        __str__() -> str: Renvoie une représentation en chaîne de caractères de l'objet CompteBancaire.
    """
    numero = models.CharField(max_length=100, verbose_name="Numéro du compte")
    solde_bancaire = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    frais_tenue_de_compte = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Frais de tenue de compte")

    def __str__(self):
        """
        Renvoie une représentation en chaîne de caractères de l'objet CompteBancaire.
        """
        return "Solde actuel : " + str(self.solde_bancaire)


class Salaire(models.Model):
    """
    Modèle représentant les détails du salaire d'un personnel.

    Attributes:
        date_debut (date): La date de début de la période de paie.
        date_fin (date): La date de fin de la période de paie.
        personnel (Personnel): La référence au personnel concerné par le salaire.
        tcs (decimal): Le montant de la taxe sur les salaires.
        prime_forfaitaire (decimal): Le montant de la prime forfaitaire.
        acomptes (decimal): Le montant des acomptes versés au personnel.
        frais_prestations_familiale_salsalaire (decimal): Les frais de prestations familiales sur le salaire.
        
    Methods:
        calculer_salaire_brut_annuel() -> decimal: Calcule le salaire brut annuel du personnel.
        calculer_salaire_brut_mensuel() -> decimal: Calcule le salaire brut mensuel du personnel.
        calculer_total_A() -> decimal: Calcule le total A.
        calculer_net_imposable_arrondi() -> int: Calcule le net imposable arrondi.
        calculer_irpp_annuel() -> decimal: Calcule l'impôt sur le revenu des personnes physiques (IRPP) annuel.
        calculer_irpp_mensuel() -> decimal: Calcule l'IRPP mensuel.
        calculer_deductions_cnss() -> decimal: Calcule les déductions CNSS.
        save(*args, **kwargs): Enregistre les détails du salaire dans la base de données.
    """
    TYPE_CHOICES = [
        ('Enseignant', 'Enseignant'),
        ("Comptable", "Comptable"),
        ("Directeur des études", "Directeur des études"),
        ("Gardien", "Gardien"),
        ("Agent d'entretien", "Agent d'entretien"),
    ]
    date_debut = models.DateField(verbose_name="Date de début", null=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True)
    personnel = models.ForeignKey(
        Personnel, on_delete=models.CASCADE, null=False)
    numero_cnss = models.CharField(
        max_length=30, verbose_name="Numéro CNSS", default=0)
    qualification_professionnel = models.CharField(
        max_length=30, choices=TYPE_CHOICES, verbose_name="Qualification professionnelle")
    prime_efficacite = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'éfficacité")
    prime_qualite = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime de qualité")
    frais_travaux_complementaires = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Travaux complémentaires")
    prime_anciennete = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime d'ancienneté")
    frais_prestations_familiales = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.03)
    frais_risques_professionnel = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.02)
    frais_pension_vieillesse_emsalaire = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.125)
    frais_prestations_familiale_salsalaire = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.04)
    tcs = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="TCS")
    irpp = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="IRPP")
    prime_forfaitaire = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prime forfaitaires")
    acomptes = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Acomptes")
    salaire_net_a_payer = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Salaire Net à payer")
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def calculer_salaire_brut_annuel(self):
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
        irpp_mensuel = self.calculer_irpp_annuel() / 12
        return irpp_mensuel

    def calculer_deductions_cnss(self):
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



        salaire_brut =  self.calculer_salaire_brut_mensuel()
        deductions = self.calculer_deductions_cnss() +Decimal(irpp) + tcs

        salaire_net = salaire_brut - deductions
        pret = salaire_net - acomptes
        self.salaire_net_a_payer = pret + prime_forfaitaire
        super(Salaire, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.personnel.nom) 
    

class Fournisseur(models.Model):
    """
    Modèle représentant les paiements effectués aux fournisseurs de service.

    Attributes:
        TYPE (list): Liste des types de fournisseurs.
        TYPE_MOIS (list): Liste des mois.
        type (str): Le type de fournisseur.
        montant (decimal): Le montant versé au fournisseur.
        dateversement (date): La date de versement du paiement.
        le_mois (str): Le mois auquel le paiement est associé.
        compte_bancaire (CompteBancaire): La référence au compte bancaire utilisé pour le paiement.
        annee_universitaire (AnneeUniversitaire): L'année universitaire associée au paiement.

    Methods:
        save(*args, **kwargs): Enregistre les détails du paiement dans la base de données.

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
    montant = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant versé")
    dateversement = models.DateField(
        default=timezone.now, verbose_name="Date de versement")
    le_mois = models.CharField(
        max_length=30, choices=TYPE_MOIS, verbose_name="Mois")
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        super(Fournisseur, self).save(*args, **kwargs)


class Information(models.Model):
    """
    Modèle pour enregistrer les informations relatives aux attestations de service des enseignants.

    Attributes:
        TYPE_CHOISE (list): Liste des choix de niveaux.
        enseignant (Enseignant): Référence à l'enseignant associé à l'attestation.
        directeur (DirecteurDesEtudes): Référence au directeur des études associé à l'attestation.
        numeroSecurite (int): Numéro de sécurité sociale de l'enseignant.
        discipline (Matiere): La discipline associée enseigné par l'enseignant.
        niveau (str): Le niveau enseigné par l'enseignant.
        dateDebut (date): Date de début du contrat.
        dateFin (date): Date de fin du contrat.
        duree (str): Durée du contrat en jours.

    Methods:
        save(*args, **kwargs): Enregistre les détails de l'attestation dans la base de données.
        __str__(): Renvoie une représentation en chaîne de caractères de l'attestation.

    """
    TYPE_CHOISE = [
        ('Premier', 'Niveau 1'),
        ('Deuxième', 'Niveau 2'),
        ('Troisième', 'Niveau 3'),
    ]
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseigant", null=True)
    directeur = models.ForeignKey(
        'DirecteurDesEtudes', on_delete=models.CASCADE, verbose_name="Directeur des études", null=True)
    numeroSecurite = models.IntegerField(
        verbose_name="Numéro de sécurité sociale")
    discipline = models.ForeignKey(
        'Matiere', on_delete=models.CASCADE, verbose_name="Discipline")
    niveau = models.CharField(
        max_length=100, choices=TYPE_CHOISE, verbose_name="Niveau")
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
    """
    Modèle représentant les fiches de paie des enseignants.

    Attributes:
        dateDebut (date): Date de début de la période de paie.
        dateFin (date): Date de fin de la période de paie.
        matiere (Matiere): Référence à la matière enseignée.
        enseignant (Enseignant): Référence à l'enseignant concerné par la fiche de paie.
        nombreHeureL1 (int): Nombre d'heures enseignées pour le niveau 1.
        nombreHeureL2 (int): Nombre d'heures enseignées pour le niveau 2.
        nombreHeureL3 (int): Nombre d'heures enseignées pour le niveau 3.
        nombreHeure (int): Nombre total d'heures enseignées.
        prixUnitaire (int): Prix unitaire par heure.
        montantL1 (int): Montant total pour le niveau 1.
        montantL2 (int): Montant total pour le niveau 2.
        montantL3 (int): Montant total pour le niveau 3.
        montant (int): Montant total.
        difference (int): Différence entre le montant total et les acomptes.
        acomptes (int): Montant des acomptes déjà versés.
        montantEnLettre (str): Montant total en lettres.
        compte_bancaire (CompteBancaire): Référence au compte bancaire utilisé pour le paiement.
        annee_universitaire (AnneeUniversitaire): Année universitaire associée à la fiche de paie.

    Methods:
        save(*args, **kwargs): Enregistre les détails de la fiche de paie dans la base de données.
        __str__(): Renvoie une représentation en chaîne de caractères de la fiche de paie.

    """
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    matiere = models.ForeignKey(
        'Matiere', on_delete=models.CASCADE, verbose_name="Matière")
    enseignant = models.ForeignKey(
        'Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant")
    nombreHeureL1 = models.IntegerField(
        verbose_name="Nombre d'heure L1", default=0)
    nombreHeureL2 = models.IntegerField(
        verbose_name="Nombre d'heure L2", default=0)
    nombreHeureL3 = models.IntegerField(
        verbose_name="Nombre d'heure L3", default=0)
    nombreHeure = models.IntegerField(verbose_name="Nombre d'heure", default=0)
    prixUnitaire = models.IntegerField(verbose_name="Prix unitaire", default=0)
    montantL1 = models.IntegerField(verbose_name="montant L1", default=0)
    montantL2 = models.IntegerField(verbose_name="montant L2", default=0)
    montantL3 = models.IntegerField(verbose_name="montant L3", default=0)
    montant = models.IntegerField(verbose_name="montant", default=0)
    difference = models.IntegerField(verbose_name="Différence", default=0)
    acomptes = models.IntegerField(verbose_name="Acomptes", default=0)
    montantEnLettre = models.CharField(
        max_length=100, verbose_name="Montant en lettre", default="lettres")
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

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

    Attributes:
        dateDebut (date): Date de début de la période de paie.
        dateFin (date): Date de fin de la période de paie.
        personnel (Personnel): Référence au personnel concerné par la prise en charge.
        frais_de_vie (int): Montant des frais de vie pris en charge.
        frais_nourriture (int): Montant des frais de nourriture pris en charge.
        montant (int): Montant total pris en charge.
        montantEnLettre (str): Montant total en lettres.
        annee_universitaire (AnneeUniversitaire): Année universitaire associée à la prise en charge.
        compte_bancaire (CompteBancaire): Référence au compte bancaire utilisé pour le remboursement.

    Methods:
        save(*args, **kwargs): Enregistre les détails de la prise en charge dans la base de données.
        __str__(): Renvoie une représentation en chaîne de caractères de la prise en charge.

    """
    dateDebut = models.DateField(verbose_name="Date de début", null=True)
    dateFin = models.DateField(verbose_name="Date de fin", null=True)
    personnel = models.ForeignKey(
        'Personnel', on_delete=models.CASCADE, verbose_name="Personnel")
    frais_de_vie = models.IntegerField(verbose_name="Frais de vie", default=0)
    frais_nourriture = models.IntegerField(
        verbose_name="Frais de nourriture", default=0)
    montant = models.IntegerField(verbose_name="Montant", default=0)
    montantEnLettre = models.CharField(
        max_length=100, verbose_name="Montant en lettre", default="lettres")
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)
    compte_bancaire = models.ForeignKey(
        'CompteBancaire', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.personnel.nom) + "  " + str(self.personnel.prenom) + "  " + str(self.dateDebut) + "-" + str(self.dateFin)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()

        total = self.frais_de_vie + self.frais_nourriture
        self.montant = total
        self.montantEnLettre = num2words(total, lang='fr')
        super(Charge, self).save(*args, **kwargs)


class Conge(models.Model):
    """
    Modèle représentant les demandes de congé du personnel.

    Attributes:
        NATURE_CHOICES (list): Liste des choix de nature de congé.
        VALIDATION_CHOICES (list): Liste des choix d'état de validation.

        nature (str): Nature des congés.
        autre_nature (str): Autre nature de congé à préciser (optionnel).
        date_et_heure_debut (date): Date de début du congé.
        date_et_heure_fin (date): Date de fin du congé.
        personnel (Personnel): Référence au personnel demandant le congé.
        motif_refus (str): Motif de refus du congé.
        valider (str): État de validation du congé.
        nombre_de_jours_de_conge (int): Nombre de jours de congé demandés.
        annee_universitaire (AnneeUniversitaire): Année universitaire associée à la demande de congé.

    Methods:
        save(*args, **kwargs): Enregistre les détails de la demande de congé dans la base de données.
        __str__(): Renvoie une représentation en chaîne de caractères de la demande de congé.

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
    autre_nature = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Autre nature à préciser")
    date_et_heure_debut = models.DateField(
        default=timezone.now, verbose_name="Date de début")
    date_et_heure_fin = models.DateField(
        default=timezone.now, verbose_name="Date de fin")
    personnel = models.ForeignKey(
        'Personnel', on_delete=models.CASCADE, verbose_name="Personnel")
    motif_refus = models.TextField(
        null=True, blank=True, verbose_name="Motif de refus")
    valider = models.CharField(
        max_length=30, choices=VALIDATION_CHOICES, verbose_name="État", default="Inconnu")
    nombre_de_jours_de_conge = models.IntegerField(default=0)
    annee_universitaire = models.ForeignKey(
        'AnneeUniversitaire', on_delete=models.CASCADE, verbose_name="Année Universitaire", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.annee_universitaire:
            self.annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
        duree = self.date_et_heure_fin - self.date_et_heure_debut
        self.nombre_de_jours_de_conge = duree.days if duree.days > 0 else 0
        super(Conge, self).save(*args, **kwargs)
        self.personnel.update_conge_counts()

    def __str__(self):
        return str(self.personnel.nom) + "  " +  str(self.personnel.prenom) + "  " + str(self.nombre_de_jours_de_conge) 
