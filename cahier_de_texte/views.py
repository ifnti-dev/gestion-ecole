
import json
import datetime 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from main.models import Enseignant, Matiere, Etudiant,Seance ,AnneeUniversitaire , Semestre
from django.contrib.auth import authenticate, login , get_user_model

import datetime

def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres



def getNiveauEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    print(etudiant.nom)
    print('semestre',semestre)
    if semestre:
        if semestre[0].libelle =="S1" or semestre[0].libelle =="S2":
            return "L1"
        if semestre[0].libelle =="S3" or semestre[0].libelle =="S4":
            return "L2"
        elif semestre[0].libelle =="S5" or semestre[0].libelle =="S6":
            return "L3"
    else :
        return "RR"
            

@login_required(login_url="/main/connexion")
def enregistrer_seance(request):
    if request.method == "POST":
        intitule = request.POST.get("intitulé")
        description = request.POST.get("description")
        date=request.POST.get("dateseance")
        heure_debut = request.POST.get("heuredebut")
        heure_fin = request.POST.get("heurefin")
        date_et_heure_debut = date + ' '+heure_debut
        date_et_heure_fin = date + ' '+heure_fin
        eleves_absents = request.POST.getlist("eleves-absent")
        matiere_id = request.POST.get("matiere")
        etudiant_id = request.POST['ecrit_par']
        matiere_obj=get_object_or_404(Matiere, pk=matiere_id)
        user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
        auteur_obj=get_object_or_404(Etudiant,user=user_connecte)
        annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestreEtudiant=auteur_obj.semestres.filter(courant=True,pk__contains=annee).first()

        seance = Seance(
            intitule=intitule,
            semestre=semestreEtudiant,
            description=description,
            enseignant=matiere_obj.enseignant,
            date_et_heure_debut=date_et_heure_debut,
            date_et_heure_fin=date_et_heure_fin,
            matiere=matiere_obj,
            auteur=auteur_obj
        )
        seance.save()
        for etudiant_id in eleves_absents:
            etudiant_obj = get_object_or_404(Etudiant, id=etudiant_id)
            seance.eleves_presents.add(etudiant_obj)

        
        return redirect("/cahier_de_texte/info_seance/" + str(seance.id) + "/" ) 

    elif request.user.is_authenticated:
        if request.user.groups.all().first().name not in ['etudiant']:
            return render(request, 'errors_pages/403.html')
        user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
        etudiant=get_object_or_404(Etudiant,user=user_connecte)
        print("ffff ",AnneeUniversitaire.static_get_current_annee_universitaire())
        annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
            
        try :
            semestre=etudiant.semestres.filter(courant=True,pk__contains=annee).get()
            etudiants=semestre.etudiant_set.all().exclude(id=etudiant.id)        
            matieres = getMatieresEtudiant(etudiant)
        except :
            return render(request, 'errors_pages/403.html')
    
        dateActuelle=datetime.datetime.now().strftime("%Y-%m-%d")
        heureActuelle=datetime.datetime.now().strftime("%H:%M")
        return render(request, "cahier_de_text/enregistrer_seance.html", {"etudiants": etudiants, "matieres": matieres,"etudiant":etudiant,"currentDate":dateActuelle,"currentTime":heureActuelle})

    else :
        return redirect('/admin/')

@login_required(login_url="/main/connexion")
def modifier_seance(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
    etudiant=get_object_or_404(Etudiant,user=user_connecte)
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee).get()
    etudiants=semestre.etudiant_set.all().exclude(id=etudiant.id)
    matieres = getMatieresEtudiant(etudiant)        

    if request.method == "POST":
        date=request.POST.get("dateseance")
        heure_debut = request.POST.get("heuredebut")
        heure_fin = request.POST.get("heurefin")
        seance.intitule = request.POST.get("intitule")
        seance.description = request.POST.get("description")
        seance.date_et_heure_debut = date + ' '+heure_debut
        seance.date_et_heure_fin = date + ' '+heure_fin
        eleves_absents = request.POST.getlist("eleves-absent")
        seance.matiere = get_object_or_404(Matiere, id=request.POST.get("matiere"))
        seance.enseignant = seance.matiere.enseignant
        seance.valider=False

        seance.eleves_presents.clear()
        for etudiant_id in eleves_absents:
            etudiant = get_object_or_404(Etudiant, id=etudiant_id)
            seance.eleves_presents.add(etudiant)
            
        seance.save()

        return redirect("/cahier_de_texte/info_seance/" + str(seance.id) + "/" ) 

    return render(request, "cahier_de_text/modifier_seance.html", {"seance": seance, "etudiants": etudiants, "matieres": matieres})

@login_required(login_url="/main/connexion")
def supprimer_seance(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    seance.delete()
    return redirect('/cahier_de_texte/')

def changer_secretaire(request):
    etudiant_id = request.POST.get('secretaire')
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)  
    semestres= etudiant.semestres.all()
    for semestre in semestres:
        etudiants = Etudiant.objects.filter(semestre=semestre) 
    print('ici' ,etudiants)
    secretaire_actuels = etudiants.filter(secretaire=True)
   
    for secretaire_actuel in secretaire_actuels:
        secretaire_actuel.secretaire = False
        secretaire_actuel.save()
    
    etudiant.secretaire = True
    etudiant.save()
            
    return redirect('/cahier_de_texte/gestion_classe')

def changer_delegue(request):
    etudiant_id = request.POST.get('delegue')
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)  
    semestre = etudiant.get_semestre_courant()
    if semestre:
        semestre = semestre.get()
        etudiants= semestre.etudiant_set.all()
        delegue_actuel = etudiants.filter(delegue=True)
        if delegue_actuel :
            delegue_actuel = delegue_actuel.get()
            delegue_actuel.delegue = False
            delegue_actuel.save()
        etudiant.delegue = True
        etudiant.save()

    return redirect('cahier_de_texte:gestion_classe')

@login_required(login_url="/main/connexion")
def gestion_classe(request):
    students = Etudiant.objects.all()
    print(students)
    license1_students = set()
    license2_students = set()
    license3_students = set()
    for etudiant in students:
        if getNiveauEtudiant(etudiant) == "L3":
            license3_students.add(etudiant)
        elif getNiveauEtudiant(etudiant) == "L2":
            license2_students.add(etudiant)
        elif getNiveauEtudiant(etudiant) == "L1":
            license1_students.add(etudiant)

    context = {
        'license1_students': license1_students,
        'license2_students': license2_students,
        'license3_students': license3_students,
    }

    return render(request, "cahier_de_text/controle_classe.html", context)

@login_required(login_url="/main/connexion")
def info_seance(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    date_fin = datetime.datetime.fromisoformat((str)(seance.date_et_heure_fin))
    date_debut = datetime.datetime.fromisoformat((str)(seance.date_et_heure_debut))
    new_debut =(str)(date_debut.strftime("%d %B %Y, %H:%M")) 
    new_fin = (str)(date_fin.strftime("%d %B %Y, %H:%M"))
    print((str)(new_debut))
    return render(request, "cahier_de_text/details_seance.html", {"seance": seance,"date_debut":new_debut,"date_fin":new_fin})

@login_required(login_url="/main/connexion")
def valider_seance(request,seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    seance.valider=True
    seance.commentaire=""
    seance.save()
    return redirect("/cahier_de_texte/liste_seance/") 


def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError("Type not serializable")

@login_required(login_url="/main/connexion")
def cahier_de_text(request):
    if request.user.is_authenticated:
        if  request.user.groups.all()[0].name == "etudiant":
            user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
            etudiant=get_object_or_404(Etudiant,user=user_connecte)
            seances=Seance.objects.all()
            events = set()
            niveau=getNiveauEtudiant(etudiant)
            for seance in seances:
                if niveau== getNiveauEtudiant(seance.auteur):
                    print("seance :", seance)
                    events.add(seance)
            print("seances :",events )
            event_data = [{'title': event.intitule, 'start': event.date_et_heure_debut , 'end':event.date_et_heure_fin ,'url': '/cahier_de_texte/info_seance/' + str(event.id) + '/'} for event in events]
            event_data = json.dumps(event_data, default=datetime_serializer)
            return render(request,"cahier_de_text/cahier_de_texte.html",{"event_data":event_data,"niveau":niveau})

        else:
            events = set()
            seances=Seance.objects.all()
            semestres=Semestre.objects.all()
            niveau=''
            if request.method=="POST" and request.POST.get("niveau")=="L1" :
                niveau= "L1" 
                for seance in seances:
                    if "L1"== getNiveauEtudiant(seance.auteur):
                        events.add(seance)

            elif request.method=="POST" and request.POST.get("niveau")=="L2" : 
                niveau= "L2"
                for seance in seances:
                    if "L2"== getNiveauEtudiant(seance.auteur):
                        events.add(seance)
            elif request.method=="POST" and request.POST.get("niveau")=="L3" :
                niveau= "L3" 
                for seance in seances:
                    if "L3"== getNiveauEtudiant(seance.auteur):
                        events.add(seance)
            else :
                niveau="L1"
                for seance in seances:
                    if "L1"== getNiveauEtudiant(seance.auteur):
                        events.add(seance)

            event_data = [{'title': event.intitule, 'start': event.date_et_heure_debut , 'end':event.date_et_heure_fin ,'url': '/cahier_de_texte/info_seance/' + str(event.id) + '/'} for event in events]
            event_data = json.dumps(event_data, default=datetime_serializer)
            return render(request,"cahier_de_text/cahier_de_texte.html",{"event_data":event_data,"niveau":niveau,"semestres":semestres})

@login_required(login_url="/main/connexion")
def liste_seance(request):
    if request.user.is_authenticated:
        if request.user.groups.all().first().name not in ['enseignant']:
            return render(request, 'errors_pages/403.html')
        user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
        enseignant_connecte = get_object_or_404(Enseignant, user=user_connecte)
        matieres = Matiere.objects.filter(enseignant=enseignant_connecte)
        seances_en_attente = Seance.objects.filter(matiere__in=matieres, valider=False)
        seances_validees = Seance.objects.filter(matiere__in=matieres, valider=True)
        return render(request, "cahier_de_text/liste_seance.html", {"seances_en_attente": seances_en_attente, "seances_validees": seances_validees})

@login_required(login_url="/main/connexion")
def liste_seance_etudiant(request):
    if request.user.is_authenticated:
        if request.user.groups.all().first().name not in ['etudiant']:
            return render(request, 'errors_pages/403.html')
        user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
        etudiant_connecte = get_object_or_404(Etudiant, user=user_connecte)
        seances_en_attente = Seance.objects.filter(auteur=etudiant_connecte, valider=False)
        seances_validees = Seance.objects.filter(auteur=etudiant_connecte,valider=True)
        return render(request, "cahier_de_text/liste_seance_etudiant.html", {"seances_en_attente": seances_en_attente, "seances_validees": seances_validees})



def lancer_impression():
    return

@login_required(login_url="/main/connexion")
def imprimer(request):
    semestres = request.POST.getlist("semestres")
    nonvalider = request.POST.get("imprimer_non_validees")
    commentaires = request.POST.get("imprimer_commentaires")
    listeAbsence = request.POST.get("eleves_absents")
    listeUe = request.POST.get("details_ue")
    listeMatiere = request.POST.get("details_matieres")
    HeureConsomme = request.POST.get("details_heures_matieres")
    listeEtudiant = request.POST.get("details_etudiants")
    sous_categorisation = request.POST.get("sous_categorisation")
    for semestre_id in semestres:
        semestre =Semestre.objects.get(id=semestre_id)
        programmes=semestre[0].programme_set.all() 
        seances = set()
        ues=set()
        matieres=set()
        if nonvalider :
            try :
                seances.add(Seance.objects.filter(semestre=semestre))
            except :
                pass
        else :
            try :
                seances.add(seances = Seance.objects.filter(semestre=semestre,valider=True))
            except :
                pass
        if listeUe and listeMatiere:                       
            for programme in programmes:
                ues.update([programme.ue])
            
            for ue in ues :
                matieres.update(ue.matiere_set.all())         
            return matieres
        
        elif listeMatiere and not listeUe:
            programmes=semestre[0].programme_set.all()            
            for programme in programmes:
                ues.update([programme.ue])
            
            for ue in ues :
                matieres.update(ue.matiere_set.all())         
            return matieres
        
        elif listeUe and not listeMatiere:
            programmes=semestre[0].programme_set.all()            
            for programme in programmes:
                ues.update([programme.ue])
        
        else :
            pass

        print(seances)
                    
    
    return HttpResponse("traitement en cours ")






@login_required(login_url="/main/connexion")
def commenter(request):
    commentaire = request.POST.get("commentaire")
    idv=request.POST.get("seance_id")
    seance = get_object_or_404(Seance, id=idv)
    seance.commentaire=commentaire
    seance.save()
    return redirect("/cahier_de_texte/info_seance/" + str(seance.id) + "/" )