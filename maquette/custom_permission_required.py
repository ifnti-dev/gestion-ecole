from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from main.helpers import get_user_role

def data_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            role = get_user_role(request)
            if role:
                if role.name in ["directeur_des_etudes", "secretaire"]:
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden(render(request, 'errors_pages/403.html'))
        return _wrapped_view
    return decorator
