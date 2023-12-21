import json
from django.core.serializers import serialize
import datetime 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from main.models import Enseignant, Matiere, Etudiant ,AnneeUniversitaire , Semestre
from cahier_de_texte.models import Seance
from django.contrib.auth import authenticate, login , get_user_model

import datetime

from collections import defaultdict

def index(request):
    return render(request, 'planning.html')

def save_a_planning():
    
    return

def new_planning(request,semestreId):
    semestreId=semestreId
    annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
    print(semestre)
    planification = defaultdict(list)
    ues = semestre.get_all_ues()

    for ue in ues:
        print(ue)
        matieres_json = serialize('json', ue.matiere_set.all())
        matieres = json.loads(matieres_json)
        for matiere in matieres :
            seances=Seance.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps=0
            for seance in seances:
                temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()/3600
            matiere['temps']=temps
            print(matiere)
                 
        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)

    return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'ues':ues})


def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres
