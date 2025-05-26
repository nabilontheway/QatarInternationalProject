from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseRedirect
import os
import json
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import destroy
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.shortcuts import redirect

from .models import Notice, Users, Student, PaymentHistory,GalleryPic

# Cloudinary config
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# --- VIEWS START ---

# Dashboard
def dashboard_view(request):
    user_id = request.session.get('user_id')
    if user_id and request.session.get('role') == 'admin':
        return render(request, 'dashboard.html', {'user_id': user_id, 'page_title': 'Dashboard'})
    elif user_id and request.session.get('role') == 'student':
        return redirect('/student_dashboard/')    
    return render(request, 'login.html')

def student_dashboard_view(request):
    user_id = request.session.get('user_id')
    if user_id and request.session.get('role') == 'admin':
        return render(request, 'dashboard.html', {'user_id': user_id, 'page_title': 'Dashboard'})
    elif user_id and request.session.get('role') == 'student':
        return redirect('/student_dashboard/')
    return render(request, 'login.html')

# Landing
def landing_view(request):
    user_id = request.session.get('user_id')
    if user_id and request.session.get('role') == 'admin':
        return render(request, 'dashboard.html', {'user_id': user_id, 'page_title': 'Dashboard'})
    elif user_id and request.session.get('role') == 'student':
        return redirect('/student_dashboard/')
    latest_notice = Notice.objects.order_by('-created_at').first()
    return render(request, 'landing.html', {'notice': latest_notice})

def payment_view(request):
    user_id = request.session.get('user_id')
    if user_id and request.session.get('role') == 'admin':
        return render(request, 'dashboard.html', {'user_id': user_id, 'page_title': 'Dashboard'})
    elif user_id and request.session.get('role') == 'student':
        return redirect('/student_dashboard/')
    latest_notice = Notice.objects.order_by('-created_at').first()
    return render(request, 'payment.html', {'notice': latest_notice, 'page_title': 'Payment'})


# Add Notice Form
def addnotice(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in to add a notice.'})

    user = Users.objects.filter(id=user_id).first()
    if user and user.role == "admin":
        return render(request, 'add_notice.html', {'page_title': 'Add Notice'})

    return render(request, 'login.html', {'message': 'Unauthorized access. Admins only.'})

# Upload Notice (PDF upload to Drive)
@csrf_exempt
def upload_notice(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        pdf_file = request.FILES.get("pdf_file")

        if not (title and description and pdf_file):
            return JsonResponse({"message": "All fields are required."}, status=400)

        temp_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
        with open(temp_path, "wb+") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        try:
            drive_link = upload_pdf_to_drive(pdf_file, temp_path)
            Notice.objects.create(title=title, description=description, url=drive_link)
            os.remove(temp_path)
            return JsonResponse({"message": "Notice uploaded successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"message": f"Upload failed: {str(e)}"}, status=500)

    return JsonResponse({"message": "Only POST allowed"}, status=405)

def upload_pdf_to_drive(pdf_file, temp_path):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': pdf_file.name,
        'parents': ['1_HZ3ilkSX10iU_TyZlDhLA7Ip5f4ArM0'],
    }
    media = MediaFileUpload(temp_path, mimetype='application/pdf')
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    service.permissions().create(
        fileId=uploaded['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    drive_link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"
    return drive_link

# All notices
def allnotice(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in to view notices.'})

    user = Users.objects.filter(id=user_id).first()
    if user and user.role == "admin":
        return render(request, 'all_notice.html', {'page_title': 'All Notices'})

    return render(request, 'login.html', {'message': 'Unauthorized access. Admins only.'})

def get_all_notices_json(request):
    if request.method == "GET":
        notices = Notice.objects.all().order_by('-id')
        data = [{
            "id": n.id,
            "sl": i + 1,
            "title": n.title,
            "url": n.url,
            "description": n.description,
            "date": n.created_at.strftime('%Y-%m-%d') if n.created_at else "",
        } for i, n in enumerate(notices)]
        return JsonResponse({"notices": data}, status=200)
    return JsonResponse({"error": "Only GET allowed"}, status=405)

@csrf_exempt
def delete_notice(request, id):
    if request.method == "DELETE":
        try:
            notice = Notice.objects.get(id=id)
            drive_file_id = notice.url.split("/d/")[-1].split("/")[0]  # Extract the file ID from the URL

            # Delete the file from Google Drive
            delete_file_from_drive(drive_file_id)

            # Now delete the notice from the database
            notice.delete()

            return JsonResponse({"message": "Notice and associated file deleted successfully."}, status=200)
        except Notice.DoesNotExist:
            return JsonResponse({"message": "Notice not found."}, status=404)
        except Exception as e:
            return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"message": "Only DELETE allowed."}, status=405)


def public_notice(request):
    latest_notice = Notice.objects.order_by('-created_at').first()
    return render(request, 'public_notice.html', {'notice': latest_notice, 'page_title': 'Public Notice'})

def public_gallery(request):
    latest_notice = Notice.objects.order_by('-created_at').first()
    return render(request, 'public_gallery.html', {'notice': latest_notice, 'page_title': 'Public Gallery'})


def delete_file_from_drive(file_id):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    try:
        service.files().delete(fileId=file_id).execute()  # Delete the file
    except Exception as e:
        raise Exception(f"Failed to delete file from Google Drive: {str(e)}")


@csrf_exempt
def add_payment(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)
    if request.method == "GET":
        return render(request, 'add_payment.html', {'page_title': 'Add Payment'})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            roll = data.get("roll")
            amount = data.get("amount")
            via = data.get("via")
            payment_date = data.get("payment_date")  # 🌟

            if not (roll and amount and via and payment_date):
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            student = Student.objects.filter(s_roll=roll).first()
            if not student:
                return JsonResponse({"success": False, "message": "Student not found."}, status=404)

            PaymentHistory.objects.create(
                user=student.s_user,
                amount=amount,
                via=via,
                date=payment_date
            )

            return JsonResponse({"success": True, "message": "Payment added successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid method."}, status=405)

# Student profile
def student_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in to view your profile.'})

    user = Users.objects.filter(id=user_id).first()
    if user and user.role == "student":
        return render(request, 'student_profile.html', {'page_title': 'Student Profile'})

    return render(request, 'login.html', {'message': 'Unauthorized access. Students only.'})

@csrf_exempt
def edit_student(request, id):
    if request.method == "GET":
        try:
            student = Student.objects.get(id=id)
            return render(request, 'edit_student.html', {"student": student, "page_title": "Edit Student"})
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            student = Student.objects.get(id=id)
            user = student.s_user  # ForeignKey to Users

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

            return JsonResponse({"message": "Student updated successfully!"}, status=200)

        except Exception as e:
            return JsonResponse({"message": f"Something went wrong: {str(e)}"}, status=500)

    return JsonResponse({"message": "Method not allowed"}, status=405)

@csrf_exempt
def upload_p_p(request):
    if request.method == "POST":
        try:
            student_id = request.POST.get('student_id')
            if not student_id:
                return JsonResponse({"message": "No student ID provided."}, status=400)

            file = request.FILES.get("profile_pic")
            if not file:
                return JsonResponse({"message": "No file uploaded."}, status=400)

            student = Student.objects.get(id=student_id)
            old_pp_url = student.pp_url

            if old_pp_url:
                public_id = old_pp_url.split("/")[-1].split(".")[0]
                destroy(public_id)  # Optional: remove old image from Cloudinary

            result = cloudinary.uploader.upload(file)
            secure_url = result.get('secure_url')

            student.pp_url = secure_url
            student.save()

            return JsonResponse({"success": True, "message": "Profile picture uploaded successfully.", "url": secure_url})

        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found."}, status=404)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=405)


@csrf_exempt
def profile_setting(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        try:
            student = Student.objects.get(s_user_id=user_id)
            return render(request, 'student_profile.html', {"student": student, "page_title": "Edit Profile"})
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

    elif request.method == "POST":
        try:
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
            return JsonResponse({"message": "Something went wrong: " + str(e)}, status=500)

    return JsonResponse({"message": "Method not allowed"}, status=405)

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

            student = Student.objects.get(s_user_id=user_id)
            old_pp_url = student.pp_url

            if old_pp_url:
                public_id = old_pp_url.split("/")[-1].split(".")[0]
                destroy(public_id)

            result = cloudinary.uploader.upload(file)
            secure_url = result.get('secure_url')

            student.pp_url = secure_url
            student.save()

            return JsonResponse({"message": "Profile picture uploaded.", "url": secure_url})

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=405)

@csrf_exempt
def add_student(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    user = Users.objects.filter(id=user_id).first()
    if not user or user.role != "admin":
        return JsonResponse({"message": "Forbidden: Admins only."}, status=403)

    if request.method == "GET":
        return render(request, 'add_student.html', {'page_title': 'Add Student'})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            s_roll = data.get("s_roll")
            s_class = data.get("s_class")
            password = data.get("password")

            if not all([s_roll, s_class, password]):
                return JsonResponse({"message": "All fields required"}, status=400)

            user = Users.objects.create(
                email=f"{s_roll}@example.com",
                username=f"student_{s_roll}",
                password=password,
                role="student",
                student_id=s_roll
            )

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

def all_students(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in to view all students.'})

    user = Users.objects.filter(id=user_id).first()
    if user and user.role == "admin":
        return render(request, 'all_students.html', {'page_title': 'All Students'})

    return render(request, 'login.html', {'message': 'Unauthorized access. Admins only.'})


def get_all_students_json(request):
    if request.method == "GET":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        user = Users.objects.filter(id=user_id).first()
        if not user or user.role != "admin":
            return JsonResponse({"error": "Forbidden: Admins only."}, status=403)

        student_id = request.GET.get('id', None)  # Get 'id' from query parameters
        
        if student_id:
            # Filter students by the provided ID
            students = Student.objects.filter(s_roll=student_id).order_by('-s_roll')
        else:
            # Return all students if no ID filter is provided
            students = Student.objects.all().order_by('-id')
        
        # Prepare the data to send back
        data = [{
            "id": s.id,
            "sl": i + 1,
            "s_name": s.s_name,
            "s_roll": s.s_roll,
            "s_class": s.s_class,
            "pp_url": s.pp_url  
        } for i, s in enumerate(students)]
        
        return JsonResponse({"students": data}, status=200)
    
    return JsonResponse({"error": "Only GET allowed"}, status=405)

@csrf_exempt
def delete_student(request, id):
    if request.method == "DELETE":
        try:
            student = Student.objects.get(id=id)
            user = student.s_user
            student.delete()
            user.delete()  # If you want to delete linked user too
            return JsonResponse({"success": True, "message": "Student deleted successfully."}, status=200)
        except Student.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student not found."}, status=404)
    return JsonResponse({"success": False, "message": "Only DELETE method allowed."}, status=405)


def payments(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in to view payment history.'})

    user = Users.objects.filter(id=user_id).first()
    if user and user.role == "admin":
        return render(request, 'payment_history.html', {'page_title': 'Payments'})

    return render(request, 'login.html', {'message': 'Unauthorized access. Admins only.'})

@csrf_exempt
def delete_payment(request, payment_id):
    if request.method == "DELETE":
        try:
            payment = PaymentHistory.objects.get(id=payment_id)
            payment.delete()
            return JsonResponse({"success": True})
        except PaymentHistory.DoesNotExist:
            return JsonResponse({"success": False, "message": "Payment not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid method."}, status=405)


@csrf_exempt
def get_payment_history(request, roll):
    if request.method == "GET":
        try:
            student = Student.objects.get(s_roll=roll)
            payments = PaymentHistory.objects.filter(user=student.s_user).order_by('-date')

            data = [{
                "id": p.id,
                "amount": p.amount,
                "via": p.via,
                "date": p.date.strftime("%Y-%m-%d")
            } for p in payments]

            return JsonResponse({"payments": data}, status=200)
        except Student.DoesNotExist:
            return JsonResponse({"payments": []}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only GET allowed."}, status=405)

@csrf_exempt
def upload_image(request):
    if request.method == "GET":
        return render(request, 'upload_image.html', {'page_title': 'Upload Image'})

    if request.method == "POST":
        try:
            image_file = request.FILES.get("image")
            if not image_file:
                return JsonResponse({"message": "No image provided."}, status=400)

            result = upload(image_file)
            url = result.get("secure_url")

            pic = GalleryPic(pic_url=url)
            pic.save()

            return JsonResponse({"message": "Image uploaded successfully.", "url": url})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=405)

def get_all_images(request):
    images = list(GalleryPic.objects.values("id", "pic_url"))
    return JsonResponse({"images": images})

@csrf_exempt
def delete_image(request, id):
    if request.method == "DELETE":
        try:
            pic = GalleryPic.objects.get(id=id)
            public_id = pic.pic_url.split("/")[-1].split(".")[0]
            destroy(public_id)
            pic.delete()
            return JsonResponse({"message": "Image deleted."})
        except GalleryPic.DoesNotExist:
            return JsonResponse({"message": "Image not found."}, status=404)
    return JsonResponse({"message": "Invalid request method."}, status=405)



 