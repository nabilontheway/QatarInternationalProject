from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Notice  # Make sure to import your model


# Dashboard view
def dashboard_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'dashboard.html', {'user_id': user_id})
    else:
        return render(request, 'login.html')


# Landing page
def landing_view(request):
    return render(request, 'landing.html')


# Show add notice page
def addnotice(request):
    return render(request, 'add_notice.html')


# Handle AJAX-based notice submission
@csrf_exempt
def add_notice_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description")
            url = data.get("url")
            print(title)
            print(description) 
            print(url)
            if not (title and description):
                return JsonResponse({"message": "All fields are required."}, status=400)

            Notice.objects.create(title=title, description=description, url=url)

            return JsonResponse({"message": "Notice saved successfully!"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON."}, status=400)

    return JsonResponse({"message": "Only POST method is allowed."}, status=405)


def get_all_notices_json(request):
    if request.method == "GET":
        notices = Notice.objects.all().order_by('-id')  # latest first
        data = []
        for i, notice in enumerate(notices, 1):
            data.append({
                "id": notice.id,
                "sl": i,
                "title": notice.title,
                "description": notice.description,
                "date": notice.created_at.strftime('%Y-%m-%d') if notice.created_at else "",  # update if using custom field
            })
        return JsonResponse({"notices": data}, status=200)
    return JsonResponse({"error": "Only GET allowed"}, status=405)



@csrf_exempt
def delete_notice(request, id):
    if request.method == "DELETE":
        try:
            notice = Notice.objects.get(id=id)
            notice.delete()
            return JsonResponse({"message": "Notice deleted successfully."}, status=200)
        except Notice.DoesNotExist:
            return JsonResponse({"message": "Notice not found."}, status=404)
    return JsonResponse({"message": "Only DELETE allowed."}, status=405)

# Show all notices page (dummy, you can expand this later)
def allnotice(request):
    return render(request, 'all_notice.html')
