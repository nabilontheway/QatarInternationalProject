from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Notice
import os
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Dashboard view
def dashboard_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'dashboard.html', {'user_id': user_id})
    return render(request, 'login.html')


# Landing page with latest notice
def landing_view(request):
    latest_notice = Notice.objects.order_by('-created_at').first()
    return render(request, 'landing.html', {'notice': latest_notice})


# Show the Add Notice form page
def addnotice(request):
    return render(request, 'add_notice.html')


# Save new notice via AJAX (file upload + Google Drive)
@csrf_exempt
def upload_notice(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        pdf_file = request.FILES.get("pdf_file")

        if not (title and description and pdf_file):
            return JsonResponse({"message": "All fields are required."}, status=400)

        # Save the uploaded file temporarily
        temp_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
        with open(temp_path, "wb+") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        # Upload the file to Google Drive
        try:
            drive_link = upload_pdf_to_drive(pdf_file, temp_path)

            # Save to DB
            Notice.objects.create(title=title, description=description, url=drive_link)

            # Clean up
            os.remove(temp_path)

            return JsonResponse({"message": "Notice uploaded successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"message": f"Upload failed: {str(e)}"}, status=500)

    return JsonResponse({"message": "Only POST allowed"}, status=405)


# Separate function to upload PDF to Google Drive
def upload_pdf_to_drive(pdf_file, temp_path):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')

    # Authenticate and initialize the Drive service
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    # Upload to a specific folder in Drive
    file_metadata = {
        'name': pdf_file.name,
        'parents': ['1_HZ3ilkSX10iU_TyZlDhLA7Ip5f4ArM0'],  # Folder ID
    }
    media = MediaFileUpload(temp_path, mimetype='application/pdf')
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Make file public
    service.permissions().create(
        fileId=uploaded['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    drive_link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"
    return drive_link


# Get all notices as JSON (for AJAX table)
def get_all_notices_json(request):
    if request.method == "GET":
        notices = Notice.objects.all().order_by('-id')
        data = [
            {
                "id": n.id,
                "sl": i + 1,
                "title": n.title,
                "url": n.url,
                "description": n.description,
                "date": n.created_at.strftime('%Y-%m-%d') if n.created_at else "",
            }
            for i, n in enumerate(notices)
        ]
        return JsonResponse({"notices": data}, status=200)
    return JsonResponse({"error": "Only GET method allowed."}, status=405)


# Delete a notice
@csrf_exempt
def delete_notice(request, id):
    if request.method == "DELETE":
        try:
            notice = Notice.objects.get(id=id)
            notice.delete()
            return JsonResponse({"message": "Notice deleted successfully."}, status=200)
        except Notice.DoesNotExist:
            return JsonResponse({"message": "Notice not found."}, status=404)

    return JsonResponse({"message": "Only DELETE method allowed."}, status=405)


# Show all notices HTML page
def allnotice(request):
    return render(request, 'all_notice.html')




# student 
def student_view(request):
     return render(request, 'student_profile.html')


# Profile settings page (same as dashboard for now)
def profile_setting(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'student_profile.html', {'user_id': user_id})
    return render(request, 'login.html')