from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views import ue_api_views
from api.views import personnel_api_views

urlpatterns = [
    path("etudiant/", etudiant_list),


    ############### Personnels urls###################################
    path("personnels",personnel_api_views.list_personnel),
    path("personnel/create",personnel_api_views.create_personnel),
    path("personnel/delete/<int:pk>",personnel_api_views.delete_personnel),
    path("personnel/update/<int:pk>",personnel_api_views.update_personnel),
    path("personnel/detail/<int:pk>",personnel_api_views.detail_personnel),
    path("personnel/form__demander_conge",personnel_api_views.form_demander_conge),
    path("personnel/imprimer_demande_conge",personnel_api_views.imprimer_demande_conge),
    path("personnel/accorder_conge",personnel_api_views.accorder_conge),

    #-----api des ues------------
    path("ues/", ue_api_views.list_ue),
    path("ue/create", ue_api_views.create_ue),
    path("ue/update/<int:pk>", ue_api_views.update_ue),
    path("ue/deltail/<int:pk>", ue_api_views.detail_ue),
    path("ue/delete/<int:pk>", ue_api_views.delete_ue),
]