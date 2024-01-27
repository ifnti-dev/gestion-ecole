from main.helpers import get_user_role
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404, redirect
from main.models import AnneeUniversitaire
# from django.core.cache import cache

class AuthUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "id_annee_selectionnee" not in request.session:
            current_annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
            request.session['id_annee_selectionnee'] = current_annee_universitaire.id
            
        return