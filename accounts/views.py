from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import UserProfile


@login_required
def debug_user_view(request):
    """Debug view to show user information"""
    user_data = {
        'user': request.user,
        'profile': getattr(request.user, 'profile', None),
        'is_authenticated': request.user.is_authenticated,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'groups': request.user.groups.all(),
        'permissions': request.user.user_permissions.all(),
    }
    
    return render(request, 'accounts/debug_user.html', {
        'user_data': user_data
    })


@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'accounts/profile.html', {
        'profile': profile
    })


def api_user_info(request):
    """API endpoint for user information"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    profile = getattr(request.user, 'profile', None)
    
    data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'full_name': request.user.get_full_name(),
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'profile': {
            'role': profile.get_role_display() if profile else None,
            'department': profile.department if profile else None,
            'phone': profile.phone if profile else None,
            'permissions': {
                'is_admin': profile.is_admin if profile else False,
                'is_manager': profile.is_manager if profile else False,
                'can_view_reports': profile.can_view_reports if profile else False,
                'can_manage_users': profile.can_manage_users if profile else False,
                'can_delete_records': profile.can_delete_records if profile else False,
            }
        } if profile else None
    }
    
    return JsonResponse(data)


# Helper functions for other apps
def is_admin(user):
    """Check if user is admin"""
    return hasattr(user, 'profile') and user.profile.is_admin


def is_manager(user):
    """Check if user is manager or admin"""
    return hasattr(user, 'profile') and user.profile.is_manager


def can_delete(user):
    """Check if user can delete records"""
    return hasattr(user, 'profile') and (user.profile.is_admin or user.profile.can_delete_records)


def can_manage_users(user):
    """Check if user can manage other users"""
    return hasattr(user, 'profile') and (user.profile.is_admin or user.profile.can_manage_users)


def can_view_reports(user):
    """Check if user can view reports"""
    return hasattr(user, 'profile') and (user.profile.is_admin or user.profile.can_view_reports)