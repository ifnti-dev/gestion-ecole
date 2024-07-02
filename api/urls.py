from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views.matiere_api_views import list_matiere,create_matiere,update_matiere,delete_matiere,detail_matiere
from api.views import ue_api_views
from api.views.programme_api_views import get_programme



urlpatterns = [
    path("etudiant/", etudiant_list),

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