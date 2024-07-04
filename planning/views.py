import json
from django.core.serializers import serialize
import datetime 
from django.http import JsonResponse
from django.http import HttpResponse
from main.pdfMaker import generate_pdf
import re
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from main.models import Enseignant, Evaluation, Matiere, Etudiant ,AnneeUniversitaire , Semestre
from cahier_de_texte.models import Seance
from planning.models import Planning , SeancePlannifier
from django.contrib.auth import authenticate, login , get_user_model

import datetime
from datetime import timedelta

from collections import defaultdict

from django.conf import settings
from datetime import datetime




@login_required(login_url=settings.LOGIN_URL)
def index(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','comptable','secretaire']:
            return render(request, 'errors_pages/403.html')
    id_annee=request.session.get("id_annee_selectionnee")
    annee=AnneeUniversitaire.objects.filter(id=id_annee).first()
    semsestre_courant=Semestre.objects.filter(courant=True,annee_universitaire=annee)
    semestres=Semestre.objects.filter(annee_universitaire=annee)
    if request.method=="POST" :
            semestreId =request.POST.get("semestre")
            plannings = Planning.objects.filter(semestre__id=semestreId)
    else :
        plannings = Planning.objects.all()

    dernier_planning = Planning.objects.all().last()

    #condition  nécéssaire pour que nouvelle_semaine ne sorte pas une erreur quand il n'y a aucun planning
    if dernier_planning:
        nouvelle_semaine = dernier_planning.semaine + 1
    else:
        nouvelle_semaine = 1


    context= {
        'semestres':semestres,
        'nouvelle_semaine' : nouvelle_semaine,
        'semestre_courant':semsestre_courant,
        'plannings':plannings}


    return render(request, 'planning_list.html',context)



@login_required(login_url=settings.LOGIN_URL)
def verifier(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestreId = data.get('semestre')
        annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
        plan = Planning.objects.filter(semestre=semestre, semaine=semaine).first()
        if plan is None:
            return JsonResponse({"status": "reussite"})
        return JsonResponse({"datedebut": str(plan.datedebut),"datefin": str(plan.datefin),"semaine": str(plan.semaine),"semestre": str(plan.semestre)})
        
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url=settings.LOGIN_URL)
def nouveau_planning(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    
    if request.method == 'POST':
        semestreId = request.POST.get("semestre")
        semaine = request.POST.get("semaine")

        intervalle = request.POST.get("intervalle")
        dates = intervalle.split('to')
        datedebut = dates[0].strip()
        datefin = dates[1].strip()
        intervalle = datedebut[-2:] + '/' + datedebut[5:7] + ' au ' + datefin[-2:] + '/' + datefin[5:7] + '/' + datefin[:4]

        annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestre = Semestre.objects.filter(courant=True, pk__contains=annee, id=semestreId).first()
        planification_json = ""  # Initialize the variable

        if semestre:
            planification = defaultdict(list)
            ues = semestre.get_all_ues()
            
            for ue in ues:
                matieres_json = serialize('json', ue.matiere_set.all())
                matieres = json.loads(matieres_json)
                
                for matiere in matieres:
                    seances = Seance.objects.filter(semestre=semestre, matiere=matiere['pk'])
                    temps = sum((seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds() for seance in seances)
                    hours, remainder = divmod(temps, 3600)
                    minutes, _ = divmod(remainder, 60)
                    matiere['temps_effectuer'] = f"{int(hours)}h {int(minutes)}min"

                    planning = Planning.objects.filter(semestre=semestre)
                    for plan in planning:
                        plannings = SeancePlannifier.objects.filter(planning=plan, matiere=matiere['pk'])
                        temps_x = sum((planning.date_heure_fin - planning.date_heure_debut).total_seconds() for planning in plannings)
                        hours_x, remainder = divmod(temps_x, 3600)
                        minutes_x, _ = divmod(remainder, 60)
                        matiere['temps_plannifier'] = f"{int(hours_x)}h {int(minutes_x)}min"

                planification[str(ue)].append({'matieres': matieres})

            planification_json = json.dumps(planification)
        

        return render(request, 'generer_planning.html', {
            'planification_json': planification_json,
            'semestre': semestre,
            'semaine': semaine,
            'datedebut': datedebut,
            'datefin': datefin,
            'intervalle': intervalle,
            'ues': ues if semestre else []
        })

    return render(request, 'some_default_template.html')  # Render a default template if not POST

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError("Type not serializable")

import datetime
@login_required(login_url=settings.LOGIN_URL)
def details(request,planningId):
    planning = Planning.objects.filter(id=planningId).first()
    seances=SeancePlannifier.objects.filter(planning=planning)
    print(seances )
    event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut , 'end':seance.date_heure_fin ,'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
    event_data = json.dumps(event_data, default=datetime_serializer)
            
    return render(request, 'planning.html', {'event_data': event_data,'planning':planning})

@login_required(login_url=settings.LOGIN_URL)
def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres

@login_required(login_url=settings.LOGIN_URL)
def sauvegarder(request):
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestre = data.get('semestre')
        datedebut = data.get('datedebut')
        datefin = data.get('datefin')

        intervalle = data.get('intervalle')

        events = data.get('events')
        semestre=Semestre.objects.filter(id=semestre).first()

        print( semaine)
        print(events)
        planning = Planning(
                semaine=semaine,
                semestre=semestre,
                datedebut=datedebut,

                datefin=datefin,
                intervalle=intervalle

        )
        planning.save()
        for event in events:
            title = event.get('title')
            #cleaned_title = re.sub(r'\s*\([^)]*\)$', '', title)
            #print(cleaned_title)
            print(title)
            matiere = Matiere.objects.filter(libelle=title).first()
            professeur = matiere.enseignant  # Remplacez cela par le champ approprié
            
            seance = SeancePlannifier(
                intitule=title,
                matiere=matiere,
                date_heure_debut=event.get('start'),
                date_heure_fin=event.get('end'),
                professeur=professeur,
                planning=planning,
                precision='aucune'
            )

            # Sauvegardez l'objet Planning en base de données
            seance.save()
        
        return JsonResponse({'status':"reussite"})

from django.db.models import Count
@login_required(login_url=settings.LOGIN_URL)    
def resume(request,semestreId):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    semestre=Semestre.objects.filter(id=semestreId).first()
    liste_absence={}
    etudiants=semestre.etudiant_set.all()
    planning=Planning.objects.filter(semestre=semestre)
    plannings=set()
    for plan in planning:
        plannings.add(SeancePlannifier.objects.filter(planning=plan))
    valeur_min = 0
    seances = Seance.objects.filter(semestre=semestre).annotate(num_eleves=Count('eleves_presents')).filter(num_eleves__gt=valeur_min)
    print(seances.count())

    for seance in seances:
        for eleve in seance.eleves_presents.all():
            eleve_key = eleve.nom + ' ' + eleve.prenom
            absence_details = "Matiere : " + seance.matiere.libelle + ", Date et Heure : " + str(seance.date_et_heure_debut.date()) + " " + str(seance.date_et_heure_debut.time()) + " à " + str(seance.date_et_heure_fin.time())

            if eleve_key in liste_absence:
                liste_absence[eleve_key].append(absence_details)
            else:
                liste_absence[eleve_key] = [absence_details]






    activite_prof={}
    enseignants=Enseignant.objects.all()
    for prof in enseignants :
        seances_prof = Seance.objects.filter(semestre=semestre,enseignant=prof)
        if seances_prof.exists():
            temps = 0
            activity = {}
            
            for seance_p in seances_prof:
                temps += (seance_p.date_et_heure_fin - seance_p.date_et_heure_debut).total_seconds()
                activity[seance_p.matiere]= 'Date et Heure : ' + str(seance_p.date_et_heure_debut) + ' à ' + str(seance_p.date_et_heure_fin)
            
            hours_x, remainder = divmod(temps, 3600)
            minutes_x, _ = divmod(remainder, 60)
            hours_x=int(hours_x)
            minutes_x=int(minutes_x)
            prof_key = prof.prenom + ' ' + prof.nom
            
            # Utilisez setdefault pour créer une entrée pour le professeur s'il n'existe pas
            activite_prof.setdefault(prof_key, {})
            
            activite_prof[prof_key]['activité'] = str(hours_x) + 'h' + str(minutes_x) + 'min'
            activite_prof[prof_key]['seances'] = activity

    activite_matiere={}
    ues = semestre.get_all_ues()
    
    for ue in ues:
        matieres = ue.matiere_set.all()
        for matiere in matieres :
            seances=Seance.objects.filter(semestre=semestre,matiere=matiere)
            temps=0
            nmbre_planifier=0
            nombre_effectuer=0
            for seance in seances:
                temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()
            hours, remainder = divmod(temps, 3600)
            minutes, _ = divmod(remainder, 60)
            hours=int(hours)
            minutes=int(minutes)

            planning=Planning.objects.filter(semestre=semestre)
            for plan in planning :
                plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere)
                nmbre_planifier+=plannings.count()
                temps_x=0
                for planning in plannings:
                    temps_x+=(planning.date_heure_fin - planning.date_heure_debut).total_seconds()
                    if planning.valider:
                        nombre_effectuer+=1
                hours_x, remainder = divmod(temps_x, 3600)
                minutes_x, _ = divmod(remainder, 60)
                hours_x=int(hours_x)
                minutes_x=int(minutes_x)
            mat_key = str(ue)+str(matiere)
            if mat_key not in activite_matiere:
                activite_matiere[mat_key] = {'professeur':'','libelle':'','temps_prevu':'','temps_effectuer': '','ue':'', 'temps_plannifier': ''}

            activite_matiere[mat_key]['temps_effectuer'] = str(hours) + 'h' + str(minutes) + 'min'
            activite_matiere[mat_key]['temps_plannifier'] = str(hours_x) + 'h' + str(minutes_x) + 'min'  
            activite_matiere[mat_key]['temps_prevu'] = str(int(matiere.heures)) + 'h' 
            activite_matiere[mat_key]['libelle'] = str(matiere)                  
            activite_matiere[mat_key]['ue'] = str(ue)  
            activite_matiere[mat_key]['professeur'] = matiere.enseignant.nom + ' ' + matiere.enseignant.prenom
            activite_matiere[mat_key]['nmbre_planifier'] = nmbre_planifier
            activite_matiere[mat_key]['nombre_effectuer'] = nombre_effectuer
            activite_matiere[mat_key]['nombre_enregistrer'] = seances.count()
            activite_matiere[mat_key]['nombre_enregistrer_valider'] = seances.filter(valider=True).count()
            activite_matiere[mat_key]['nombre_evaluations'] = Evaluation.objects.filter(semestre=semestre,matiere=matiere).count()
            activite_matiere[mat_key]['rattrapage'] =Evaluation.objects.filter(semestre=semestre,matiere=matiere,rattrapage=True).count()


            

    print(json.dumps(liste_absence))
    context={'liste_absences':liste_absence,'liste_absences_json':json.dumps(liste_absence),'semestre':semestre,'etudiants':etudiants,'activite_prof':activite_prof,'activite_matiere':activite_matiere,'ues':ues}
    #recuperer les date et heure des seance plannifier mais non enregistrer (facultatif)
     
    return render(request,'semestre_recap.html',context)
        
@login_required(login_url=settings.LOGIN_URL)
def modifier(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        data = json.loads(request.body.decode('utf-8'))
        events = data.get('events')
        plan = data.get('planningId')
        planning=Planning.objects.filter(id=plan).first()
        
        for event in events:
            title = event.get('title')
            matiere = Matiere.objects.filter(libelle=title).first()
            professeur = matiere.enseignant  # Remplacez cela par le champ approprié
            old_seance=SeancePlannifier.objects.filter(
                intitule=title,
                matiere=matiere,
                date_heure_debut=event.get('start'),
                date_heure_fin=event.get('end'),
                professeur=professeur,
                planning=planning,
                precision='aucune').first()
            if old_seance :
                next
            else :
                seance = SeancePlannifier(
                    intitule=title,
                    matiere=matiere,
                    date_heure_debut=event.get('start'),
                    date_heure_fin=event.get('end'),
                    professeur=professeur,
                    planning=planning,
                    precision='aucune'
                )
                seance.save()
            # Sauvegardez l'objet Planning en base de données
            
        
        return JsonResponse({'status':"reussite"})

    


@login_required(login_url=settings.LOGIN_URL)
def ajouter_cours(request,planningId):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    planningg = Planning.objects.filter(id=planningId).first()
    seances=SeancePlannifier.objects.filter(planning=planningg)
    event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut , 'end':seance.date_heure_fin ,'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
    event_data = json.dumps(event_data, default=datetime_serializer)
    semestre = planningg.semestre
    print(semestre)
    planification = defaultdict(list)
    ues = semestre.get_all_ues()

    for ue in ues:
        matieres_json = serialize('json', ue.matiere_set.all())
        matieres = json.loads(matieres_json)
        for matiere in matieres :
            seances=Seance.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps=0
            for seance in seances:
                temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()/3600
            matiere['temps_effectuer']=temps
            
            planning=Planning.objects.filter(semestre=semestre)
            for plan in planning :
                plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere['pk'])
                temps_x=0
                for planning in plannings:
                    temps_x+=(planning.date_heure_fin - planning.date_heure_debut).total_seconds()/3600
                matiere['temps_plannifier']=temps_x                         

        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)
    
    return render(request, 'update_planning.html', {'planification_json': planification_json,'event_data': event_data,'planning':planningg,'ues':ues})


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_seance(request):
    print("yesssssssssss")
    intitule = request.POST.get("intitulé")
    description = request.POST.get("description")
    eleves_absents = request.POST.getlist("eleves-absent")
    etudiant_id = request.POST.get('ecrit_par')
    seanceId = request.POST.get('seanceId')
    user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
    auteur_obj=get_object_or_404(Etudiant,user=user_connecte)
    seance_plan=SeancePlannifier.objects.filter(id=seanceId).first()
    if len(intitule)<=0:
        intitule=seance_plan.intitule
    seance = Seance(
        intitule=intitule,
        semestre=seance_plan.planning.semestre,
        description=description,
        enseignant=seance_plan.professeur,
        date_et_heure_debut=seance_plan.date_heure_debut,
        date_et_heure_fin=seance_plan.date_heure_fin,
        matiere=seance_plan.matiere,
        auteur=auteur_obj
    )
    seance_plan.valider=True
    seance_plan.save()
    seance.save()

    for etudiant_id in eleves_absents:
        etudiant_obj = get_object_or_404(Etudiant, id=etudiant_id)
        seance.eleves_presents.add(etudiant_obj)

    
    return redirect("/cahier_de_texte/info_seance/" + str(seance.id) + "/" )

@login_required(login_url=settings.LOGIN_URL)
def seance(request,seanceId):
    seance=SeancePlannifier.objects.filter(id=seanceId).first()
    seance_exe=seance.seance_set.all()
    if request.user.groups.all().first().name in ['etudiant']:
        etudiants=seance.planning.semestre.etudiant_set.exclude(user=request.user)
        context={'seance':seance,'etudiants':etudiants,'cdt':seance_exe}
    else :
        etudiants=seance.planning.semestre.etudiant_set.all()
        context={'seance':seance,'etudiants':etudiants,'cdt':seance_exe}

    return render(request,'details.html',context)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def french_day(day):
    days = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'
    }
    return days.get(day.capitalize(), day)


@login_required(login_url=settings.LOGIN_URL)
def imprimer(request, planningId):
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')
    
    planns = Planning.objects.filter(id=planningId).first()
    days = []
    timeslots = ['']
    tenues = ['Veste', 'Tricot', 'Veste', 'Tricot', 'Bigarré', 'Bigarré']
    
    semestre_libelle = planns.semestre.libelle
    annee_universitaire = planns.semestre.annee_universitaire

    if semestre_libelle in ['S1', 'S2']:
        niveau = f'L1 {semestre_libelle} {annee_universitaire}'
    elif semestre_libelle in ['S3', 'S4']:
        niveau = f'L2 {semestre_libelle} {annee_universitaire}'
    elif semestre_libelle in ['S5', 'S6']:
        niveau = f'L3 {semestre_libelle} {annee_universitaire}'
    else:
        niveau = f'Unknown {semestre_libelle} {annee_universitaire}'


    plannings = SeancePlannifier.objects.filter(planning=planns)    
    for planning in plannings:
        jour_n = (planns.semaine - 1) * 5 + planning.date_heure_debut.weekday() + 1
        jour_n = str(jour_n)
        valeur_jour = str(planning.date_heure_debut.day).zfill(2)
        valeur_mois = str(planning.date_heure_debut.month).zfill(2)

        jour = french_day(planning.date_heure_debut.strftime("%A"))

        day = f'{jour} {valeur_jour}/{valeur_mois} - J{jour_n}'
        timeshot = f'{planning.date_heure_debut.hour}h{str(planning.date_heure_debut.minute).zfill(2)}'
        # print(timeshot)

        planning.day = day
        planning.timeshot = timeshot
        planning.save()
        if day not in days:
            days.append(day)
        if timeshot not in timeslots:
            timeslots.append(timeshot)
        

    #heures de la jours
    ues_prof_matieres = {time: {} for time in timeslots}
    # print(ues_prof_matieres)

    for plan in plannings:
        time_slot = plan.timeshot  
        day = plan.day  
        activity = plan.intitule
        professor = plan.professeur.personnel.nom if plan.professeur else "No Professor"

        if time_slot not in ues_prof_matieres:
            ues_prof_matieres[time_slot] = {}
        
        if day not in ues_prof_matieres[time_slot]:
            ues_prof_matieres[time_slot][day] = {}

        if activity not in ues_prof_matieres[time_slot][day]:
            ues_prof_matieres[time_slot][day][activity] = []

        ues_prof_matieres[time_slot][day][activity].append({
            "professeur": professor
        })
    
    heure_statique = {
        'c1' : '7h:00',
	    "c2" : "8h:30",
        "c3" : "8h:45",
        "c4" : "10h:15",
        "c5" : "10h:30",
        "c6" : "12h:00",
        "c7" : "14h:00",
        "c8" : "15h:30",
        "c9" : "15h:45",
        "c10" : "17h:15",
    }

    tableau_final = []
    values_plannings = ues_prof_matieres.values()
    for elt in values_plannings:
        # On crée une liste temporaire pour stocker les valeurs de chaque élément
        temp_list = []
        for day, schedule in elt.items():
            if schedule:  # Vérifie si le jour est programmé
                temp_list.append(schedule)
            else:
                etude = "etudes"
                temp_list.append(etude)
        tableau_final.append(temp_list)

    ligne1 = [(list(e.keys()), list(e.values())) for e in tableau_final[1]]
    ligne2 = [(list(e.keys()), list(e.values())) for e in tableau_final[2]]
    ligne3 = [(list(e.keys()), list(e.values())) for e in tableau_final[3]]
    ligne4 = [(list(e.keys()), list(e.values())) for e in tableau_final[4]]
    ligne5 = [(list(e.keys()), list(e.values())) for e in tableau_final[5]]



    print(ligne1)

    context = {
        'planning': ues_prof_matieres, 
        'niveau': niveau, 
        'days': days, 
        'taille': 22.5 / len(days), 
        'tenues': tenues,
        'heure_statique' : heure_statique,
        'ligne1' : ligne1,
        'ligne2' : ligne2,
        'ligne3' : ligne3,
        'ligne4' : ligne4,
        'ligne5' : ligne5,
    } 
         

    latex_input = 'planning_week'
    latex_output = f'planning_week_{planns.semaine}_{semestre_libelle}_{annee_universitaire}'
    pdf_file = f'planning_week_{planns.semaine}_{semestre_libelle}_{annee_universitaire}'

    # génération du pdf
    generate_pdf(context, latex_input, latex_output, pdf_file)

    with open(f'media/pdf/{pdf_file}.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = f'inline;filename={pdf_file}.pdf'
        return response

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url=settings.LOGIN_URL)
def effacer(request,planningId):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    planning=Planning.objects.filter(id=planningId).first()
    seance = SeancePlannifier.objects.filter(planning=planning)
    for se in seance :
        se.delete()
    planning.delete()
    return redirect('planning:planning')



@login_required(login_url=settings.LOGIN_URL)
def retirer_seance(request, seance_id):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    seance=SeancePlannifier.objects.filter(id=seance_id)
    seance.delete()
    return redirect('planning:planning')


@login_required(login_url=settings.LOGIN_URL)
def valider_seance(request, seance_id):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    seance=SeancePlannifier.objects.filter(id=seance_id).get()
    seance.valider=True
    seance.save()
    return redirect('planning:details',seance.id)

@login_required(login_url=settings.LOGIN_URL)
def invalider_seance(request, seance_id):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
    seance=SeancePlannifier.objects.filter(id=seance_id).get()
    seance.valider=False
    seance.save()
    return redirect('planning:details',seance.id)

