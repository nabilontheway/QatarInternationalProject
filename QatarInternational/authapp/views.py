from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from myapp.models import Users
from django.db import models



@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.session.get('user_id'):
        role = request.session.get('role')
        if role == 'student':
            return redirect('/student_dashboard/')
        else:
            return redirect('/dashboard/')

    if request.method == "GET":
        return render(request, "login.html")

    elif request.method == "POST":
        identifier = request.POST.get("email")  # Email or Student ID
        password = request.POST.get("password")

        # Find user by email or student_id
        user = Users.objects.filter(
            is_active=True
        ).filter(
            models.Q(email=identifier) | models.Q(student_id=identifier),
            password=password
        ).first()

        if user:
            # Set session
            request.session['user_id'] = user.id
            request.session['role'] = user.role

            # ✅ If request is AJAX (from fetch or JS), return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "role": user.role
                })

            # ✅ Otherwise fallback (normal POST form submit)
            if user.role == 'student':
                return redirect('/student_dashboard/')
            else:
                return redirect('/dashboard/')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Invalid email or student ID or password."
                })
            else:
                return render(request, "login.html", {
                    "error": "Invalid email/student ID or password."
                })
def logout_view(request):
    request.session.flush()
    return redirect('/auth/login/')
