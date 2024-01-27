from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from main.helpers import get_user_role
from .models import Evaluation, Matiere
from django.contrib import messages

def verify_if_user_is_can_be_pass_to_evaluation_data(request, matiere):
    role = get_user_role(request)
    if role:
        if matiere.enseignant:
            principale_id = matiere.ue.enseignant.user.id if matiere.ue.enseignant else -1
            return (role.name in ["directeur_des_etudes", "secretaire"] or (role.name == "enseignant" and (request.user.id == matiere.enseignant.user.id or principale_id == request.user.id)))
        else:
            messages.error(request, f"La matière {matiere.libelle} n'a pas d'enseignant ! ")
    return False

def evaluation_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, id_matiere=None, id=None, *args, **kwargs):
            if id:
                matiere = get_object_or_404(Evaluation, pk=id).matiere
            else:
                matiere = get_object_or_404(Matiere, pk=id_matiere)
            if verify_if_user_is_can_be_pass_to_evaluation_data(request, matiere):
                if permission_name in ["main.view_evaluation", "main.add_evaluation"]:
                    return view_func(request, id_matiere, *args, **kwargs)
                else:
                    return view_func(request, id, *args, **kwargs)
                
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator

def evaluation_upload_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, id_matiere, id_semestre, *args, **kwargs):
            matiere = get_object_or_404(Matiere, pk=id_matiere)
            if verify_if_user_is_can_be_pass_to_evaluation_data(request, matiere):
                return view_func(request, id_matiere, id_semestre, *args, **kwargs)
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator


def show_recapitulatif_note_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, id_semestre, id_matiere, *args, **kwargs):
            matiere = get_object_or_404(Matiere, pk=id_matiere)
            if verify_if_user_is_can_be_pass_to_evaluation_data(request, matiere):
                return view_func(request, id_semestre, id_matiere, *args, **kwargs)
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator
