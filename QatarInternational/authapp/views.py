from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from myapp.models import Users
from django.db import models




@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == "GET":
        return render(request, "login.html")

    elif request.method == "POST":
        identifier = request.POST.get("email")  # can be email or student ID
        password = request.POST.get("password")

        # Try to match by email or student_id
        user = Users.objects.filter(
            is_active=True,
        ).filter(
            (models.Q(email=identifier) | models.Q(student_id=identifier)),
            password=password
        ).first()

        if user:
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            return redirect('/dashboard/')
        else:
            return render(request, "login.html", {
                "error": "Invalid email/student ID or password"
            })


def logout_view(request):
    request.session.flush()
    return redirect('/auth/login/')
