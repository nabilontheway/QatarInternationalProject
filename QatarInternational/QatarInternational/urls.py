"""
URL configuration for QatarInternational project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp.views import dashboard_view, landing_view, addnotice,allnotice,add_notice_ajax,delete_notice,get_all_notices_json   # Import the landing view from myapp.views
from authapp.views import login_view



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # path('login/', login_view, name='login'),
    path('auth/', include('authapp.urls')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('',landing_view, name='landing'), # Add this line to include the landing page view
    path('add_notice',addnotice, name='add_notice'),
    path('all_notice',allnotice, name='all_notice'),
    path('add-notice-json/',add_notice_ajax, name='add_notice_json'),
    path('delete-notice/<int:id>/', delete_notice, name='delete_notice'),
    path('get-notices-json/', get_all_notices_json, name='get_notices'),


]
