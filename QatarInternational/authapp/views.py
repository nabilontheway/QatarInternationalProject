from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from myapp.models import Users


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == "GET":
        return render(request, "login.html")

    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Users.objects.filter(email=email, password=password, is_active=True).first()

        if user:
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = user.role
            return redirect('/dashboard/')
        else:
            return render(request, "login.html", {
                "error": "Invalid email or password"
            })


def logout_view(request):
    request.session.flush()
    return redirect('/auth/login/')
