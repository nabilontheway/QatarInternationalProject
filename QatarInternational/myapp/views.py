from django.shortcuts import render

# Create your views here.



def dashboard_view(request):
    user_id = request.session.get('user_id')  # Get user_id from session
    if user_id:  # Check if session is present
        return render(request, 'dashboard.html', {'user_id': user_id})  # Pass user_id to dashboard
    else:
        return render(request, 'login.html')  # Return login
