from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from main.helpers import get_user_role
from .models import Matiere


def evaluation_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, id_matiere, *args, **kwargs):
            matiere = get_object_or_404(Matiere, pk=id_matiere)
            role = get_user_role(request)
            if role:
                if role.name in ["directeur_des_etudes", "secretaire"] or (role.name == "enseignant" and (request.user.id == matiere.enseignant.user.id or matiere.ue.enseignant.user.id == request.user.id)):
                    return view_func(request, id_matiere, *args, **kwargs)
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator


def show_recapitulatif_note_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, id_semestre, id_matiere, *args, **kwargs):
            role = get_user_role(request)
            if role:
                if role.name in ["directeur_des_etudes", "enseignant"]:
                    return view_func(request, id_semestre, id_matiere, *args, **kwargs)
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator
