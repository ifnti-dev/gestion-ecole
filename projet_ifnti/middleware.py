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
            print('OKay')
            print(current_annee_accademique)
            id_annee_selectionnee = current_annee_accademique.id if current_annee_accademique else 0
            request.session["id_annee_selectionnee"] = id_annee_selectionnee
        path = request.path
        print(path)
        allowed_paths = ['/admin/', '/main/connexion', '/main/deconnexion', '/__reload__/events/']
        return
        for allowed_path in allowed_paths:
            if allowed_path in path:
                return
        
        auth_user_role = get_user_role(request)
        
        role_name = ""
        if not auth_user_role:
            return redirect('main:connexion')
        
        role_name = auth_user_role.name
        if role_name == "etudiant":
            etudiant = request.user.etudiant
            if not etudiant.semestres.all():
                return redirect('main:connexion')
        return