from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views.matiere_api_views import list_matiere,create_matiere,update_matiere,delete_matiere,detail_matiere

urlpatterns = [
    path("etudiant/", etudiant_list),
    path("matieres/", list_matiere),
    path("matiere/create/<int:id>/", create_matiere),
    path("matiere/update/<int:id>/", update_matiere),
    path("matiere/delete/<int:id>/", delete_matiere),
    path("matiere/detail/<int:id>/", detail_matiere)
]