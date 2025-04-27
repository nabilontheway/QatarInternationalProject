from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Notice
import os
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
from .models import Users, Student
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import cloudinary
import cloudinary.uploader



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


# Student
def student_view(request):
    return render(request, 'student_profile.html')



@csrf_exempt
def profile_setting(request):
    if request.method == "GET":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"message": "Not logged in"}, status=401)

        try:
            student = Student.objects.get(s_user_id=user_id)
            return render(request, 'student_profile.html', {"student": student})
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

    if request.method == "POST":
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({"message": "Not logged in"}, status=401)

            data = json.loads(request.body)

            student = Student.objects.get(s_user_id=user_id)
            user = Users.objects.get(id=user_id)

          
            if "s_name" in data:
                student.s_name = data["s_name"]
            if "present_address" in data:
                student.present_address = data["present_address"]
            if "permanent_address" in data:
                student.permanent_address = data["permanent_address"]
            if "father_name" in data:
                student.father_name = data["father_name"]
            if "father_number" in data:
                student.father_number = data["father_number"]
            if "mother_name" in data:
                student.mother_name = data["mother_name"]
            if "mother_number" in data:
                student.mother_number = data["mother_number"]

            if "password" in data and data["password"]:
                user.password = data["password"]
                user.save()

            student.save()

            return JsonResponse({"message": "Profile updated successfully!"}, status=200)

        except Exception as e:
            print("Error while updating profile:", e)
            return JsonResponse({"message": "Something went wrong"}, status=500)

    return JsonResponse({"message": "Method not allowed"}, status=405)



cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)

@csrf_exempt
def upload_profile_picture(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            file = request.FILES.get("profile_pic")
            if not file:
                return JsonResponse({"message": "No file uploaded."}, status=400)

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)

            # Save URL
            secure_url = result.get('secure_url')
            student = Student.objects.get(s_user__id=user_id)
            student.pp_url = secure_url
            student.save()

            return JsonResponse({"message": "Profile picture uploaded successfully.", "url": secure_url})

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=405)



@csrf_exempt
def add_student(request):
    if request.method == "GET":
        return render(request, 'add_student.html')

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            s_roll = data.get("s_roll")
            s_class = data.get("s_class")
            password = data.get("password")

            if not all([s_roll, s_class, password]):
                return JsonResponse({"message": "All fields (roll, class, password) are required."}, status=400)

            # First, create the User
            user = Users.objects.create(
                email=f"{s_roll}@example.com",  # You can change this later
                username=f"student_{s_roll}",
                password=password,              # (Note: Later use password hashing)
                role="student",
                student_id=s_roll
            )

            # Then, create the Student linked with the User
            Student.objects.create(
                s_user=user,
                s_name="Default Name",
                s_roll=s_roll,
                s_class=s_class,
                present_address="Default Present Address",
                permanent_address="Default Permanent Address",
                father_name="Default Father",
                father_number="0000000000",
                mother_name="Default Mother",
                mother_number="0000000000",
                pp_url="https://res.cloudinary.com/dee0zdpi9/image/upload/v1745640614/AdobeStock_1197779557_Preview_t7nhbj.jpg"
            )

            return JsonResponse({"message": "Student added successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"message": f"Failed to add student: {str(e)}"}, status=500)

    return JsonResponse({"message": "Only POST method allowed."}, status=405)
