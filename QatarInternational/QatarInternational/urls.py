from django.contrib import admin
from django.urls import path, include
from myapp.views import (
    dashboard_view,
    landing_view,
    addnotice,
    allnotice,
    # add_notice_ajax,
    delete_notice,
    get_all_notices_json,
    upload_notice,  # If you are uploading to Google Drive
    student_view,
    profile_setting,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('auth/', include('authapp.urls')),

    # Main pages
    path('', landing_view, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Notice management
    path('add_notice/', addnotice, name='add_notice'),  # Renders add_notice.html
    path('all_notice/', allnotice, name='all_notice'),  # Renders all_notice.html

    # AJAX and API
    # path('add-notice-json/', add_notice_ajax, name='add_notice_json'),  # JSON-based add
    path('upload-notice/', upload_notice, name='upload_notice'),        # File upload to Drive
    path('delete-notice/<int:id>/', delete_notice, name='delete_notice'),
    path('get-notices-json/', get_all_notices_json, name='get_notices'),

    path('profile/', student_view, name='student_profile'),  # Profile page (same as dashboard for now)
    path('profile_setting',profile_setting, name='profile_setting'),  # Profile settings page (same as dashboard for now)
]
