
import json
import datetime
import random 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from faker import Faker
from main.pdfMaker import generate_pdf
from main.models import Enseignant, Matiere, Etudiant ,AnneeUniversitaire, Personnel , Semestre
from cahier_de_texte.models import Seance
from django.contrib.auth import authenticate, login , get_user_model

import datetime

from planning.models import SeancePlannifier

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
    return render(request, "cahier_de_text/details.html", {"seance": seance,"date_debut":new_debut,"date_fin":new_fin})

@login_required(login_url="/main/connexion")
def valider_seance(request,seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    seance.valider=True
    seance.commentaire=""
    seance.save()
    return redirect("/cahier_de_texte/liste_seance/") 

@login_required(login_url="/main/connexion")
def signature_prof(request):
    seance_id=request.POST.get("seance_id")
    username = request.POST.get("teacherName")
    password = request.POST.get("password")
    seance = get_object_or_404(Seance, id=seance_id)
    user = authenticate(request, username=username, password=password)
    notification = {
                "message": "verifier vos identifiant et reessayer", "type": "erreur"}
    context = {"seance": seance, "notification": notification }
    print(username,user)
    if user :           
        if seance.enseignant.user == user:
            print("c'est signer")
            seance.valider=True
            seance.commentaire=""
            seance.save()
            notification
            notification = {
                "message": "seance signer et valider avec succes", "type": "succes"}
            context = {"seance": seance, "notification": notification }
            return render(request, "cahier_de_text/details.html",context)
    else:  
        return render(request, "cahier_de_text/details.html", context)

def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError("Type not serializable")

@login_required(login_url="/main/connexion")
def cahier_de_text(request):
    id_annee=request.session.get("id_annee_selectionnee")
    annee=AnneeUniversitaire.objects.filter(id=id_annee).first()
    if  request.user.groups.all()[0].name == "etudiant":
        user_connecte=get_object_or_404(get_user_model(),id=request.user.id)
        etudiant=get_object_or_404(Etudiant,user=user_connecte)
        sem=etudiant.get_semestre_courant
        niveau=getNiveauEtudiant(etudiant)
        events=Seance.objects.filter(semestre=sem)
        events = set()
        print("seances :",events )
        event_data = [{'title': event.intitule, 'start': event.date_et_heure_debut , 'end':event.date_et_heure_fin ,'url': '/cahier_de_texte/info_seance/' + str(event.id) + '/'} for event in events]
        event_data = json.dumps(event_data, default=datetime_serializer)
        return render(request,"cahier_de_text/cahier_de_texte.html",{"event_data":event_data,"niveau":niveau})

    else:
        semestres=Semestre.objects.all()
        if request.method=="POST" :
            niveau =request.POST.get("niveau")
            if niveau == "L1" :
                niveau="L1"
                s1='S1-'+str(annee.annee)
                s2='S2-'+str(annee.annee)
                events=Seance.objects.filter(semestre__in= [s1,s2])
                print('nombre seances' , len(events))

            elif niveau=="L2" : 
                niveau="L2"
                s3='S3-'+str(annee.annee)
                s4='S4-'+str(annee.annee)
                events=Seance.objects.filter(semestre__in= [s3,s4])
                print('nombre seances' , len(events))
            elif niveau=="L3" :
                niveau= "L3"
                s5='S5-'+str(annee.annee)
                s6='S6-'+str(annee.annee)
                events=Seance.objects.filter(semestre__in= [s5,s6])
                print('nombre seances' , len(events))
        else :
            niveau="L1"
            s1='S1-'+str(annee.annee)
            s2='S2-'+str(annee.annee)
            events=Seance.objects.filter(semestre__in= [s1,s2])
            print('nombre seances' , len(events))

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

def nuance(valeur):
    if valeur is None :
        return False
    elif valeur == 'on' :
        return True
    


@login_required(login_url="/main/connexion")
def imprimer(request):
    semestres = request.POST.getlist("semestres")
    print('semestres :',semestres)
    valider = request.POST.get("imprimer_validees")
    print('Recuperer uniquement les seances valider ? :',nuance(valider))
    commentaires = request.POST.get("imprimer_commentaires")
    print('Recuperer les commentaires des professeurs  ? :',nuance(commentaires))
    listeAbsence = request.POST.get("eleves_absents")
    print('Afficher la liste des absents par seances  ? :',nuance(listeAbsence))
    listeUe = request.POST.get("details_ue")
    print('Afficher la liste des Ues du semestres   ? :',nuance(listeUe))
    listeMatiere = request.POST.get("details_matieres")
    print('Afficher la liste des Matieres du semestres   ? :',nuance(listeMatiere))
    HeureConsomme = request.POST.get("details_heures_matieres")
    print('Afficher le nombre d"heure consommer par matiere pendant le semestre   ? :',nuance(HeureConsomme))
    listeEtudiant = request.POST.get("details_etudiants")
    print('Afficher la liste des etudiants du semestre   ? :',nuance(listeEtudiant))
    sousCategorisation = request.POST.get("sous_categorisation")
    print('Afficher la liste des seances regrouper par matiere  ? :',sousCategorisation)
    pdf_paths = []
    #si on veut un affichage par matiere , ca met automatiquement la liste des matieres a true 
    for semestre_id in semestres:
        semestre = Semestre.objects.get(id=semestre_id)
        if nuance(valider) :
            seances_total = Seance.objects.filter(semestre=semestre,valider=nuance(valider)).order_by('date_et_heure_debut')
        else :
            seances_total = Seance.objects.filter(semestre=semestre).order_by('date_et_heure_debut')    
        ues = semestre.get_all_ues()
        matieres_dict = {}
        matieres=[]
        etudiants=semestre.etudiant_set.all()
        for ue in ues :                   
            matieres += ue.matiere_set.all()
        print(matieres)
        if sousCategorisation != 'parMatieres' :
            print(nuance(commentaires))
            context={'etudiants':etudiants,
                     'semestre':semestre_id,
                     'listeAbsence':listeAbsence,
                     'ues':ues,
                     'commentaires':commentaires,
                     'listeUe':listeUe,
                     'listeEtudiant':listeEtudiant,
                     'listeMatiere':listeMatiere,
                     'seances':seances_total,
                     'matieres':matieres,
                     'sousCategorisation':sousCategorisation
                     }
                                       
            latex_input = 'cahier_de_texte'
            latex_ouput = 'CDT_'+str(semestre_id)+'_'+str(datetime.datetime.now())
            pdf_file = 'CDT_'+str(semestre_id)+'_'+str(datetime.datetime.now())

            # génération du pdf
            generate_pdf(context, latex_input, latex_ouput, pdf_file)
            pdf_paths.append('media/pdf/' + pdf_file)
            
        else :                       
            if nuance(HeureConsomme) :
                for matiere in matieres :
                    seances_prime = seances_total.filter(matiere=matiere).order_by('date_et_heure_debut')
                    temps=0
                    for seance in seances_prime:
                        temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()
                    hours, remainder = divmod(temps, 3600)
                    minutes, _ = divmod(remainder, 60)

                    matiere_key = matiere.libelle
                    if matiere_key not in matieres_dict:
                        matieres_dict[matiere_key] = {"HeureConsomme": 0, "seances": []}

                    matieres_dict[matiere_key]["HeureConsomme"] = str(hours)+'h '+str(minutes)+'min'
                    matieres_dict[matiere_key]["seances"]=seances_prime
                
                context={'etudiants':etudiants,
                         'semestre':semestre_id,
                         'ues':ues,
                         'matieres' : matieres,
                         'listeEtudiant':listeEtudiant,
                         'listeMatiere':listeMatiere,
                         'listeAbsence':listeAbsence,
                         'commentaires':commentaires,
                         'listeUe':listeUe,
                         'listeEtudiant':listeEtudiant,
                         'seances':matieres_dict,
                         'sousCategorisation':sousCategorisation
                        }        
                latex_input = 'cahier_de_texte'
                latex_ouput = 'CDT_'+str(semestre_id)+'_'+str(datetime.datetime.now())
                pdf_file = 'CDT_'+str(semestre_id)+'_'+str(datetime.datetime.now())

                # génération du pdf
                generate_pdf(context, latex_input, latex_ouput, pdf_file)
                pdf_paths.append('media/pdf/' + pdf_file)

    pdf_paths = [pdf_path + '.pdf' for pdf_path in pdf_paths]
    merged_pdf_content = b''.join([open(pdf_path, 'rb').read() for pdf_path in pdf_paths])

    response = HttpResponse(merged_pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=merged_pdfs.pdf'
    return response
        
                







@login_required(login_url="/main/connexion")
def commenter(request):
    commentaire = request.POST.get("commentaire")
    idv=request.POST.get("seance_id")
    seance = get_object_or_404(Seance, id=idv)
    seance.commentaire=commentaire
    seance.save()
    return redirect("/cahier_de_texte/info_seance/" + str(seance.id) + "/" )


fake = Faker()
def creer_etudiant(nombre):
    for _ in range(nombre):
        etu=creer_fake_etudiant()
        print(etu)


def creer_fake_etudiant():
    etudiant = Etudiant.objects.create(
        nom=fake.name(),
        prenom=fake.first_name(),
        sexe="M",
        datenaissance=fake.date_of_birth(),
        adresse=fake.address(),
        email=fake.email(),
        contact=fake.phone_number(),
        
        
    )
    semestre1 = Semestre.objects.filter(id='S1-2023' ).first()
    semestre2 = Semestre.objects.filter(id='S3-2023' ).first()
    semestres = [random.choice([semestre1,semestre2])]
    etudiant.semestres.set(semestres)
    return etudiant

def creer_seance(nombre):
    semestre1 = Semestre.objects.filter(id='S1-2023' ).first()
    semestre2 = Semestre.objects.filter(id='S3-2023' ).first()
    
    for _ in range(nombre):
        print(_)
        semestre=random.choice([semestre1,semestre2])
        ues = semestre.get_all_ues()
        print(ues)
        matieres=list()
        for ue in ues:
            matt = ue.matiere_set.all()
            for ma in matt:
                matieres.append(ma)
        taille=len(matieres)
        mat=random.randint(0,taille)
        matiere=matieres[mat-1]
        fake=create_fake_seance(semestre, matiere)
        print(fake)

def create_fake_seance(seme, matieres):
    
    print(matieres)
    
    intitule = fake.sentence()
    date_et_heure_debut = fake.date_time_this_year()
    date_et_heure_fin = date_et_heure_debut + datetime.timedelta(hours=2)
    description = fake.paragraph()
    auteur = Etudiant.objects.order_by('?').first()  # Get a random Etudiant
    valider = fake.boolean()
    matiere =matieres  
    semestre = seme  # Get a random Semestre
    enseignant = matiere.enseignant  # Get a random Enseignant
    commentaire = fake.paragraph()
    seance_plannifier = SeancePlannifier.objects.order_by('?').first()  # Get a random SeancePlannifier

    absents=[Etudiant.objects.order_by('?').first(),Etudiant.objects.order_by('?').first(),Etudiant.objects.order_by('?').first()]

    seance_instance = Seance.objects.create(
        intitule=intitule,
        date_et_heure_debut=date_et_heure_debut,
        date_et_heure_fin=date_et_heure_fin,
        description=description,
        auteur=auteur,
        valider=valider,
        matiere=matiere,
        semestre=semestre,
        enseignant=enseignant,
        commentaire=commentaire,
        seancePlannifier=seance_plannifier
    )
    print("les absents",absents[0])
    for student in absents:
        if len(student.nom) <= 12:
            seance_instance.eleves_presents.add(student)

    return seance_instance

def creer_prof(nombre):
        for _ in range(nombre):
            enseignant = Enseignant(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                sexe=random.choice(['F', 'M']),
                datenaissance=fake.date_of_birth(minimum_age=25, maximum_age=60),
                lieunaissance=fake.city(),
                contact=fake.phone_number(),
                email=fake.email(),
                adresse=fake.address(),
                numero_cnss='testtou1234',
                prefecture=fake.city(),
                carte_identity=fake.random_number(digits=10),
                nationalite='Togolaise',
                salaireBrut=random.uniform(1000, 5000),
                dernierdiplome=None,
                nbreJrsCongesRestant=random.randint(0, 30),
                nbreJrsConsomme=random.randint(0, 30),
                specialite=fake.job(),
            )
            enseignant.save()
            print(f"Enseignant créé : {enseignant}")