from django.shortcuts import render

# Create your views here.



def dashboard_view(request):
    user_id = request.session.get('user_id')  # Get user_id from session
    if user_id:  # Check if session is present
        return render(request, 'dashboard.html', {'user_id': user_id})  # Pass user_id to dashboard
    else:
        return render(request, 'login.html')  # Return login

def landing_view(request):
    return render(request, 'landing.html')  # Return landing page


def addnotice(request):
    if request.method == 'POST':
        notice = request.POST.get('notice')
        # Here you would typically save the notice to the database
        return render(request, 'add_notice.html', {'notice': notice})
    return render(request, 'add_notice.html')  # Return add notice page

def allnotice(request):
    return render(request, 'all_notice.html')  # Return all notices page