from django.urls import path
from api.views.etudiant_api_views import create_etudiant, delete_etudiant, detail_etudiant,list_etudiant, update_etudiant
from api.views.matiere_api_views import list_matiere,create_matiere,update_matiere,delete_matiere,detail_matiere
from api.views import ue_api_views
from api.views.programme_api_views import get_programme


from api.views import personnel_api_views
from api.views import enseignant_api_views

urlpatterns = [
  
    path("etudiants/", list_etudiant),
    path("etudiant/create/", create_etudiant),
    path("etudiant/update/<int:pk>/", update_etudiant),
    path("etudiant/delete/<int:pk>/", delete_etudiant),
    path("etudiant/detail/<int:pk>/", detail_etudiant),



    ############### Personnels urls###################################
    path("personnels",personnel_api_views.list_personnel),
    path("personnel/create",personnel_api_views.create_personnel),
    path("personnel/delete/<int:pk>",personnel_api_views.delete_personnel),
    path("personnel/update/<int:pk>",personnel_api_views.update_personnel),
    path("personnel/detail/<int:pk>",personnel_api_views.detail_personnel),
    path("personnel/form__demander_conge",personnel_api_views.form_demander_conge),
    path("personnel/imprimer_demande_conge",personnel_api_views.imprimer_demande_conge),
    path("personnel/accorder_conge",personnel_api_views.accorder_conge),

    ########################## Enseignant api  urls######################################

    path("enseignants",enseignant_api_views.list_enseignant),
    path("enseignant/create",enseignant_api_views.create_enseignant),
    path("enseignant/update/<int:pk>",enseignant_api_views.update_enseignant),
    path("enseignant/delete/<int:pk>",enseignant_api_views.delete_enseignant),
    path("enseignant/detail/<int:pk>",enseignant_api_views.detail_enseignant),
    path("enseignant/list_informations_enseignants",enseignant_api_views.list_informations_enseignants),
    
    path("enseignant/detail/<int:pk>",enseignant_api_views.detail_enseignant),
    path("enseignant/detail/<int:pk>",enseignant_api_views.detail_enseignant),
    path("enseignant/detail/<int:pk>",enseignant_api_views.detail_enseignant),

    #-----api des ues------------
    path("ues/", ue_api_views.list_ue),
    path("ue/create", ue_api_views.create_ue),
    path("ue/update/<int:pk>", ue_api_views.update_ue),
    path("ue/deltail/<int:pk>", ue_api_views.detail_ue),
    path("ue/delete/<int:pk>", ue_api_views.delete_ue),
    #-----api des matieres------------
    path("matieres/", list_matiere),
    path("matiere/create/<int:id>/", create_matiere),
    path("matiere/update/<int:id>/", update_matiere),
    path("matiere/delete/<int:id>/", delete_matiere),
    path("matiere/detail/<int:id>/", detail_matiere),
    #-----api des programme------------
    path("programmes/", get_programme)

]