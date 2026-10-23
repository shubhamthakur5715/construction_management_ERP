from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import UserProfile

def get_role(user):
    if user.is_superuser or user.is_staff: return "Admin"
    try: return user.profile.role
    except UserProfile.DoesNotExist: return "Site Manager"

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated: return redirect("login")
            if get_role(request.user) not in allowed_roles: raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def visible_projects(user, queryset=None):
    from .models import Project
    qs = queryset if queryset is not None else Project.objects.all()
    role = get_role(user)
    if role == "Admin": return qs
    try:
        profile = user.profile
        assigned = profile.projects.all()
        if assigned.exists(): return qs.filter(pk__in=assigned.values("pk"))
    except UserProfile.DoesNotExist: pass
    return qs.none()
