from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views import ue_api_views
from api.views import personnel_api_views
from api.views import enseignant_api_views

urlpatterns = [
    path("etudiant/", etudiant_list),


    ############### Personnels urls###################################
    path("personnels",personnel_api_views.list_personnel),
    path("personnel/create",personnel_api_views.create_personnel),
    path("personnel/delete/<int:pk>",personnel_api_views.delete_personnel),
    path("personnel/update/<int:pk>",personnel_api_views.update_personnel),
    path("personnel/detail/<int:pk>",personnel_api_views.detail_personnel),
    path("personnel/formulaire_demande_conges",personnel_api_views.formulaire_demande_conges),
    path("personnel/imprimer_demande_conge",personnel_api_views.imprimer_demande_conge),
    path("personnel/accorder_conge",personnel_api_views.accorder_conge),

    ########################## Enseignant api  urls######################################

    path("enseignants",enseignant_api_views.list_enseignant),
    path("enseignant/create",enseignant_api_views.create_enseignant),
    path("enseignant/update/<int:pk>",enseignant_api_views.update_enseignant),
    path("enseignant/delete/<int:pk>",enseignant_api_views.delete_enseignant),
    path("enseignant/detail/<int:pk>",enseignant_api_views.detail_enseignant),


    path("enseignant/list_informations_enseignants",enseignant_api_views.list_informations_enseignants),
    path("enseignant/enregistrer_informations",enseignant_api_views.enregistrer_informations),
    # path("enseignant/get_semestres",enseignant_api_views.get_semestres),
    # path("enseignant/reactiver_semestre/<int:pk>",enseignant_api_views.reactiver_semestre),
   











    #-----api des ues------------
    path("ues/", ue_api_views.list_ue),
    path("ue/create", ue_api_views.create_ue),
    path("ue/update/<int:pk>", ue_api_views.update_ue),
    path("ue/deltail/<int:pk>", ue_api_views.detail_ue),
    path("ue/delete/<int:pk>", ue_api_views.delete_ue),
]