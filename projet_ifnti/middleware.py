from main.helpers import get_user_role
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from main.models import AnneeUniversitaire
from datetime import datetime

class AuthUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_annee_accademique = AnneeUniversitaire.static_get_current_annee_universitaire()
        
        try:
            AnneeUniversitaire.objects.get(id=request.session.get('id_annee_selectionnee'))
        except:
            print(current_annee_accademique)
            id_annee_selectionnee = current_annee_accademique.id
            request.session["id_annee_selectionnee"] = current_annee_accademique.id
            
        path = request.path
        allowed_paths = ['/admin/', '/main/connexion', '/main/deconnexion', '/__reload__/events/']
        return