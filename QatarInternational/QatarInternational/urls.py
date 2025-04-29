from django.contrib import admin
from django.urls import path, include
from myapp.views import (
    dashboard_view,
    landing_view,
    addnotice,
    allnotice,
    delete_notice,
    get_all_notices_json,
    upload_notice,  # If you are uploading to Google Drive
    student_view,
    profile_setting,
    add_student,
    upload_profile_picture,
    student_dashboard_view,
    all_students,
    get_all_students_json,
    add_payment,
    payments, 
    get_payment_history,
    delete_student,
    delete_payment,
    edit_student,
    delete_student,
    upload_p_p,
    get_all_images,
    delete_image,
    upload_image, 
    payment_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('auth/', include('authapp.urls')),

    # Main pages
    path('', landing_view, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('student_dashboard/', student_dashboard_view, name='student_dashboard'),  # Same as dashboard for now
     path('add_payment/', add_payment, name="add_payment"),
    # Notice management
    path('add_notice/', addnotice, name='add_notice'),  # Renders add_notice.html
    path('all_notice/', allnotice, name='all_notice'),  # Renders all_notice.html

    path('upload-notice/', upload_notice, name='upload_notice'),        # File upload to Drive
    path('delete-notice/<int:id>/', delete_notice, name='delete_notice'),
    path('get-notices-json/', get_all_notices_json, name='get_notices'),
    path('add_student/', add_student, name='add_student'),  # Renders add_student.html
    path('get_all_students_json/', get_all_students_json, name='get_students'),  # Renders all_students.html
    path('all_students/', all_students, name='all_students'),  # Renders all_students.html
    path('payment_history/', payments, name='payment_history'),  # Renders payment_history.html
    path('get_payment_history/<str:roll>/',get_payment_history, name='get_payment_history'),
    path('delete_payment/<int:payment_id>/',delete_payment, name='delete_payment'),  # Renders edit_student.html
    path('delete_student/<int:id>/',delete_student, name='delete_student'),
    path('edit_student/<int:id>/', edit_student, name='edit_student'),
    path('delete_student/<int:id>/', delete_student, name='delete_student'),
    path('upload_p_p/', upload_p_p, name='upload_profile_picture'),


    path('upload_image/', upload_image, name="upload_image"),
    path('get_all_images/', get_all_images, name="get_all_images"),
    path('delete_image/<int:id>/', delete_image, name="delete_image"),


    path('profile/', student_view, name='student_profile'),  # Profile page (same as dashboard for now)
    path('profile_setting',profile_setting, name='profile_setting'),  # Profile settings page (same as dashboard for now)
    path('upload-profile-picture/', upload_profile_picture, name='upload_profile_picture'),

    path('payment/', payment_view, name='payment'),  # Renders payment_history.html
]
