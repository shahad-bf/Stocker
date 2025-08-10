from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    """Simple dashboard view for testing"""
    
    context = {
        'message': 'Dashboard is working!',
        'user': request.user
    }
    
    return render(request, 'dashboard/dashboard_simple.html', context)
