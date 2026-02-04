from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Skip check for staff users or if profile is already complete
                if request.user.is_staff or request.user.profile.is_complete:
                    pass
                # Allow access if terms modal needs to be shown (assuming modal is on dashboard)
                elif request.user.profile.show_terms_modal and request.path == reverse('dashboard'):
                    pass
                else:
                    profile_url = reverse('profile')
                    logout_url = reverse('account_logout') 
                    # Allow access to profile page, logout, signin, dashboard, admin, and static/media files
                    if (request.path != profile_url and 
                        request.path != logout_url and 
                        not request.path.startswith('/dashboard/signin') and
                        not request.path.startswith('/maze/') and
                        not request.path.startswith('/static/') and 
                        not request.path.startswith('/media/') and 
                        not request.path.startswith('/account/') and 
                        not request.path.startswith('/two_factor/')):
                        return redirect('profile')
            except Exception:
                # Handle cases where user might not have a profile yet (though signals should prevent this)
                pass

        response = self.get_response(request)
        return response

class LoginEnforcementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Exempt Paths
            if (request.path.startswith('/dashboard/signin') or 
                request.path.startswith('/maze/') or 
                request.path.startswith('/static/') or 
                request.path.startswith('/media/') or 
                request.path.startswith('/accounts/') or
                request.path.startswith('/two_factor/') or
                request.path == '/'):
                pass
            else:
                return redirect('signin')
        
        response = self.get_response(request)
        return response
