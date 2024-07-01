from django.urls import path
from api.views.etudiant_api_views import etudiant_list
from api.views import ue_api_views



urlpatterns = [
    path("etudiant/", etudiant_list),

    #-----api des ues------------
    path("ues/", ue_api_views.list_ue),
    path("ue/create", ue_api_views.create_ue),
    path("ue/update/<int:pk>", ue_api_views.update_ue),
    path("ue/deltail/<int:pk>", ue_api_views.detail_ue),
    path("ue/delete/<int:pk>", ue_api_views.delete_ue),
]