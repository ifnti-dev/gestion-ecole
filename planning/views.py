
import json
import datetime 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from main.models import Enseignant, Matiere, Etudiant,Seance ,AnneeUniversitaire , Semestre
from django.contrib.auth import authenticate, login , get_user_model

import datetime

from collections import defaultdict

def index(request):
    annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestres = Semestre.objects.filter(courant=True, pk__contains=annee)
    
    # Structure de données pour stocker les informations organisées
    planification = defaultdict(list)

    for semestre in semestres:
        ues = semestre.get_all_ues()

        for ue in ues:
            matieres = list(ue.matiere_set.all())
            planification[semestre].append({'ue': ue, 'matieres': matieres})

    # Vous pouvez désormais transmettre 'planification' au modèle
    return render(request, 'generer_planning.html', {'planification': dict(planification)})


def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres
