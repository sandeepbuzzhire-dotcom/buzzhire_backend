from django.http import HttpResponse

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "ADMIN":
            return HttpResponse("Access Denied")
        return view_func(request, *args, **kwargs)
    return wrapper
