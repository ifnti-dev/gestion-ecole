from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('affecter_matieres_prof', views.affectation_matieres_professeur,
         name='affectation_matieres_professeur'),
    path('liste_matieres_professeur', views.liste_matieres_professeur,
         name='liste_matieres_professeur'),
    path('retirer_professeur/<int:id>',
         views.retirer_professeur, name='retirer_professeur'),
    path('modifier_coefficient/<int:matiere_id>/<int:coefficient>/',
         views.modifier_coefficient, name='modifier_coefficient'),

    path('affecter_ues_prof', views.affectation_ues_professeur,
         name='affectation_ues_professeur'),
    path('liste_ues_professeur', views.liste_ues_professeur,
         name='liste_ues_professeur'),
    path('retirer_professeur_ue/<int:id>',
         views.retirer_professeur_ue, name='retirer_professeur_ue'),


    path('connexion', views.login_view, name='connexion'),
    path('profil', views.profil, name='profil'),
    path('change_role/<int:id_role>', views.change_role, name='change_role'),
    path('edit_profil', views.edit_profil, name='edit_profil'),
    path('changer_mdp', views.changer_mdp, name='changer_mdp'),
    path('boite_a_suggestion', views.boite_a_suggestion, name='boite_a_suggestion'),
    path('reminder', views.recuperation_mdp, name='reminder'),
    path('deconnexion', views.logout_view, name='deconnexion'),


    # touré-ydaou urls templates latex 30-04-2023
#     path('etudiants_l/<int:niveau>/',
#          views.etudiants_par_niveau, name='etudiants_ln'),
    path('carte-etudiant/<str:id>/<str:niveau>',
         views.carte_etudiant, name='carte_etudiant'),
    path('diplome/<str:id>', views.diplome_etudiant, name='diplome_etudiant'),
    path('certificat_scolaire/<str:id>/<str:niveau>',
         views.certificat_scolaire, name='certificat_scolaire'),
    path('releve_notes/<str:id>/<str:id_semestre>',
         views.releve_notes, name='releve_notes'),
    path('releve_note_detail/<str:id>/<str:id_semestre>',
         views.releve_notes_detail, name="releve_notes_detail"),
    path('releve_note_detail/<str:id_semestre>',
         views.releve_notes_details_all, name="releve_notes_detail"),

    # urls permettant de générer les documents de manière groupée (pour un ensemble d'étudiants)
    path('releve_notes/<str:id_semestre>',
         views.releve_notes_semestre, name='releve_notes'),
    path('carte-etudiant/<str:niveau>',
         views.carte_etudiant_all, name='carte_etudiant'),
    path('diplomes', views.diplome_etudiant_all, name='diplome_etudiant'),
    path('recapitulatif-notes-matières/<str:id_matiere>/<str:id_semestre>',
         views.recapitulatif_notes, name='recap_notes'),



    # Abdoul-Malik urls 
     path('recapitulatifs_des_notes_par_etudiant/<str:id_semestre>/',
          views.recapitulatifs_des_notes_par_etudiant, name='recapitulatifs_des_notes_par_etudiant'),
     path('recapitulatifs_des_notes_par_matiere/<str:id_semestre>/<int:id_matiere>/',
          views.recapitulatifs_des_notes_par_matiere, name='recapitulatifs_des_notes_par_matiere'),
     path('evaluations/<int:id_matiere>/', views.evaluations, name='evaluations'),
     path('evaluations/delete/<int:id>/', views.deleteEvaluation, name='delete_evaluation'),
     path('evaluations/upload/<int:id_matiere>/<str:id_semestre>/', views.uploadEvaluation, name='upload_evaluations'),
     path('add_evaluation/<int:id_matiere>/<int:rattrapage>/<str:id_semestre>/',
          views.createNotesByEvaluation, name='add_evaluation'),
     path('edit_evaluation/<int:id>/',
          views.editeNoteByEvaluation, name='edit_evaluation'),
     path('evaluations_etudiant/<int:id_matiere>/<str:id_etudiant>/',
          views.evaluations_etudiant, name='evaluations_etudiant'),

     path('etudiants/',views.etudiants, name='etudiants'),

     #### Étudiants ####
     path('change_annee_universitaire/', views.change_annee_universitaire,name='change_annee_universitaire'),
     path('liste_des_etudiants/<int:id_annee_selectionnee>/',views.etudiants, name='liste_des_etudiants'),
     path('liste_des_etudiants_suspendu/', views.etudiants_suspendu,name='liste_des_etudiants_suspendu'),
     path('detail_etudiant/<str:id>/',views.detailEtudiant, name='detail_etudiant'),
     path('create_etudiant/', views.create_etudiant, name='create_etudiant'),
     path('importer_les_donnees/', views.importer_data,name='importer_les_donnees'),
     path('update_etudiant/<str:id>/',views.create_etudiant, name='update_etudiant'),

     #### Tuteurs ####
     path('liste_des_tuteurs/', views.tuteurs, name='liste_des_tuteurs'),
     path('detail_tuteur/<int:id>/', views.detailTuteur, name='detail_tuteur'),
     path('create_tuteur/', views.create_tuteur, name='create_tuteur'),
     path('update_tuteur/<int:id>/', views.create_tuteur, name='update_tuteur'),



     #### Matières ####
     path('matieres_etudiant/',views.matieres, name='matieres_etudiant'),

     # path('liste_des_matieres/', views.matieres, name='liste_des_matieres'),
     path('detail_matiere/<int:id>/', views.detailMatiere, name='detail_matiere'),
     path('create_matiere/', views.create_matiere, name='create_matiere'),
     path('update_matiere/<int:id>/', views.create_matiere, name='update_matiere'),
     path('delete_matiere/<int:id_matiere>/', views.delete_matiere, name='delete_matiere'),


     #### UEs ####
     path('ues/', views.ues_etudiants, name='ues'),
     path('liste_des_ues/', views.ues, name='liste_des_ues'),
     path('detail_ue/<int:id>/', views.detailUe, name='detail_ue'),
     path('create_ue/', views.create_ue, name='create_ue'),
     path('update_ue/<int:id>/', views.create_ue, name='update_ue'),


                    #### Enseignant ####
     path('enseignants/',views.enseignants, name='enseignants'),
     path('create_enseignant/', views.create_enseignant, name='create_enseignant'),
     path('enseignant_suspendu/', views.enseignant_inactif,name='enseignant_suspendu'),
     path('enseignant_detail/<str:id>/',views.enseignant_detail, name='enseignant_detail'),
     path('edit_enseignant/<str:id>/',views.create_enseignant, name='edit_enseignant'),
     path('certificat_travail/(?P<id>[0-9]+)\\Z/',views.certificat_travail, name='certificat_travail'),
     path('importer_les_enseignants/', views.importer_les_enseignants,name='importer_les_enseignants'),

     ### Information ###
     path('liste_informations_enseignants/', views.liste_informations_enseignants, name='liste_informations_enseignants'),
     path('enregistrer_informations/', views.enregistrer_informations,name='enregistrer_informations'),
     path('edit_information/(?P<id>[0-9]+)\\Z/',views.enregistrer_informations, name='edit_information'),




     # Malia clôture des semestres
     path('semestres/', views.semestres, name='semestres'),
     path('cloturer_semestre/<str:semestre_id>/',
          views.cloturer_semestre, name='cloturer_semestre'),
     path('reactiver_semestre/<str:semestre_id>/',
          views.reactiver_semestre, name='reactiver_semestre'),


     # Historique des semestres :
     path('semestre/<str:semestre_id>/historique/',
          views.historique_semestre, name='historique_semestre'),



     # Liste des étudiants par semestres

     path('liste_etudiants_par_semestre/<int:id_annee_selectionnee>/',
          views.liste_etudiants_par_semestre, name='liste_etudiants_par_semestre'),

     path('passage_etudiants/', views.passage_etudiants, name='passage_etudiants'),


     #Table de paramètre globale


]
