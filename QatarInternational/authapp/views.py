from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from myapp.models import Users  # Update this path based on your project


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == "GET":
        return render(request, "login.html")

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            user = Users.objects.filter(email=email, password=password, is_active=True).first()

            if user:
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email or password'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


def logout_view(request):
    request.session.flush()
    return redirect('/auth/login/')
