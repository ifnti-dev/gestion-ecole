from django.urls import path
from api.views.etudiant_api_views import etudiant_list


from api.views.personnel_api_views import *
urlpatterns = [
    path("etudiant/", etudiant_list),

    ############### Personnels urls###################################
    path("personnels/",list_personnel),
    path("personnel/create/",create_personnel),
    path("personnel/delete/<int:pk>/",delete_personnel),
    path("personnel/update/<int:pk>/",update_personnel),
]