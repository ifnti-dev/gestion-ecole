from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views import ue_api_views
from api.views.matiere_api_views import list_matiere,create_matiere,update_matiere,delete_matiere,detail_matiere


urlpatterns = [
    path("etudiant/", etudiant_list),

    path("ues/", ue_api_views.list_ue),
    path("ue/create", ue_api_views.create_ue),
    path("ue/update/<int:pk>", ue_api_views.update_ue),
    path("ue/deltail/<int:pk>", ue_api_views.detail_ue),
    path("ue/delete/<int:pk>", ue_api_views.delete_ue),
    path("etudiant/", etudiant_list),
    path("matieres/", list_matiere),
    path("matiere/create/<int:id>/", create_matiere),
    path("matiere/update/<int:id>/", update_matiere),
    path("matiere/delete/<int:id>/", delete_matiere),
    path("matiere/detail/<int:id>/", detail_matiere)
]